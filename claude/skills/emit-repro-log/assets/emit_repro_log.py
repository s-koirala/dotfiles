"""ReproLog emitter — self-contained port of SKIE-Universe reproducibility.py.

Source-of-truth: github.com/s-koirala/SKIE-Universe blob
src/skie_ninja/utils/reproducibility.py SHA-1 3f90d557bed13ccfd3e362077e5b40ae06ebd084
(gh api fetched 2026-05-15).

Self-contained — no project-internal imports. Inlines `file_sha256` and a
minimal `ProjectPaths` discovery (CLAUDE_PROJECT_DIR > pyproject.toml ancestor
search > cwd).

13-field contract:
    run_id, phase, hypothesis_id, timestamp_utc, git_head,
    pip_freeze_sha256, pip_freeze_path, dataset_checksums,
    rng_seed, model_hash, config_resolved_sha256, host, env_id.

CLI: `python emit_repro_log.py --selftest` exits 0 on round-trip success.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

# Subprocess timeout for `git rev-parse` / `uv pip freeze`. Tunable via env var.
_SUBPROCESS_TIMEOUT_SEC = int(os.environ.get("SKIE_SUBPROCESS_TIMEOUT_SEC", "30"))

# Project-root discovery markers, ordered by specificity.
_PROJECT_MARKERS = (
    "pyproject.toml", "uv.lock", "poetry.lock",
    "requirements.txt", "Pipfile.lock", ".git",
)


# --------------------------------------------------------------------------- #
# Inlined utilities (replacements for skie_ninja.utils.hashing / .paths)
# --------------------------------------------------------------------------- #

def file_sha256(path: Path, chunk: int = 65536) -> str:
    """Stream-based SHA-256 of a file's bytes. Empty string on read failure."""
    try:
        h = hashlib.sha256()
        with Path(path).open("rb") as f:
            for block in iter(lambda: f.read(chunk), b""):
                h.update(block)
        return h.hexdigest()
    except OSError:
        return ""


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    logs_reproducibility: Path
    logs_reproducibility_env: Path

    @staticmethod
    def discover(start: Path | None = None) -> ProjectPaths:
        """Find project root via CLAUDE_PROJECT_DIR or ancestor marker search."""
        env_root = os.environ.get("CLAUDE_PROJECT_DIR")
        if env_root:
            root = Path(env_root).resolve()
        else:
            cur = (start or Path.cwd()).resolve()
            root = cur
            for parent in [cur, *cur.parents]:
                if any((parent / m).exists() for m in _PROJECT_MARKERS):
                    root = parent
                    break
        return ProjectPaths(
            root=root,
            logs_reproducibility=root / "logs" / "reproducibility",
            logs_reproducibility_env=root / "logs" / "reproducibility" / "env",
        )

    def ensure(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# ReproLog dataclass — verbatim from SKIE-Universe
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ReproLog:
    run_id: str
    phase: str
    hypothesis_id: str
    timestamp_utc: str
    git_head: str
    pip_freeze_sha256: str
    pip_freeze_path: str
    dataset_checksums: dict[str, str]
    rng_seed: int
    model_hash: str | None
    config_resolved_sha256: str | None
    host: dict[str, str]
    env_id: str

    def to_dict(self) -> dict:
        return asdict(self)

    def write(self, path: Path) -> Path:
        """Atomically serialize this ReproLog to `path`.

        Pattern: NamedTemporaryFile in destination dir → write → flush →
        os.fsync(fd) → close → os.replace. Atomic on POSIX and on Windows
        (MoveFileEx semantics per Python 3.3+ os.replace docs). Readers
        therefore never observe a partial file.

        Limit: SIGKILL strictly between write and rename may leave the
        tempfile on disk (target untouched). Accepted POSIX limit — no
        userspace pattern can defeat SIGKILL.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_dict()
        data = json.dumps(
            payload, sort_keys=True, indent=2, ensure_ascii=False
        ).encode("utf-8")
        # Binary mode: Windows translates `\n` to `\r\n` in text mode, which
        # would break byte-identity SHA-256 checks. `delete=False` so we can
        # rename; `dir=path.parent` keeps the rename same-filesystem.
        tmp = tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        )
        tmp_path = Path(tmp.name)
        try:
            try:
                tmp.write(data)
                tmp.flush()
                os.fsync(tmp.fileno())
            finally:
                tmp.close()
            os.replace(tmp_path, path)
        except Exception:
            # Clean up orphan tempfile if write/fsync/replace fails.
            tmp_path.unlink(missing_ok=True)
            raise
        return path

    @staticmethod
    def read(path: Path) -> ReproLog:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return ReproLog(**payload)

    @staticmethod
    def verify(path: Path) -> bool:
        """Round-trip verification: read → re-serialize → compare bytes."""
        try:
            on_disk = Path(path).read_text(encoding="utf-8")
            payload = json.loads(on_disk)
            parsed = ReproLog(**payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return False
        canonical = json.dumps(
            parsed.to_dict(), sort_keys=True, indent=2, ensure_ascii=False
        )
        return on_disk == canonical


# --------------------------------------------------------------------------- #
# Capture helpers
# --------------------------------------------------------------------------- #

def _git_head(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
            timeout=_SUBPROCESS_TIMEOUT_SEC,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


def _pip_freeze_bytes() -> bytes:
    """Prefer `uv pip freeze` per project tooling default; fall back to pip."""
    for cmd in (["uv", "pip", "freeze"], [sys.executable, "-m", "pip", "freeze"]):
        try:
            out = subprocess.run(
                cmd, capture_output=True, check=True,
                timeout=_SUBPROCESS_TIMEOUT_SEC,
            )
            return out.stdout
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return b""


def _host_info() -> dict[str, str]:
    return {
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "cpu": platform.machine(),
    }


def _posix(path: Path) -> str:
    return str(PurePosixPath(*Path(path).parts))


def _make_run_id() -> str:
    """ULID when available; uuid4 hex otherwise."""
    try:
        import ulid  # type: ignore
        return str(ulid.new())
    except ImportError:
        import uuid
        return uuid.uuid4().hex


def capture(
    *,
    phase: str,
    hypothesis_id: str = "n/a",
    rng_seed: int = 0,
    dataset_checksums: dict[str, str] | None = None,
    model_hash: str | None = None,
    config_resolved_sha256: str | None = None,
    env_id: str | None = None,
    paths: ProjectPaths | None = None,
    run_id: str | None = None,
) -> ReproLog:
    """Build a ReproLog from the current process state.

    Pure w.r.t. inputs given identical git/pip state — successive calls
    differ only in `timestamp_utc` (and auto-generated `run_id`).
    """
    paths = paths or ProjectPaths.discover()
    paths.ensure(paths.logs_reproducibility_env)

    freeze_bytes = _pip_freeze_bytes()
    freeze_sha = hashlib.sha256(freeze_bytes).hexdigest()
    freeze_path = paths.logs_reproducibility_env / f"{freeze_sha}.txt"
    if not freeze_path.exists():
        freeze_path.write_bytes(freeze_bytes)

    uv_lock = paths.root / "uv.lock"
    lock_id = file_sha256(uv_lock) if uv_lock.is_file() else "no-uv-lock"

    return ReproLog(
        run_id=run_id or _make_run_id(),
        phase=phase,
        hypothesis_id=hypothesis_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        git_head=_git_head(paths.root),
        pip_freeze_sha256=freeze_sha,
        pip_freeze_path=_posix(freeze_path.relative_to(paths.root)),
        dataset_checksums=dict(dataset_checksums or {}),
        rng_seed=rng_seed,
        model_hash=model_hash,
        config_resolved_sha256=config_resolved_sha256,
        host=_host_info(),
        env_id=env_id or lock_id,
    )


def with_model_hash(log: ReproLog, model_hash: str) -> ReproLog:
    return replace(log, model_hash=model_hash)


# --------------------------------------------------------------------------- #
# Self-test entrypoint
# --------------------------------------------------------------------------- #

def _selftest() -> int:
    """Build → write → read → verify round-trip. Exit 0 on success."""
    with tempfile.TemporaryDirectory() as td:
        os.environ["CLAUDE_PROJECT_DIR"] = td
        paths = ProjectPaths.discover()
        paths.ensure(paths.logs_reproducibility_env)

        log = capture(
            phase="bootstrap",
            hypothesis_id="selftest",
            rng_seed=42,
            paths=paths,
        )
        out_path = paths.logs_reproducibility / f"repro_log_{log.run_id}.json"
        log.write(out_path)

        if not out_path.exists():
            print(f"FAIL: output file not created at {out_path}", file=sys.stderr)
            return 1

        if not ReproLog.verify(out_path):
            print(f"FAIL: round-trip verification failed for {out_path}", file=sys.stderr)
            return 2

        # Re-read and check 13 fields present
        re_read = ReproLog.read(out_path)
        d = re_read.to_dict()
        expected_fields = {
            "run_id", "phase", "hypothesis_id", "timestamp_utc", "git_head",
            "pip_freeze_sha256", "pip_freeze_path", "dataset_checksums",
            "rng_seed", "model_hash", "config_resolved_sha256", "host", "env_id",
        }
        if set(d.keys()) != expected_fields:
            print(f"FAIL: field set mismatch. expected={expected_fields}, "
                  f"got={set(d.keys())}", file=sys.stderr)
            return 3

        # Validate pip_freeze_sha256 is exactly 64 hex chars
        if len(re_read.pip_freeze_sha256) != 64:
            print(f"FAIL: pip_freeze_sha256 is {len(re_read.pip_freeze_sha256)} chars; "
                  f"expected 64", file=sys.stderr)
            return 4

        # Validate host has 3 fields
        if set(re_read.host.keys()) != {"os", "python", "cpu"}:
            print(f"FAIL: host fields are {set(re_read.host.keys())}; "
                  f"expected {{os, python, cpu}}", file=sys.stderr)
            return 5

        print(f"PASS: ReproLog round-trip OK at {out_path}")
        print(f"  run_id: {re_read.run_id}")
        print(f"  pip_freeze_sha256: {re_read.pip_freeze_sha256[:16]}... ({len(re_read.pip_freeze_sha256)} chars)")
        print(f"  env_id: {re_read.env_id}")
        print(f"  host: {re_read.host}")
        return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print("Usage: python emit_repro_log.py --selftest", file=sys.stderr)
    sys.exit(64)  # EX_USAGE

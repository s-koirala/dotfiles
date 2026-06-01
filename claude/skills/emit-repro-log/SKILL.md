---
name: emit-repro-log
description: Emit a 13-field ReproLog JSON record before any artifact write to `artifacts/` or `logs/`. Provides reproducibility envelope (git HEAD, pip freeze SHA-256, dataset checksums, RNG seed, model hash) for every run per CLAUDE.md mandate. Invoke at the start of any bootstrap, backtest, inference, validation, or delivery operation.
---

# emit-repro-log

## When to invoke
Before any run that writes to `artifacts/` or `logs/`. This includes:
- Any backtest, inference, or validation run.
- Any pre-registration freeze (`pre-register-hypothesis` skill).
- Any analysis output bundled by `deliver-results`.
- Any commit that uses `commit-with-provenance` (R2-A consumes the emitted log).

Skip for transient EDA / scratch operations that produce no tracked artifact.

## 13-field contract

The 13-field contract is a superset of the 5-field reproducibility mandate in [CLAUDE.md](../../CLAUDE.md) §Reproducibility (git HEAD, pip-freeze SHA-256, dataset checksums, RNG seed, model hash); the remaining fields derive automatically. JSON Schema at [assets/repro_log_schema.json](assets/repro_log_schema.json).

| Field | Type | Semantics |
|---|---|---|
| `run_id` | str | ULID (preferred) or uuid4 hex; lexical-sort property convenient but not required |
| `phase` | str | Suggested values: `bootstrap`, `backtest`, `inference`, `validation`, `deliver` — not enum-constrained for forward compatibility |
| `hypothesis_id` | str | HID e.g. `H055`, or `n/a` for non-hypothesis-bound work |
| `timestamp_utc` | str | ISO 8601, microsecond precision |
| `git_head` | str | 40-hex SHA of HEAD; `"unknown"` if outside a git repo |
| `pip_freeze_sha256` | str | **Full 64-hex SHA-256** of `uv pip freeze` (or `pip freeze`) stdout. NOT a truncated cache digest. |
| `pip_freeze_path` | str | Project-relative POSIX path to the captured freeze text (typically `logs/reproducibility/env/<sha>.txt`) |
| `dataset_checksums` | dict<str,str> | Per-file SHA-256 from `data/_manifest.json` (R1-E populates this) |
| `rng_seed` | int | Explicit seed used; `0` if no sampling |
| `model_hash` | str \| null | Model commit / weight SHA when applicable |
| `config_resolved_sha256` | str \| null | SHA-256 of resolved config snapshot (e.g., frozen `design.md` content) |
| `host` | dict<str,str> | `{os, python, cpu}` — `platform.python_version()` for `python` (version only) |
| `env_id` | str | `file_sha256(uv.lock)` if present; else `"no-uv-lock"` |

## Atomic write semantics

Implemented in [assets/emit_repro_log.py](assets/emit_repro_log.py) `ReproLog.write()`:

```
NamedTemporaryFile(mode='wb', delete=False, dir=path.parent, prefix=f'.{name}.', suffix='.tmp')
  → write bytes → flush → os.fsync(fd) → close
os.replace(tmp.name, path)   # atomic on POSIX and Windows (MoveFileEx)
```

Constraints:
- Same-volume placement (`dir=path.parent`) — `os.replace` is atomic only within a single filesystem.
- Binary mode (`'wb'`) — Windows text-mode CRLF translation would invalidate byte-identity SHA-256.
- `delete=False` — Windows cannot reopen a delete-on-close tempfile.
- `os.fsync(tf.fileno())` — flushes OS write cache to disk; required for crash safety.

Crash window: SIGKILL strictly between write and `os.replace` may leave the tempfile on disk; the target is untouched. This is an accepted limit of POSIX semantics.

## Filename convention

`logs/reproducibility/repro_log_{run_id}.json` (per CLAUDE.md filename rule). The freeze text is sidecar at `logs/reproducibility/env/{pip_freeze_sha256}.txt`.

## CLI

```
python ~/.claude/skills/emit-repro-log/assets/emit_repro_log.py --selftest
```

Builds a fixture record from current env + writes + reads back + verifies round-trip identity. Exit 0 on success.

## Hand-off

- Consumed by [`/commit-with-provenance`](../../commands/commit-with-provenance.md) (R2-A): reads most-recent log under `logs/reproducibility/` and emits `Repro-Log-Path:` + `Repro-Log-SHA256:` trailers.
- Hand-off to [audit-remediate-loop](../audit-remediate-loop/SKILL.md) when used inside that loop's per-deliverable audit.

## References

- Atomic-write pattern: Python `os.replace` docs (atomicity on POSIX + Windows MoveFileEx).
- CLAUDE.md "Reproducibility (hook-enforced)" — 5-field mandate (git HEAD, pip freeze, dataset checksum, RNG seed, model commit); the 13 fields here are a superset.
- Sandve et al. (2013) "Ten Simple Rules for Reproducible Computational Research" *PLOS Comput Biol* 9(10):e1003285. https://doi.org/10.1371/journal.pcbi.1003285

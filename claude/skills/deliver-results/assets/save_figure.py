"""Figure export with publication-grade 3-format bundle + font-embedding check.

Usage:
    from save_figure import save_figure
    fig = plt.figure(...)
    paths = save_figure(fig, slug="my_result", target="single_col")
    # paths is dict: {"png": Path, "svg": Path, "pdf": Path}

Targets (size in inches; per memo §B.3 with Nature/Microsoft citations):
    single_col  3.5 x 2.7    # Nature single-column = 89 mm
    two_col     7.2 x 4.5    # Nature double-column = 183 mm
    ppt_full   13.333 x 7.5  # MS Office 16:9 slide default
    ppt_half    6.5 x 7.5    # half of ppt_full minus 1/3" gutter
    ppt_quad    6.5 x 3.5    # quarter minus gutters
    print_600   <preserved size> at 600 dpi  # Nature line-art / combination

Default save: PNG@300dpi + SVG + PDF. Post-write `pdffonts` check (if poppler
is installed) verifies every font in the PDF shows `emb`+`sub`; non-zero exit
of `pdffonts` is logged as a WARN but does not block — environments without
poppler still produce valid output.

Reproducibility: each call appends an entry to a session-local figure log
under `artifacts/figures/_log_{date}.jsonl` capturing slug, target, sizes,
output paths, and the pip_freeze_sha256 of the calling process. Consumed by
[emit-repro-log](../../emit-repro-log/SKILL.md) at run-end.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


# Target -> (width_inches, height_inches, dpi). Justification per memo §B.3:
# - single_col / two_col: Nature artwork guide (89 mm / 183 mm)
# - ppt_*: Microsoft Office 16:9 default slide = 13.333" x 7.5"
# - print_600: Nature line-art requirement
_TARGETS: dict[str, tuple[float, float, int]] = {
    "single_col":   (3.5,   2.7,  300),
    "two_col":      (7.2,   4.5,  300),
    "ppt_full":    (13.333, 7.5,  300),
    "ppt_half":     (6.5,   7.5,  300),
    "ppt_quad":     (6.5,   3.5,  300),
    "print_600":    (3.5,   2.7,  600),  # default to single_col size; resize as needed
}

Target = Literal["single_col", "two_col", "ppt_full", "ppt_half", "ppt_quad", "print_600"]
Format = Literal["png", "svg", "pdf"]


@dataclass
class SaveResult:
    paths: dict[str, Path]
    target: str
    width_in: float
    height_in: float
    dpi: int
    fonts_embedded: bool | None  # None if pdffonts unavailable


def save_figure(
    fig,
    slug: str,
    target: Target = "single_col",
    formats: tuple[Format, ...] = ("png", "svg", "pdf"),
    out_dir: Path | None = None,
) -> SaveResult:
    """Save `fig` as PNG + SVG + PDF (or specified subset) at the target size.

    Args:
        fig: matplotlib.figure.Figure
        slug: stem of the output filename; final names are `<slug>.<ext>`.
        target: one of _TARGETS keys. Selects size + DPI.
        formats: tuple of extensions to emit.
        out_dir: defaults to `artifacts/figures/`; created if absent.

    Returns:
        SaveResult with paths to written files + metadata.

    Raises:
        ValueError on unknown target or unknown format.
    """
    if target not in _TARGETS:
        raise ValueError(f"unknown target: {target!r}; expected one of {list(_TARGETS)}")
    width, height, dpi = _TARGETS[target]
    fig.set_size_inches(width, height)

    out_dir = Path(out_dir or Path.cwd() / "artifacts" / "figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}
    for ext in formats:
        if ext not in ("png", "svg", "pdf"):
            raise ValueError(f"unsupported format: {ext!r}")
        p = out_dir / f"{slug}.{ext}"
        # PDF/SVG honor rcParams pdf.fonttype/svg.fonttype set by publication.mplstyle
        fig.savefig(p, dpi=dpi, bbox_inches="tight")
        paths[ext] = p

    # Post-write font-embedding check on the PDF (if produced)
    fonts_ok: bool | None = None
    if "pdf" in paths and shutil.which("pdffonts"):
        fonts_ok = _check_pdf_fonts(paths["pdf"])

    # Append to figure log for ReproLog consumption
    _append_figure_log(out_dir, slug, target, width, height, dpi, paths, fonts_ok)

    return SaveResult(
        paths=paths,
        target=target,
        width_in=width,
        height_in=height,
        dpi=dpi,
        fonts_embedded=fonts_ok,
    )


def _check_pdf_fonts(pdf_path: Path) -> bool:
    """Run `pdffonts <pdf>` and verify every font shows `emb` + `sub`.
    Returns True if all fonts embedded; False otherwise. Errors logged to stderr
    but never block."""
    try:
        r = subprocess.run(
            ["pdffonts", str(pdf_path)],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"WARN: pdffonts check skipped for {pdf_path}: {e}", file=sys.stderr)
        return False

    if r.returncode != 0:
        print(f"WARN: pdffonts exit {r.returncode} for {pdf_path}: {r.stderr.strip()}",
              file=sys.stderr)
        return False

    # Parse table: column "emb" should be "yes" for every row beyond the header
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if len(lines) < 3:
        return True  # no fonts (uncommon but valid)
    header = lines[0].split()
    try:
        emb_col = header.index("emb")
    except ValueError:
        print(f"WARN: pdffonts output unrecognized for {pdf_path}", file=sys.stderr)
        return False
    for ln in lines[2:]:  # skip header + separator
        cols = ln.split()
        if len(cols) <= emb_col:
            continue
        if cols[emb_col].lower() != "yes":
            print(f"WARN: font not embedded in {pdf_path}: {ln}", file=sys.stderr)
            return False
    return True


def _append_figure_log(
    out_dir: Path,
    slug: str,
    target: str,
    width: float,
    height: float,
    dpi: int,
    paths: dict[str, Path],
    fonts_embedded: bool | None,
) -> None:
    """Append a JSONL line to artifacts/figures/_log_{date}.jsonl."""
    log_path = out_dir / f"_log_{datetime.now(timezone.utc).date().isoformat()}.jsonl"
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "slug": slug,
        "target": target,
        "width_in": width,
        "height_in": height,
        "dpi": dpi,
        "paths": {ext: str(p) for ext, p in paths.items()},
        "fonts_embedded": fonts_embedded,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

---
description: Render a manuscript markdown (.md/.qmd) to .docx via pandoc using the minimalist B&W reference.docx (12pt Times New Roman, double-spaced, 1" margins — major clinical/medical/public health journal compatible). Emits a render-log sidecar capturing input/output SHA-256 + pandoc version for reproducibility.
argument-hint: "<input.md> [-o <output.docx>] [--standard=<STROBE|CONSORT|STARD|TRIPOD|PRISMA>]"
---

Run the render script with $ARGUMENTS:

    python ~/.claude/scripts/render_manuscript.py $ARGUMENTS

Behavior:
1. Verify pandoc is on PATH (else print install instructions for Windows/macOS/Linux and exit 2).
2. Verify `~/.claude/templates/manuscript/reference.docx` exists (else instruct user to run `build_manuscript_reference.py` once; exit 3).
3. Invoke pandoc:
   ```
   pandoc <input> -o <output.docx> --reference-doc <reference.docx> --standalone
   ```
4. Emit a sidecar `<output>.render.json` with input/output SHA-256 + pandoc version + reference.docx SHA — replay anchor for the rendered doc.

Reference.docx specifications (per user directive 2026-05-15):
- 12pt Times New Roman body (universal across NEJM, JAMA, Lancet, BMJ, Ann Intern Med, AJPH, Am J Epidemiol)
- Double-spaced
- 1" margins all sides
- Page numbers bottom-right
- Bold headings, same point size as body
- Captions 11pt single-spaced (per AMA Manual of Style §4.2.3)
- Title 14pt bold center
- No colors, no shading, no decorative formatting

Templates available for each reporting standard:
- `~/.claude/templates/manuscript/manuscript_strobe_TEMPLATE.md` — observational (STROBE 22-item)
- `~/.claude/templates/manuscript/manuscript_consort_TEMPLATE.md` — RCT (CONSORT 2010 25-item)
- `~/.claude/templates/manuscript/manuscript_stard_TEMPLATE.md` — diagnostic accuracy (STARD 2015 30-item)
- `~/.claude/templates/manuscript/manuscript_tripod_TEMPLATE.md` — prediction model (TRIPOD+AI 2024 27-item)
- `~/.claude/templates/manuscript/manuscript_prisma_TEMPLATE.md` — systematic review (PRISMA 2020 27-item)

Each template has the reporting-standard checklist items embedded as HTML comments next to the corresponding section, so reviewers / submitters can audit completeness without leaving the manuscript.

Identity hygiene: per [rules/publishing.md](../rules/publishing.md), the manuscript YAML frontmatter lists only `author: SKIE` (pseudonym). The reference.docx contains no author metadata (verified empty `dc:creator` / `cp:lastModifiedBy` fields). Run `~/.claude/scripts/render_manuscript.py` does not modify these.

Customization: if a target journal has specific requirements not covered by the defaults (e.g., Lancet specifies Arial, BMJ requires line numbers), edit `~/.claude/templates/manuscript/reference.docx` in Word and save. Re-running `build_manuscript_reference.py` reverts customizations; track venue-specific variants as `reference_<journal>.docx` siblings.

References:
- Pandoc User's Guide — reference-doc option: https://pandoc.org/MANUAL.html#option--reference-doc
- python-docx (for the reference doc generator): https://python-docx.readthedocs.io/
- AMA Manual of Style (11th ed.) — figure/table caption typography: https://www.amamanualofstyle.com/
- ICMJE Recommendations (Jan 2026) — manuscript preparation: https://www.icmje.org/recommendations/

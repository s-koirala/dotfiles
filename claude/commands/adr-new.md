---
description: Create a new Architecture Decision Record under docs/decisions/, auto-numbered, from the ADR template. Use whenever a non-trivial design decision needs durable record.
argument-hint: "<title> [--type=scope|methodology|inference|modeling|execution|project] [--description=<one-line>]"
---

Create a new ADR under the current project's `docs/decisions/` directory. Steps:

1. Verify `docs/decisions/` exists at the project root (walk up from cwd looking
   for `pyproject.toml`, `uv.lock`, or `.git`). If missing, error:
   "No docs/decisions/ at project root. Run `/bootstrap-project` or create
   the directory manually."

2. Scan `docs/decisions/ADR-*.md` files; find the highest NNNN; new ADR is
   NNNN + 1, zero-padded to 4 digits. If no ADRs exist, start at `0001`.

3. Slugify the `<title>` argument:
   - Lowercase.
   - Replace whitespace and underscores with hyphens.
   - Strip non-alphanumeric-and-hyphen characters.
   - Collapse consecutive hyphens.
   - Truncate to 50 chars.

4. Compose the filename: `ADR-{NNNN}-{slug}.md`.

5. Copy the ADR template from
   `~/.claude/templates/adr_TEMPLATE.md` into the new file, performing these
   placeholder substitutions:
   - `<<NNNN>>` → the zero-padded number (e.g. `0007`)
   - `<<TITLE>>` → the raw title argument
   - `<<ONE_LINE_DESCRIPTION>>` → `--description` flag value, or `<TODO: one-line>`
   - `<<TYPE>>` → `--type` flag value, or `project` (default)
   - `<<DATE>>` → today's ISO date (YYYY-MM-DD)
   - `<<SUPERSEDES_OR_BLANK>>` → empty string

6. Verify the placeholder substitutions: grep the resulting file for
   `<<[A-Z_]+>>` patterns — any remaining placeholder OTHER than `<<...>>`
   markers in body prose (which are intentional fillable sections like
   `<<Describe the forces...>>`) indicates incomplete substitution. The
   header-block placeholders (NNNN, TITLE, DESCRIPTION, TYPE, DATE,
   SUPERSEDES) must be fully substituted; body-placeholder text inside
   `<<...>>` may remain as user-fillable guidance.

7. Open the file (or print its path) so the user can fill in the Context,
   Decision, Consequences, Alternatives, References sections.

8. Identity hygiene: ADRs are committed to the project repo. Avoid embedding
   unwanted real-name metadata in the ADR; the author is implicit from the git
   commit author.

9. Report: print the new file path and a one-line summary of what was created.

Reproducibility: ADR creation is a doc edit; no ReproLog needed unless this
command runs inside a larger pipeline (e.g., `bootstrap-project` seeding
ADR-0001).

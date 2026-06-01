---
description: Add a new hypothesis to the project's hypothesis_backlog.md with auto-assigned HID. Quant-project workflow. Validates citations via CrossRef MCP if available.
argument-hint: "<title> [--tier=1|2|3|4|5] [--mechanism-doi=<DOI>] [--notes=<text>]"
---

Append a new hypothesis to the project's `hypothesis_backlog.md`. Steps:

1. **Locate `hypothesis_backlog.md`** at project root (walk up from cwd looking for `pyproject.toml`, `uv.lock`, or `.git`). If absent, error:
   > "No hypothesis_backlog.md at project root. Run `/bootstrap-project --kind=quant` or create it from `~/.claude/scripts/bootstrap_templates/hypothesis_backlog.md.tmpl`."

2. **Parse existing HIDs.** Scan the backlog's main table for rows matching the pattern `| H(\d{3}) |`. The new HID is `max + 1`, zero-padded to 3 digits.

   Reserved blocks (do not auto-assign into these without explicit user direction):
   - H001-H099: core hypotheses
   - H100-H199: replication/reanalysis
   - H900-H999: methodology/gate hypotheses

3. **Validate `--tier`** is in {1, 2, 3, 4, 5}; default to 3 (exploratory).

4. **Validate `--mechanism-doi`** if provided:
   - Format check: Python regex `re.compile(r'^10\.\d{4,9}/[\-._;()/:A-Za-z0-9]+$', re.IGNORECASE)` (case-insensitivity via flag, not JS-style `/i` suffix). Reference: CrossRef DOI regex documentation https://www.crossref.org/blog/dois-and-matching-regular-expressions/.
   - If CrossRef MCP (R1-B) is available, resolve the DOI to confirm it exists and capture the title for the backlog `Mechanism citation` cell.
   - If MCP unavailable, fall back to a polite-pool HTTPS GET `https://api.crossref.org/works/{doi}` with `User-Agent: ${CROSSREF_MAILTO}`.
   - On format failure or 404, abort with error.

5. **Append the row** to the main table (preserving header + tier ordering). Row format matches the template (`~/.claude/scripts/bootstrap_templates/hypothesis_backlog.md.tmpl`):
   ```
   | H<NNN> | <tier> | <title> | designed | <doi> | <notes> |
   ```

6. **Create the per-hypothesis directory** `research/01_hypothesis_register/H<NNN>/` with a placeholder `design.md` (copy template if available; else minimal stub):
   ```
   # H<NNN> — <title>

   Status: designed. Next step: /preregister H<NNN> (R3-2a).
   ```

7. **Stage + commit** the backlog edit + new directory via `/commit-with-provenance`:
   ```
   git add hypothesis_backlog.md research/01_hypothesis_register/H<NNN>/
   /commit-with-provenance "feat(hypothesis): add H<NNN> <title>"
   ```

8. **Report** the new HID, the file paths created, and the next workflow step (`/preregister H<NNN>` once R3-2a lands).

Identity hygiene: the git commit author is whatever the local `git config user.email` is — confirm via `git config user.email` before committing; avoid embedding unwanted real-name metadata.

Reproducibility: HID assignment is deterministic given the backlog state at parse time. No randomness. ReproLog emission is delegated to `/commit-with-provenance`.

References:
- [CrossRef REST API](https://api.crossref.org/swagger-ui/index.html) — for DOI validation
- [International DOI Foundation handbook](https://www.doi.org/the-identifier/resources/handbook/)

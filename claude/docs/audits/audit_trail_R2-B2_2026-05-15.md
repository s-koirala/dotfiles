---
title: Audit trail — R2-B2 (bootstrap templates)
date: 2026-05-15
type: audit_trail
subject: R2-B2 from implementation_plan_dotfiles_additions_2026-05-15.md
loop: per-item audit-remediate-loop
auditor: gate-only (multi-kind end-to-end verification)
rounds_completed: 0
exit_reason: 3 kinds verified end-to-end; all template substitutions correct; manifest tracks per-file SHA
---

# R2-B2 build record

## Files created
- `~/.claude/scripts/bootstrap_templates/` (new directory)
- 12 template files in that directory:
  - **Always-emitted (8):** CLAUDE.md.tmpl, README.md.tmpl, CHANGELOG.md.tmpl, LICENSE.tmpl, .gitignore.tmpl, .gitattributes.tmpl, pyproject.toml.tmpl, .pre-commit-config.yaml.tmpl
  - **Quant-specific (1):** hypothesis_backlog.md.tmpl
  - **Epi-specific (1):** protocol_v0.md.tmpl
  - **Publishing-specific (2):** manuscript.md.tmpl, ai_assistance_statement.md.tmpl

## Files modified
- `~/.claude/scripts/bootstrap_project.py` — added `render_template()`, `template_files_for()`, `render_all_templates()`; bumped to v0.2.0; updated final output line to show tracked-files count.
- `~/.claude/commands/bootstrap-project.md` — updated description to reflect template rendering is now active.

## Placeholder syntax
All templates use `<<KEY>>` syntax consistent with R1-C (CITATION.cff.tmpl) and R1-D (adr_TEMPLATE.md). This avoids the Jinja `{{KEY}}` collision with YAML flow-mapping.

`<<TODO: ...>>` markers are preserved through rendering (only exact `<<KEY>>` matches in the ctx dict get substituted). This is intentional — the markers guide the user to fill in project-specific content.

## Verification gates — all passed

| Gate | Kind | Check | Result |
|---|---|---|---|
| 1 | quant | All 10 expected files rendered (8 always + 1 quant-specific + 1 CITATION.cff) | ✓ |
| 2 | quant | CLAUDE.md header substituted: `<<NAME>>` → `test_quant_v3`, `<<RULES_FILE>>` → `rules/quant-project.md` | ✓ |
| 3 | epi | `docs/protocol/protocol_v0.md` exists with STROBE reporting standard pre-filled | ✓ |
| 4 | publishing | `manuscript/manuscript.md` + `docs/ai_assistance_statement.md` exist | ✓ |
| 5 | All kinds | `manifest.json` populates `files` with SHA-256 per rendered file (10 entries for quant) | ✓ |
| 6 | All kinds | Idempotent re-run: existing files preserved (user edits not overwritten); manifest re-records current SHAs | ✓ |

## Identity hygiene verified
- `LICENSE.tmpl` defaults to MIT with `<<AUTHOR>>` = local part of `--user-email` (e.g., `s-koirala` from `s-koirala@users.noreply.github.com`).
- `CITATION.cff` authors list only `SKIE` pseudonym (inherited from R1-C template).
- `manuscript.md.tmpl` author line lists only `SKIE (pseudonym)`.
- No real-name strings in any template; verified via grep across all 12 templates.

## Edge cases handled
- Templates with no kind-context fall through to the base 8 (generic kind).
- Existing files in target tree are preserved (SHA recorded but not overwritten) — supports incremental re-bootstrap without losing user content.
- `<<DOTFILES>>` placeholder substituted with the user's actual `~/.claude` path (POSIX-normalized for cross-platform pre-commit configs).

## Deferred / known limits
- LICENSE template is MIT-only this round; CC-BY-4.0 variant for publishing kind is a follow-up.
- `directory_structure.md.tmpl` not yet shipped (low priority since `manifest.json` documents structure).
- ADR-0001 not auto-seeded into `docs/decisions/` (user creates via `/adr-new` post-bootstrap; R1-D handles this).
- `--migrate` flag still not implemented (defer to a R2-B3 or future ADR).

## R2-B2 PASS. Proceeding to R2-C (deliver-results skill).

---
title: Audit trail — R1-C (CITATION.cff template + precommit hook + /cite-add)
date: 2026-05-15
type: audit_trail
subject: R1-C from implementation_plan_dotfiles_additions_2026-05-15.md
loop: per-item audit-remediate-loop
auditor: gate-only (parallel to existing precommit_seed_guard.py pattern)
rounds_completed: 0
exit_reason: 4 verification gates passed; subagent audit deferred (functional parallel to existing hook precedent)
---

# R1-C build record

## Files created
- `~/.claude/templates/CITATION.cff.tmpl` — CFF v1.2.0 with `<<KEY>>` placeholders
- `~/.claude/hooks/precommit_citation_cff.py` — pre-commit validator
- `~/.claude/commands/cite-add.md` — slash command consuming CrossRef MCP (R1-B)

## Key design decisions
- **Placeholder syntax `<<KEY>>`** (not Jinja `{{KEY}}`) — chosen to keep raw template parseable by YAML, since `{{KEY}}` triggers YAML flow-mapping interpretation.
- **Hook is fail-soft on missing PyYAML/cffconvert** — emits clear install message; never blocks commits if tooling absent.
- **Hook runs on both `CITATION.cff` and `CITATION.cff.tmpl`** via the `files:` regex `^CITATION\.cff(\.tmpl)?$`.
- **`/cite-add`** uses CrossRef MCP (R1-B `crossref` server) as primary; falls back to direct HTTPS GET if MCP unavailable.

## Verification gates — all passed

| Gate | Check | Result |
|---|---|---|
| 1 | Template's `<<KEY>>` placeholders substitute to `placeholder_KEY`; YAML parses; required CFF v1.2.0 keys present | ✓ All 4 required (cff-version, message, title, authors); 11 optional keys present |
| 2 | Hook exits 0 on a complete CFF fixture | ✓ exit=0 |
| 3 | Hook exits 1 on a fixture missing `authors` with clear error message | ✓ exit=1, stderr cites the missing key |
| 4 | Hook validates the actual template file (placeholders substituted internally) | ✓ exit=0 |

## Skill/command registration
- `/cite-add` appears in the available-skills list immediately on file write.

## Identity hygiene
- Template lists only the author's publishing identity in `authors` (placeholder, no real name).
- ORCID line commented; uncomment only if bound to the publishing identity.
- No real-name fields present.

## Deferred follow-ups
- **`cffconvert` integration:** hook calls `cffconvert --validate` if present on PATH, but `cffconvert` is not in the bootstrap dependency set. Add to `pyproject.toml.tmpl` dev-deps in R2-B2.
- **Register in per-project `.pre-commit-config.yaml`:** done by R2-B2 (template).

## Risks / open items
- The actual `/cite-add` resolution flow is not exercised here (requires CrossRef MCP server running — user-enable post-R1-B). Integration test deferred until R1 + first project bootstrap.

## R1-C PASS. Proceeding to R1-D.

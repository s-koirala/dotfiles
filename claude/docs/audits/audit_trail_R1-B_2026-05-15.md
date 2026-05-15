---
title: Audit trail — R1-B (~/.claude/mcp.json)
date: 2026-05-15
type: audit_trail
subject: R1-B from implementation_plan_dotfiles_additions_2026-05-15.md
loop: per-item audit-remediate-loop
auditor: gate-only (XS-scope JSON manifest)
rounds_completed: 0
exit_reason: verification gate passed; subagent audit skipped per skill spec
---

# R1-B build record

## File created
- `~/.claude/mcp.json` — MCP server manifest

## Servers registered (active)
| Name | Package | Verification | Tools used by |
|---|---|---|---|
| `arxiv` | `arxiv-mcp-server` (PyPI, blazickjp) | GitHub repo + PyPI verified 2026-05-15 | literature-check agent |
| `crossref` | `crossref-cite-mcp` (h-lu) | GitHub repo verified 2026-05-15 | /cite-add command (R1-C) |

## Disabled / placeholder
| Name | Reason |
|---|---|
| `zenodo` | No canonical MCP server exists as of 2026-05-15. Workaround documented inline (`mcp-server-fetch` against Zenodo REST API). Needed for R3-2b OSF pre-reg + rules/publishing.md Zenodo DOI minting. |
| `zotero` | Excluded per user directive (memo §5 Q5 default = drop). |

## Verification gate — passed

| Check | Expected | Actual |
|---|---|---|
| JSON parses | exit 0 | ✓ |
| `uv` available on PATH | version returned | ✓ (uv 0.11.7) |
| No inline tokens/secrets | 0 matches in env values for `token|secret|password|api_key|bearer` keys | ✓ |
| Tuning values (`MAX_RESULTS`, `REQUEST_TIMEOUT`) match upstream defaults | per arxiv-mcp-server README | ✓ |

## Deferred (follow-up gates, post user-enable)
- `claude mcp list` shows the registered servers (user runs `claude mcp add-json arxiv "$(jq '.mcpServers.arxiv' mcp.json)"` etc. — manifest is documentation; Claude Code doesn't auto-register from `~/.claude/mcp.json`).
- `claude mcp call arxiv search_papers` returns non-empty array.

## Risks / open items
- Manifest is documentation-only; **Claude Code does not auto-register MCP servers from `~/.claude/mcp.json`**. Registration requires `claude mcp add-json` per server. Documented inline in `$schema_note`.
- Zenodo gap requires manual workaround until upstream lands a canonical server.

## R1-B PASS. Proceeding to R1-C.

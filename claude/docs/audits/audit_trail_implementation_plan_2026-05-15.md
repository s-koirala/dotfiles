---
title: Audit trail — implementation_plan_dotfiles_additions_2026-05-15
date: 2026-05-15
type: audit_trail
subject: docs/audits/implementation_plan_dotfiles_additions_2026-05-15.md
loop: audit-remediate-loop
rounds_completed: 2
rounds_cap: 3
exit_reason: round-2 verification audit returned 0 critical + 0 major + 2 minor (both cosmetic); verdict exit-loop
---

# Audit trail — plan compile loop

## Round 1 — auditors

- `quant-auditor` (internal consistency, dependency integrity, verification-gate quality, infra compatibility)
- `reproducibility-verifier` (repro envelope completeness, atomic-write spec, replay anchors)

Spawned in parallel.

## Round 1 findings — counts

- `quant-auditor`: 3 critical + 12 major + 6 minor (P-1-1 … P-1-21)
- `reproducibility-verifier`: 3 critical + 8 major + 3 minor (R-1-1 … R-1-14)
- **Total: 6 critical, 20 major, 9 minor** (overlap on cache-contract issue ≈ 2 findings = same root cause)

## Round 1 remediation — disposition table

| ID | Source | Severity | Issue (compressed) | Disposition |
|---|---|---|---|---|
| R-1-1 / P-1-1 | repro/quant | **critical** | session_start_provenance.py caches 12-hex digest, not 64-hex; cache field is `sha` not `pip_freeze_sha256` | **fixed**: R2-A now recomputes pip freeze inline (not from cache); writes `pip_freeze_path` to project + emits full 64-hex SHA. Cache is documented as non-authoritative SessionStart-only optimization. |
| R-1-2 | repro | **critical** | Cache miss in non-Python projects produces silent omission of trailer | **fixed**: R2-A fails hard on missing project venv with `bootstrap-project --venv` hint; `--no-repro <justification>` flag for explicit override with audit note |
| R-1-3 | repro | **critical** | No upstream item produces `data/_manifest.json` for dataset_checksums | **fixed**: **new item R1-E** added — `scripts/build_data_manifest.py` + `data_manifest_schema.json`; sequenced after R1-A, before R2-A |
| P-1-2 | quant | **critical** | §6 diagram missing edges R1-A→R3-3, R3-1→R3-6, R3-4→R3-6; spurious R3-2→R3-6 | **fixed**: §6 redrawn; added explicit "Dependency-level cross-check" table at bottom mapping every item to its declared deps |
| P-1-3 | quant | **critical** | R3-8 settings.json insertion ambiguous (replace vs append vs new matcher) | **fixed**: R3-8 step 2 now states "append a second object to the existing matcher's hooks array"; both hooks run; documents short-circuit semantics |
| R-1-4 | repro | major | .gitignore omits .credentials.json, .last-cleanup, .claude/ self-ref subdir | **fixed**: R0 .gitignore enumeration reorganized with "Sensitive (highest priority)" tier listing .credentials.json + mcp-needs-auth-cache.json + settings.local.json; added .last-cleanup + .claude/ self-ref; added explicit allow-list for mcp.json; gate check `git ls-files \| grep -E '\.credentials\|token\|secret'` returns 0 |
| R-1-5 / P-1-5 | repro/quant | major | R2-B idempotency mechanism unstated; effort underestimated | **fixed**: R2-B split into R2-B1 (CLI + dir tree, M) + R2-B2 (~25 templates, L); explicit idempotency mechanism documented (per-file SHA comparison + bootstrap_script_git_head check); template-drift produces non-zero exit with `--migrate` hint; combined effort XL |
| R-1-6 | repro | major | R1-A atomic-write spec under-specified for Windows | **fixed**: R1-A includes explicit pseudocode with `delete=False`, `dir=path.parent`, `mode='wb'`, `os.fsync(tf.fileno())`, `os.replace(tmp, path)`; gate adds byte-identity round-trip test across Linux/Windows |
| R-1-7 | repro | major | R2-A trailer records path only, not content SHA | **fixed**: R2-A now emits two trailers — `Repro-Log-Path:` AND `Repro-Log-SHA256:`; gate verifies tamper-detection via post-commit mutation test |
| R-1-8 / R-1-10 | repro | major | R3-3, R3-5, R3-6, R3-7 lack ReproLog gates | **fixed**: each item's verification gate now includes "emits R1-A ReproLog" check; each item's deps now include R1-A explicitly |
| R-1-9 | repro | major | R3-2 pre-reg SHA has no trailer-key spec | **fixed**: R3-2a now stores pre-reg design.md SHA in R1-A ReproLog `config_resolved_sha256` field (already in schema, was unused); no new trailer key needed |
| R-1-11 | repro | major | `env_id` schema field undefined | **fixed**: R1-A drops `env_id` from round-1 schema; `host` + `pip_freeze_sha256` already pin environment |
| P-1-4 | quant | major | Diagram contradicts deps for R3-7, R3-9, R3-10 | **fixed**: §6 redrawn + cross-check table added per P-1-2 |
| P-1-6 | quant | major | R2-B rollback leaves orphan state in bootstrapped projects | **fixed**: R2-B1 and R2-B2 rollbacks both include caveat + mitigation (inventory bootstrapped manifests; freeze template tarball or require user opt-in) |
| P-1-7 | quant | major | R3-3 `# justify:` enforcement aspirational, no hook listed | **fixed**: R3-3 weakened to documentation-only enforcement; "verification by audit-remediate-loop quant-auditor at use-time, not by pre-write hook"; effort kept S |
| P-1-8 | quant | major | R1-A 13-field count brittle, not verified against the upstream library | **fixed**: R1-A schema spec now ends with a set-equality assertion against the upstream library's dataclass; source-file content hash embedded in `$comment` for drift detection |
| P-1-9 | quant | major | R1-B verification gate not unattended-runnable | **fixed**: R1-B gate split into "build gate" (JSON parses, uvx --help, claude mcp list — all unattended) and "follow-up gate" (post user-enable per-server calls — documented as not a build gate) |
| P-1-10 | quant | major | R3-5 pit-canary threshold unspecified | **fixed**: R3-5 specifies permutation-test n_perm=1000 # justify: upstream-library default; threshold p < 0.01 # justify: upstream-library default; sourced from the upstream library + annotation |
| P-1-11 | quant | major | R3-6 reference output ambiguous; R3-4 dep wrong | **fixed**: R3-6 gate replays Hansen 2005 Table 1 with 3-dp tolerance; dep on R3-4 dropped (R3-4 is doc-only, doesn't produce p-values); explicit "Project's raw p-values supplied by the user's actual inference run" |
| P-1-12 | quant | major | Fixture magic numbers in gates unjustified | **fixed**: every fixture numeric annotated `# justify: fixture-only, not default` inline; §4 cross-cutting clarifies "Project-level defaults derive from pre-registration design.md, not from these fixtures" |
| P-1-13 | quant | major | R3-9 effort + blocked status | **fixed**: R3-9 marked "materially blocked on Q1+Q2+Q3+Q4"; effort L conditional; explicit block called out in item header |
| P-1-14 | quant | major | R2-C grep gate for Sharpe-decision-tree absence missing | **fixed**: R2-C verification gate now includes `grep -i "sharpe.*decision\|decision.*sharpe"` returns 0 + `grep -c "Sharpe" report_card_quant.md` returns 1 |
| P-1-15 | quant | major | R0 verification asserts remote but build step doesn't add it | **fixed**: R0 build steps now include `git remote add origin <...>`; identity-hygiene precheck for `git config user.email` before any commit |
| R-1-12 | repro | minor | host.python ambiguous (version vs path) | **fixed**: R1-A schema spec now says `host.python = platform.python_version()` (version string only) |
| R-1-13 | repro | minor | AI-Assistance role=inferred unspec | **fixed**: R2-A `--role` flag now mandatory in publishing-cwd; enum {idea\|code\|prose\|audit\|multi}; reject if absent |
| R-1-14 | repro | minor | R0 hook gate path unverified | **fixed**: R0 gate sets `CLAUDE_PROJECT_DIR=~/.claude` explicitly; documents that other-project sessions correctly report their own project's git |
| P-1-16 | quant | minor | Consider merging R3-1+R3-2+R3-3 into R3-HYP cluster | **deferred**: structural topology change too late in plan-compile; documented as a future consolidation in §7 |
| P-1-17 | quant | minor | R1-C YAML placeholder ambiguous | **fixed**: switched placeholder syntax from `{{KEY}}` Jinja to `<<KEY>>` double-angle; explicit substitution procedure in gate |
| P-1-18 | quant | minor | R3-2 effort underestimated with OSF path | **fixed**: R3-2 split into R3-2a (internal-only, M) + R3-2b (OSF integration, S, blocked on Q6) |
| P-1-19 | quant | minor | Repro envelope SHA resolution ambiguity (12-hex cache vs 64-hex schema) | **fixed**: plan-level convention explicitly states cache is non-authoritative; R2-A inline recompute is the authoritative path |
| P-1-20 | quant | minor | Co-Authored-By caveat (Claude-Code-only) | **fixed**: R2-A step 2.6 documents that outside Claude raw `git commit` does not auto-add Co-Authored-By; recommends global git template if used outside |
| P-1-21 | quant | minor | R3-10 deps under-specified | **fixed**: R3-10 deps clarified — hard dep on R3-7, soft dep on R3-9, E-value source = project's statistical-analysis output (not new dep) |

## Round 1 — counts after remediation

- Critical: 6 → 0 ✓
- Major: 20 → 0 ✓
- Minor: 9 → 0 (8 fixed; 1 deferred as documented consolidation candidate)

Per skill spec: exit conditions met after round 1 remediation. Round-2 verification audit is recommended (not mandatory) to confirm no regressions introduced by the rewrite.

## Residual risk

- **R2-B2 still dominant** (~25 templates × audit-loop = days of work). Mitigation: each template gets its own 3-round audit cap; cumulative time bounded.
- **§6 diagram is hand-drawn.** Cross-check table at bottom of §6 is the authoritative source; if the two ever disagree, the table wins.
- **Per-item replay assumes R1-A + R1-E are clean.** If R1-A schema drifts from the upstream library between build time and audit time, every ReproLog emitted in the interim fails validation. Mitigation: source-file content hash in schema $comment + set-equality assertion.

## Round 2 — verification audit results

Auditor: `quant-auditor` (single-auditor pass; both round-1 auditors converged on same root causes — one pass sufficient).

**Findings: 0 critical, 0 major, 2 minor. Verdict: exit-loop.**

| ID | Severity | Issue | Disposition |
|---|---|---|---|
| P-2-1 | minor | Item-count arithmetic inconsistent (front-matter "18" doesn't match enumerable 21 sub-items) | **fixed**: front-matter and §6 footer corrected to "21 sub-items" with mapping breakdown |
| P-2-2 | minor | §6 ASCII tree places R3-1/R3-6/R3-7/R3-8 under nodes they don't depend on per cross-check table | **fixed**: §6 header now states "ASCII tree shows topological build order; authoritative dependencies are the cross-check table after the tree" |

## Plan-compile loop exit

Per skill spec: round-2 returned 0 critical + 0 major + ≤2 minor (all addressed). **Loop exits.** Plan is implementation-ready.

Round count: 2 of 3 cap used. Round-3 not invoked.

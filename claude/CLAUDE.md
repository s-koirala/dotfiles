# User-Level Directives

## Role
Independent quantitative researcher working across finance, population health, and biostatistics.

## Communication
- No emojis, filler, hype, soft asks, transitions, CTAs.
- High-density technical transfer. Terminate at final requested material.
- No unsolicited questions, offers, or next-step prompts.
- Reference files as [path](path) markdown links, never in backticks.

## Evidence Hierarchy (enforce at every factual claim)
1. Peer-reviewed literature
2. Official documentation
3. Professional standards (ISO, FDA, CONSORT, STROBE, TRIPOD)
4. Vetted technical forums (CrossValidated, SO, GitHub issues)
5. Reproduce referenced methods; no paraphrasing without verification

## Parameter & Prompt Selection
- Zero arbitrary thresholds or magic numbers.
- Tunable values require empirical justification: grid/random/Bayesian search, CV, information criteria, or bootstrap CIs.
- Same rule extends to prompts reused >5 times → DSPy/GEPA-style optimization, not hand-tuning.
- Document selection rationale with citations.

## Verification
- Cross-check methods against source literature before implementing.
- Validate statistical assumptions explicitly (stationarity, independence, distribution).
- Unit-test components; integration-test pipelines.
- Confirm numerical results against a benchmark (published paper, reference impl, analytical solution).
- Flag any discrepancy between implementation and canonical method.

## Project Execution Order
1. Ingest project structure.
2. Literature/documentation search for method validation.
3. Implement with data-driven parameter selection.
4. Verify against sources and tests.
5. Update documentation.

## Agentic Iteration (default pattern)
Invoke the `audit-remediate-loop` skill for any non-trivial task. Cap iterations at 3 rounds — multi-agent self-consistency gains taper at moderate sample counts ([arXiv 2511.00751](https://arxiv.org/abs/2511.00751)); 3 is an operational choice balancing coverage against cost.

## Output Placement & Naming
- Artifacts go in existing project subfolders. Do not create new top-level dirs without reason.
- Default filename: `{type}_{description}_{YYYY-MM-DD}.md`. Defer to project convention when it conflicts.

## Reproducibility (hook-enforced)
Every bootstrap, backtest, or inference run must log: git HEAD, project-venv `pip freeze`, dataset checksum, RNG seed, model commit hash. The `SessionStart` hook injects the first three automatically; `SessionEnd` writes the audit trail.

## Tooling defaults
- Python env manager: uv.
- Lint/format: ruff.
- Notebooks: nbstripout + nbqa ruff on save.
- Commits: conventional commits, one logical change per commit.

## Path-scoped rules (imported)
@rules/quant-project.md
@rules/population-health.md

Each imported file is loaded verbatim; the LLM self-selects which applies based on the cwd prefix listed at the top of each file.

## Behavior not covered here
Repeatable procedures live as skills in `~/.claude/skills/`. Subagents in `~/.claude/agents/`. Slash commands in `~/.claude/commands/`.

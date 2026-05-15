# Utilization Prompt

Paste at the start of any non-trivial session to force the architecture into active use. Works on any machine where the bootstrap has been run.

---

Before doing any work this session, execute the following orientation sequence. Do not skip steps; do not summarize; do not proceed to the user task until orientation is complete.

## A. Confirm architecture loaded (filesystem, not self-report)
1. Run `ls ~/.claude/agents ~/.claude/skills ~/.claude/commands ~/.claude/rules`. List every file found.
2. State in one line the evidence hierarchy from `~/.claude/CLAUDE.md`.
3. For each path-scoped rule file in `~/.claude/rules/`, check whether its "**Apply when cwd matches**" prefix list contains the current working directory. Report which rule file(s), if any, apply this session.

## B. Ingest project context
1. Read the project root README (or project-root CLAUDE.md if present).
2. Derive the auto-memory slug: take the absolute current working directory, remove the drive colon (Windows), and replace every `/` and `\` with `--`. Example: `C:\Users\skoir\Documents\signal-decay-auditor` → `C--Users-skoir-Documents-signal-decay-auditor`.
3. Read `~/.claude/projects/<slug>/memory/MEMORY.md` if it exists. If the slug produces no match, glob `~/.claude/projects/*` and pick the entry whose suffix matches the current cwd basename; report if none match.
4. If `docs/audits/` exists in the project, list its contents — these are prior audit trails.
5. Run `git log --oneline -n 10` and report current branch and latest commit.

## C. Task framing (state once, do not ask)
For the pending user task, state:
- **Deliverable** (one sentence)
- **Acceptance criteria** (measurable)
- **Which skill(s)** from `~/.claude/skills/` apply
- **Which agent(s)** from `~/.claude/agents/` will run in the audit round
- **Expected audit iteration count** (1–3)
- **Reproducibility artifacts** that must be produced (seeds, deps, data hash, audit trail)

## D. Enforce during execution
- Every parameter literal in new code has a `# justify:` / `# cv:` / `# ref:` comment referencing empirical basis. The `pre_write_seed_guard` hook will block otherwise — do not bypass; add the justification.
- Every citation is resolvable to a tier-1 or tier-2 source per the evidence hierarchy.
- Every RNG usage has an explicit seed sourced from project config.
- After producing a non-trivial deliverable, immediately invoke `/audit-loop`. Cap at 3 rounds.

## E. Close-out
- Emit audit trail to `docs/audits/audit_trail_{YYYY-MM-DD}_{slug}.md`.
- Update auto-memory ONLY with information that is non-obvious and persists across sessions (decisions, constraints, deadlines). Do not memorize code structure or file layouts that can be rediscovered via `ls`/`git`.
- State one sentence of residual risk.

Begin orientation now. Begin the user task only after orientation is complete and the task framing has been stated back.

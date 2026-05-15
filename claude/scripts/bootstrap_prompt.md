# Cross-Machine Bootstrap Prompt (CLI-driven, audit/QC cycles)

Paste into a fresh Claude Code session on a new machine (local, work, remote) to install the full architecture.

Repo: [github.com/s-koirala/dotfiles](https://github.com/s-koirala/dotfiles) (private). The target machine must have `gh` authenticated to a user with read access. Use `gh auth login` first if not already.

---

You are bootstrapping my Claude Code environment on this machine. Execute every step via the CLI tools available to you (Bash, Read, Write, Grep, Glob, Agent). Do NOT simulate — actually run each command, capture the output, and halt on failure.

## Bootstrap protocol

The protocol has three stages: **install**, **verify**, **audit**. Each stage has a 3-round audit/remediate cap (same cap as the user's `audit-remediate-loop` skill). Do not proceed to the next stage until the current one exits with zero critical findings.

```
REPO_URL=https://github.com/s-koirala/dotfiles.git
REPO_WEB=https://github.com/s-koirala/dotfiles
```

---

## STAGE 1 — INSTALL

### 1.0 Preconditions

Run each; halt on any failure:

- `git --version`
- `python --version` (must be ≥3.10; report if older)
- `gh --version`
- `gh auth status` (halt if not authenticated — repo is private)

Assert `$REPO_URL` matches `^https://github\.com/.+/dotfiles\.git$` and does NOT contain `<fill`. Halt if the placeholder is still present.

### 1.1 Clone or update

- If `~/dotfiles/.git` does not exist: `git clone $REPO_URL ~/dotfiles`.
- If it exists with a clean working tree on `main`: `cd ~/dotfiles && git pull --ff-only origin main`.
- If it exists with local changes or on a divergent branch: **halt** and surface. Never force-pull or discard local work.

### 1.2 Inspect before deploying

```
python ~/dotfiles/claude/scripts/deploy.py --check
```

Capture the diff. If any name from the `PROTECTED` set in [deploy.py](../scripts/deploy.py) appears in the diff, **halt** — a protected artifact is about to be overwritten.

### 1.3 Deploy

```
python ~/dotfiles/claude/scripts/deploy.py
```

Confirm these paths exist after deploy:

- `~/.claude/CLAUDE.md`
- `~/.claude/settings.json`
- `~/.claude/agents/` (3 files)
- `~/.claude/skills/` (3 subdirs)
- `~/.claude/commands/` (3 files)
- `~/.claude/rules/` (3 files)
- `~/.claude/hooks/` (6 files)

### 1.4 Scaffold machine-local settings if absent

```
python ~/dotfiles/claude/scripts/deploy.py --init-local
```

Never put API keys in `settings.local.json::env`. If an OS keychain is available (macOS Keychain, Windows Credential Manager, Linux `pass`/secret-tool), report the command the user will need to add a keychain-backed `apiKeyHelper`.

### 1.5 Idempotency check

Run `python ~/dotfiles/claude/scripts/deploy.py --check` a second time. Must exit 0 with message `in sync`. If not, halt — the deploy is non-deterministic and must be fixed before continuing.

---

## STAGE 2 — VERIFY (filesystem + runtime, not self-report)

### 2.1 Placeholder substitution

Grep the deployed settings.json for `{{CLAUDE_HOME}}`. Zero matches required.

```
grep -c "{{CLAUDE_HOME}}" ~/.claude/settings.json  # must be 0
```

### 2.2 Hook smoke test (shell-agnostic)

Run every hook with empty stdin via Python subprocess — works identically on bash, cmd, and PowerShell:

```
python -c "import subprocess, sys, glob, os; os.chdir(os.path.expanduser('~/.claude/hooks')); [print(f, subprocess.run([sys.executable, f], input=b'{}', capture_output=True, timeout=10).returncode) for f in sorted(glob.glob('*.py'))]"
```

Every line must end in `0`. Report any non-zero.

### 2.3 Realistic payload test

Feed a deliberate seed-guard violation and confirm the hook asks. Capture the JSON:

```
python -c "import subprocess, sys, json; p = subprocess.run([sys.executable, '$HOME/.claude/hooks/pre_write_seed_guard.py'], input=json.dumps({'tool_input': {'file_path': '/tmp/t.py', 'content': 'import numpy as np; x = np.random.rand(100)'}}).encode(), capture_output=True, timeout=10); print(p.stdout.decode())"
```

Output must contain `permissionDecision` and `ask`. If not, the guard is broken.

### 2.4 Tool inventory

Record presence and version of each (do not auto-install):

- `uv --version`
- `ruff --version`
- `pytest --version`
- `nbstripout --version`
- `nbqa --version`

### 2.5 MCP servers

```
claude mcp list
```

Report. Do not auto-register — the user decides per machine which MCPs to enable. Show the active templates from `~/dotfiles/claude/scripts/mcp/` (read each `_status` / `_source` field) and propose the exact `claude mcp add` command for each active one. Skip any template whose `_status` is `planned`.

### 2.6 Identity check

Report `git config --global user.name`, `git config --global user.email`, `hostname`, `uname -a` (or `ver` on Windows cmd). If this machine will be used for the SKIE pseudonym publishing, verify identity hygiene per [rules/publishing.md](../rules/publishing.md) and flag mismatches.

### 2.7 Filesystem architecture verification

```
ls ~/.claude/agents ~/.claude/skills ~/.claude/commands ~/.claude/rules ~/.claude/hooks
```

Cross-reference the output against `~/dotfiles/claude/` contents. Every managed file must appear in both. Report any divergence.

---

## STAGE 3 — AUDIT (independent subagents, max 3 rounds)

Spawn the following audit agents **in parallel** (single message, multiple `Agent` tool calls) using the user's own definitions now deployed at `~/.claude/agents/`:

### Round 1

1. **`reproducibility-verifier`** against the bootstrap result. Brief: "Verify the deployed ~/.claude/ tree matches the dotfiles source exactly, all hooks are runnable, and the installed settings.json has no remaining placeholders. Return the documented JSON verdict schema."
2. **`quant-auditor`** against the hook scripts. Brief: "Audit hooks/*.py for schema correctness (hookSpecificOutput shape), fail-open behavior on bad input, and cross-platform path handling. Return JSON per the quant-auditor.md spec."
3. **`literature-check`** against CLAUDE.md + rules/*.md. Brief: "Verify every external URL and citation resolves. Flag any dead link or misattributed claim. Return JSON per the literature-check.md spec."

### Triage

- `critical` blocks stage exit — must remediate this round.
- `major` is remediated this round.
- `minor` logged but does not block.

### Remediation

- Remediate in-place; do not modify the upstream dotfiles repo from this bootstrap (that is the user's operational repo — the bootstrap must not push changes back).
- If a finding requires a source-of-truth edit (e.g., a broken URL in CLAUDE.md), report it for the user to fix in a separate session; do not push a fix during bootstrap.

### Round 2 (only if round 1 had critical/major findings)

Re-spawn the auditors that returned findings. Exit stage when all three return `accept` OR after round 3.

### Escalation

If residuals remain after round 3: write a `BLOCKED` entry in the final report and halt — do not mark the bootstrap complete.

---

## Final report

Produce `~/dotfiles/claude/logs/bootstrap_{hostname}_{YYYY-MM-DD}.md` with:

- Machine: hostname, OS, shell, Python version.
- Stage 1 / 2 / 3 results per step (pass/fail).
- Tool inventory and missing tools.
- MCP registration proposals (not executed).
- Audit rounds completed + findings disposition table.
- Identity check results.
- Manual follow-ups the user must take (e.g., `apiKeyHelper` setup, missing tool install, MCP registrations, any `BLOCKED` items).

Do not `git add`, `git commit`, or `git push` anything — the bootstrap is read-only toward the repo. If the final report is valuable to keep, leave it under `logs/` (gitignored) and surface the path to the user.

Begin Stage 1 now. Report progress at each stage boundary. Halt on any `halt` directive above.

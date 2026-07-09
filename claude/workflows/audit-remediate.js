// audit-remediate.js — Workflow-engine port of skills/audit-remediate-loop
// (implementation_plan_bootstrap_modernization_2026-07-09.md WI-1).
//
// One invocation = ONE round: route -> audit (parallel specialists) ->
// refute (adversarial gate on critical/major) -> triage. Remediation is the
// lead session's job (workflow scripts cannot edit files; the skill keeps
// produce/revise with the lead) — the lead re-invokes with args.round+1
// after remediating. The 3-round cap is enforced here regardless of caller.
//
// args contract (all routing signals must arrive via args — scripts have no
// filesystem access; deterministic fallbacks by extension/path below):
//   {
//     artifacts:  ["<abs or repo-relative path>", ...],   // required
//     taskSpec:   "<what the artifact was supposed to do>", // required
//     cwd:        "<project cwd for glob routing>",         // required
//     date:       "YYYY-MM-DD",  // required (Date.now() unavailable here)
//     round:      1|2|3,         // default 1
//     flags:      { citations?: bool, repro?: bool, identity?: bool,
//                   statistical?: bool },                   // optional
//     invitesPolish: bool,       // default false: minors logged, not remediated
//     priorDispositions: "<summary of previous rounds>"     // optional, round>1
//   }
//
// Routing (mirrors SKILL.md routing table; deterministic):
//   .py/.ipynb            -> code-reviewer + (quant-auditor XOR epi-auditor)
//                            + reproducibility-verifier
//   .md or flags.citations-> literature-check
//   epi cwd globs         -> epi-auditor (never together with quant-auditor)
//   non-epi cwd           -> quant-auditor for statistical branches
//                            (categorical default: quant-auditor is the
//                            cwd-agnostic statistical generalist)
//   path contains .claude, or flags.identity -> format-auditor
//   flags.repro           -> reproducibility-verifier (in addition to .py rule)

export const meta = {
  name: 'audit-remediate',
  description: '5-branch specialist audit with adversarial refute gate; one round per invocation, 3-round cap enforced in-script',
  whenToUse: 'Invoke via skills/audit-remediate-loop for any non-trivial deliverable. Lead session remediates between rounds and re-invokes with round+1.',
  phases: [
    { title: 'Audit', detail: 'parallel specialist auditors (routed deterministically)' },
    { title: 'Refute', detail: 'adversarial refuter per critical/major finding' },
  ],
}

// ---- args validation ------------------------------------------------------
// Some callers deliver args as a JSON-encoded string rather than a parsed
// object (observed in-harness 2026-07-09); accept both.
if (typeof args === 'string') {
  try { args = JSON.parse(args) } catch (e) { throw new Error('args arrived as a string and is not valid JSON: ' + e.message) }
}
if (!args || !Array.isArray(args.artifacts) || args.artifacts.length === 0)
  throw new Error('args.artifacts (non-empty array of paths) is required')
if (!args.taskSpec) throw new Error('args.taskSpec is required')
if (!args.cwd) throw new Error('args.cwd is required')
if (!args.date) throw new Error('args.date (YYYY-MM-DD) is required — Date.now() is unavailable in workflow scripts')
const ROUND = args.round ?? 1
if (ROUND > 3) throw new Error(`Round ${ROUND} exceeds the 3-round cap (arXiv 2511.00751; skill SKILL.md section Cap). Surface residuals to the user instead of looping.`)
const FLAGS = args.flags ?? {}

// ---- routing (deterministic JS, no agent) ---------------------------------
// Effort tiers mirror agents/*.md frontmatter (single source of truth is the
// agent files; duplicated here because opts.effort is explicit per call).
const TIERS = {
  'quant-auditor': 'high', 'epi-auditor': 'high', 'literature-check': 'high',
  'reproducibility-verifier': 'medium', 'code-reviewer': 'medium',
  'format-auditor': 'low',
}
// Customize to your own population-health project directory names (must
// mirror rules/population-health.md 'Apply when' globs).
const EPI_GLOBS = [/epidemiolog/i, /cohort/i, /clinical/i, /biostat/i, /public-health/i]
const isEpiCwd = EPI_GLOBS.some(re => re.test(args.cwd))
const exts = args.artifacts.map(p => (p.match(/\.[^./\\]+$/) || [''])[0].toLowerCase())
const hasCode = exts.some(e => e === '.py' || e === '.ipynb')
const hasMd = exts.some(e => e === '.md')
const touchesClaudeHome = args.artifacts.some(p => /[/\\]\.claude[/\\]/.test(p) || /^\.claude[/\\]/.test(p))

const branches = new Set()
if (hasCode) {
  branches.add('code-reviewer')
  branches.add(isEpiCwd ? 'epi-auditor' : 'quant-auditor') // XOR, never both
  branches.add('reproducibility-verifier')
}
if (FLAGS.statistical) branches.add(isEpiCwd ? 'epi-auditor' : 'quant-auditor')
if (hasMd || FLAGS.citations) branches.add('literature-check')
if (FLAGS.repro) branches.add('reproducibility-verifier')
if (touchesClaudeHome || FLAGS.identity) branches.add('format-auditor')
if (branches.has('quant-auditor') && branches.has('epi-auditor'))
  throw new Error('Routing invariant violated: quant-auditor and epi-auditor must never run together')
if (branches.size === 0) branches.add('format-auditor') // minimal floor: every artifact gets at least the mechanical pass
const routed = [...branches]
log(`Round ${ROUND}: routed ${routed.length} branch(es): ${routed.join(', ')}`)

// ---- schemas ---------------------------------------------------------------
const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    round: { type: 'integer' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          severity: { enum: ['critical', 'major', 'minor'] },
          category: { type: 'string' },
          location: { type: 'string' },
          issue: { type: 'string' },
          evidence: { type: 'string' },
          fix: { type: 'string' },
          reference: { type: 'string' },
        },
        required: ['id', 'severity', 'category', 'location', 'issue', 'evidence', 'fix'],
        additionalProperties: false,
      },
    },
    residual_risk: { type: 'string' },
    verdict: { enum: ['block', 'proceed-with-remediation', 'accept'] },
  },
  required: ['round', 'findings', 'residual_risk', 'verdict'],
  additionalProperties: false,
}
const REFUTE_SCHEMA = {
  type: 'object',
  properties: {
    finding_id: { type: 'string' },
    refuted: { type: 'boolean' },
    // Categorical evidence types keep the drop rule deterministic without a
    // magic length threshold (plan WI-1: drop requires concrete counter-
    // evidence, never bare disagreement — AUSE 2026 overcorrection guard).
    evidence_type: { enum: ['reproduced-check', 'source-quote', 'counter-test', 'logical-proof', 'none'] },
    refutation_evidence: { type: 'string' },
  },
  required: ['finding_id', 'refuted', 'evidence_type', 'refutation_evidence'],
  additionalProperties: false,
}

// ---- audit + refute, pipelined per branch ----------------------------------
const auditPrompt = (name) => `You are running as the ${name} branch of the audit-remediate loop, round ${ROUND} of max 3.

Artifact path(s):
${args.artifacts.map(p => `- ${p}`).join('\n')}

Task spec / acceptance criteria:
${args.taskSpec}

Project cwd: ${args.cwd}
${args.priorDispositions ? `Prior-round dispositions (do not re-report findings already dispositioned):\n${args.priorDispositions}\n` : ''}
Audit strictly within your agent definition's scope. Read the artifacts with your tools; form independent judgment from the artifact alone. Prefix finding ids with your branch (e.g. "${name.split('-')[0].toUpperCase()}-${ROUND}-1"). Return only the structured findings object.`

const refutePrompt = (f, branch) => `Adversarial refutation gate (audit-remediate loop, round ${ROUND}). A specialist auditor (${branch}) reported this finding against the artifact(s) listed below. Your single job: try to DISPROVE it.

Artifact path(s):
${args.artifacts.map(p => `- ${p}`).join('\n')}

Finding ${f.id} [${f.severity}/${f.category}] at ${f.location}:
issue: ${f.issue}
evidence: ${f.evidence}
claimed fix: ${f.fix}
${f.reference ? `reference: ${f.reference}` : ''}

Reproduce the claimed evidence at the stated location, check any cited source, run the counter-test if one exists. Set refuted=true ONLY with concrete counter-evidence you obtained yourself, and classify it via evidence_type (reproduced-check | source-quote | counter-test | logical-proof). Bare doubt, plausibility arguments, or severity quibbles are NOT refutation: in those cases set refuted=false, evidence_type="none". Do not evaluate whether the fix is optimal — only whether the defect claim is true.`

const branchResults = await pipeline(
  routed,
  (name) => agent(auditPrompt(name), {
    label: `audit:${name}`, phase: 'Audit',
    agentType: name, effort: TIERS[name], schema: FINDINGS_SCHEMA,
  }),
  async (report, name) => {
    if (!report) return null
    const gated = report.findings.filter(f => f.severity === 'critical' || f.severity === 'major')
    const verdicts = await parallel(gated.map(f => () =>
      agent(refutePrompt(f, name), {
        label: `refute:${f.id}`, phase: 'Refute',
        effort: 'high', schema: REFUTE_SCHEMA,
      }).then(v => ({ finding: f, refutation: v }))
    ))
    return { branch: name, report, refutations: verdicts.filter(Boolean) }
  },
)

// ---- triage (deterministic) -------------------------------------------------
const remediate = [], refuted = [], minorsLogged = [], residualRisks = {}, branchVerdicts = {}
for (const br of branchResults.filter(Boolean)) {
  branchVerdicts[br.branch] = br.report.verdict
  residualRisks[br.branch] = br.report.residual_risk
  for (const f of br.report.findings.filter(x => x.severity === 'minor')) {
    if (args.invitesPolish) remediate.push({ ...f, branch: br.branch })
    else minorsLogged.push({ ...f, branch: br.branch })
  }
  for (const { finding, refutation } of br.refutations) {
    const drop = refutation && refutation.refuted === true && refutation.evidence_type !== 'none'
    if (drop) refuted.push({ ...finding, branch: br.branch, refutation })
    else remediate.push({ ...finding, branch: br.branch, refutation: refutation ?? { refuted: false, evidence_type: 'none', refutation_evidence: 'refuter unavailable — finding conservatively retained' } })
  }
}
const survivingCritical = remediate.some(f => f.severity === 'critical')
const survivingMajor = remediate.some(f => f.severity === 'major')
const verdict = survivingCritical ? 'block' : (survivingMajor ? 'proceed-with-remediation' : 'accept')
log(`Round ${ROUND} triage: ${remediate.length} to remediate, ${refuted.length} refuted, ${minorsLogged.length} minors logged -> ${verdict}`)

return {
  round: ROUND,
  date: args.date,
  routing: routed,
  branch_verdicts: branchVerdicts,
  remediate,
  refuted,
  minors_logged: minorsLogged,
  residual_risks: residualRisks,
  verdict,
  cap_reached: ROUND === 3,
  next: verdict === 'accept'
    ? 'exit loop; emit audit_trail per skill post-loop step'
    : (ROUND === 3
        ? 'cap reached: surface residuals to the user; do not loop further'
        : `lead session remediates, then re-invokes with round=${ROUND + 1} and priorDispositions`),
}

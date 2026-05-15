---
title: Audit trail — R3 consolidated audit (8 items)
date: 2026-05-15
type: audit_trail
subject: R3-1, R3-2a, R3-3, R3-5, R3-6, R3-7, R3-8, R3-10 from implementation_plan_dotfiles_additions_2026-05-15.md
loop: audit-remediate-loop
auditors: quant-auditor + literature-check (parallel round 1)
rounds_completed: 1
rounds_cap: 3
exit_reason: 0 critical + 6 major + 14 minor; 6 majors + 3 priority minors remediated; verdict exit-loop
---

# R3 consolidated audit

## Scope
8 R3 items committed without formal subagent audit at build time (gate-only verification at the time). User requested a follow-up audit pass.

## Auditor findings — counts

- `quant-auditor`: 0 critical + 3 major + 8 minor
- `literature-check`: 0 critical + 3 major + 6 minor
- **Total:** 0 critical + 6 major + 14 minor

## Remediation table — majors

| ID | Source | Issue | Disposition |
|---|---|---|---|
| R3-8-1 | quant-auditor | PHI guard `cwd_is_epi` used substring-only matching; would false-positive on `test-pcp-archive/`, `Ultrasound-bak/`, etc. (same defect class as R2-A P2A-1-2) | **fixed**: rewrote `cwd_is_epi` with `_EPI_EXACT_SEGMENTS = {'ultrasound'}` and `_EPI_PREFIX_INFIX = (('pcp','crisis'), ('infectious_disease', None), ('epidemiolog', None))`. Verified on 10 path cases (matches rule globs from `rules/population-health.md` precisely). |
| R3-2a-1 | quant-auditor | YAML colon inside `<<TODO: OSF DOI on R3-2b external pre-reg; omit for internal-only>>` placeholder broke YAML parse | **fixed**: replaced with `<<EXTERNAL_DOI>>` (single-word, no internal colon) + YAML comment for the explanation |
| R3-6-1 | quant-auditor | Same YAML colon defect in multipletest_family_TEMPLATE.yaml `family_id` placeholder | **fixed**: renamed `<<TODO: ...>>` to `<<FAMILY_ID>>` etc. with comments. Template now parses after `<<KEY>>` substitution. |
| L-3-1 | literature-check | pit-canary claimed López de Prado 2018 §7 introduces the canary pattern; §7 actually introduces purge+embargo. Attribution misleading. | **fixed**: reframed §7 as the leakage taxonomy / purge+embargo source; canary pattern explicitly attributed to SKIE-Universe internal lib + AFML §8.3 (permutation importance). |
| L-3-2 | literature-check | `n_perm = 1000` misattributed to Politis-Romano 1994; paper doesn't prescribe B. Same defect in multipletest-gate. | **fixed**: cited Davison & Hinkley 1997 §2.5.1 + Efron & Tibshirani 1993 §19 + Good 2005 Ch.3 as the community-canonical B=1000 sources. Updated both pit-canary SKILL.md and multipletest_family_TEMPLATE.yaml. |
| L-3-3 | literature-check | epi-auditor claimed STARD 2015 has 32 items; actual count is 30 per Bossuyt et al. 2015 BMJ 351:h5527 abstract | **fixed**: changed `32 items` to `30 items` |

## Remediation table — high-priority minors

| ID | Source | Issue | Disposition |
|---|---|---|---|
| R3-3-1 | quant-auditor | power-analysis recommended `zt_ind_solve_power` for two-proportion z-test; that function is for means under known variance | **fixed**: replaced with `NormalIndPower().solve_power(effect_size=proportion_effectsize(p1,p2))` (Cohen 1988 §6.2 Cohen-h transform); added note distinguishing from means z-test |
| R3-1-1 | quant-auditor | DOI regex used JS `/i` flag syntax (would fail in Python `re.match`) | **fixed**: replaced with Python form using `re.IGNORECASE` flag + widened char class to A-Za-z; CrossRef DOI regex docs cited |
| R3-10-1 | quant-auditor | E-value formula `E = RR + sqrt(RR × (RR − 1))` only correct for RR≥1; protective effects (RR<1) yield sqrt(negative) | **fixed**: added explicit case for RR<1 using `RR' = 1/RR`; same dual-form for CI bound (use upper bound when RR<1) |

## Findings deferred as low-priority minor (not remediated)
- R3-2a-2 minor (self-contradictory step 6 phrasing in pre-register-hypothesis SKILL.md): polish only; meaning is clear in context
- R3-5-1 minor (vestigial 0.5 ratio in pit-canary): mitigated by clarifying it's not load-bearing in this round; remove fully on next pass
- R3-7-1 minor (minimum vs minimal adjustment set distinction in dag-drafter): edge case, doc-note sufficient
- R3-3-2 minor (ReproLog ordering after design.md SHA): atomic-write idiom inherited from R1-A
- L-3-4, L-3-6 minor (URL canonical forms — HHS, statsmodels): URLs resolve; canonical-form drift is low-impact
- L-3-7 minor (tier-too-low source for pit-canary thresholds): primary citations now in place (Davison-Hinkley + Good); SKIE-Universe is provenance only
- L-3-8, L-3-9 minor (page-range incompleteness in Hoenig-Heisey and Textor citations): cosmetic

## Verification — all remediations applied

Mechanical grep verification on each fix:
1. pit-canary attribution reframed ✓
2. n_perm=1000 cites Davison-Hinkley ✓
3. STARD 30 not 32 ✓
4. E-value RR<1 formula present ✓
5. power-analysis NormalIndPower for proportions ✓
6. DOI regex Python form ✓
7. multipletest_family template n_boot cites Davison-Hinkley ✓
8. PHI guard `cwd_is_epi` passes 10/10 path test cases ✓
9. Both YAML templates parse after `<<KEY>>` substitution ✓

## Residual risk
- 8 minors deferred (polish-only). No method-fidelity or reproducibility-envelope risk.
- `audit-remediate-loop` SKILL.md router still single-auditor (does not branch quant-vs-epi). Separate task; flagged in §"Outstanding items".
- The Hoenig-Heisey 2001 load-bearing claim in R3-3 verified accurate by literature-check.
- The 18-identifier HIPAA Safe Harbor list in `dua_TEMPLATE.md` verified accurate against HHS guidance.

## Verdict: **exit-loop** (round 1 cleanup pass complete; no further rounds needed)

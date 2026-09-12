# THE STATISTIC — the scoring rule, restated operationally

Governing documents, in force order: `PREREG/F1_SCORER_PREREG.md` (v0, pinned
2026-09-08, OTS block 966099) **as amended by** `PREREG/F1_SCORER_S3_AMENDMENT_v1.md`
(pinned 2026-09-10, OTS block 966355). Reference implementation (read it, don't
trust it): `SCORER/f1_scorer.py`, sha256 `52e9d17d…faaa`, 9,289 B.

## Axes — two, never blended

**Axis A — margin accuracy.** `error = predicted_margin − realised_margin`, both
executed through their respective weather fields (predicted through the forecast,
realised through the realised field), in the object's declared cost unit
(C_X·v²-weighted exposure-hours — see CORRIDOR_COST.md). Reported: MAE and bias
(`margin_stats`), plus bounds coverage where the object declared bounds.

**Axis B — confidence calibration.** Pinned class→probability map, Brier per row:

| class | implied p (PINNED) | Brier if hit | Brier if miss |
|---|---|---|---|
| FULL | 0.90 | 0.01 | 0.81 |
| REDUCED | 0.70 | 0.09 | 0.49 |
| LOW | 0.50 | 0.25 | 0.25 |

Reported: `brier_by_class`, `reliability_table`. The map is pinned and never
tuned; a class hitting far from its pinned p is answered by re-pinning the
ladder's physical rungs as a new trial, never by editing the map (§2, §9).

## "Hit" — as amended 2026-09-10 (S3)

- If the object declared bounds: hit ⇔ realised margin ∈ [lower, upper].
- If not: hit ⇔ sign(realised) = sign(predicted) **and** |error| ≤ tolerance.
- **Tolerance = 27 C_X·v²-weighted exposure-hours — one §7.3 tie band**
  (`TIE_BAND = M0/4 = 108/4`). Written as the derivation, not the bare number:
  if `M0` is ever re-pinned, the tolerance moves with it.
- **Zero convention (ruling 1):** a realised margin of exactly `0.0` **sign-agrees
  with any prediction** — it is sign-less. This states in the pre-registration
  what the reference scorer already implemented (`or realised == 0`).

## Refusals and unscorables

Every emission yields exactly one row. A refusal is CORRECT if the coverage
condition it cited genuinely did not hold (checkable against the archive), else
FALSE; `refusal_accounting` reports the rate, never penalised as such. An
outcome that cannot be computed (AIS gap, no realised field) is UNSCORABLE —
declared, counted, never dropped.

## Intervals

`block_bootstrap_ci` over the pooled Brier with `block_len = 5` windows, only
once ≥ 30 scored rows exist; dispersion only before that.

## R5 — the reproduction tolerances (pinned for this pack, spec v1.1)

| quantity | computation | tolerance |
|---|---|---|
| `error` | one IEEE-754 subtraction | **bitwise equal** |
| per-row `brier` | `(p − h)²`, `h ∈ {0,1}`, `p` from the pinned map | **bitwise equal** |
| `hit`, all counts, `refusal_rate` | integers / integer ratios | **exact** |
| `mae`, `bias`, pooled + per-class `brier`, `observed_hit_rate`, `gap` | `np.mean` (pairwise summation) | `atol = 1e-12` **and** `rtol = 1e-9` |

Only the last row involves summation — the only place a reviewer's `sum()/n` can
legitimately differ from `np.mean`, by ulps. **Any mismatch on any axis is a
finding → a correction-log entry naming the reviewer.** Criticism is answered by
publishing it.

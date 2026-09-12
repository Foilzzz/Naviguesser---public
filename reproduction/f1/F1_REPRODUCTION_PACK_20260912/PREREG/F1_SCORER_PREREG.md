# F1 — SCORER · PRE-REGISTRATION v0 (draft for owner ruling)

**Status:** v0 · **pinned and OTS-stamped 2026-09-08** · the pin-before-first-close deadline was
**missed** — 15 windows closed before the pin (measured from `accrual/f1/register.jsonl` at
2026-09-08T12:05Z); handled by owner ruling D3 2026-09-08 via §8 exclusion + published
correction-log entry, never by retro-dating. This rule governs every window closing **after**
the pin. The draft status line is preserved: *"v0 · 2026-09-03 · must be pinned and OTS-stamped
before the first 72 h window closes (per the ruling resolving the scorer/emission deadlock: the
risk is choosing a scorer that flatters results already seen; no outcome exists until a window
closes)."*
**Implementation:** `naviguesser_overlay/f1_scorer.py` at the pinned digest. Every quantity
below is a named function there.

## 1. Claims — and never claims

- **Claims:** "each F1 guidance object, once its window has closed, is scored on two separate
  axes — margin accuracy and confidence calibration — under a rule fixed before any outcome
  existed; refusals and unscorables are rows in the same record; the L3 switchover is compared
  under this same rule."
- **Never claims:** that a scored margin is a fuel, CO₂ or dollar saving; that adherence (did
  the master follow the advice) measures quality — it is recorded, never scored; that the
  class→probability map is a property of the world — it is a pinned convention.

## 2. Two axes, never blended

**Axis A — margin accuracy.** `error = predicted_margin − realised_margin`, where realised
margin is the recommended route and the baseline route both executed through the realised
weather field (the S∞-style execution through I0), in the object's declared cost unit.
Reported: MAE, bias (`margin_stats`), and — where the object carried bounds — coverage of the
realised value by the declared bounds.

**Axis B — confidence calibration.** Brier score on the object's confidence class:

| class | implied p (PINNED) | Brier if hit | Brier if miss |
|---|---|---|---|
| FULL | 0.90 | 0.01 | 0.81 |
| REDUCED | 0.70 | 0.09 | 0.49 |
| LOW | 0.50 | 0.25 | 0.25 |

Brier is a **proper scoring rule**: expected score is minimised only by reporting the true hit
probability, so it cannot be gamed by under- or over-claiming (`test_always_low_does_not_beat…`,
`test_overclaiming_is_punished`). The asymmetry the ruling asked for follows: a FULL miss costs
3.2× a REDUCED miss; a LOW hit earns nothing over a LOW miss.

**The map is pinned and never tuned.** If the reliability table (`reliability_table`) shows
FULL hitting at 0.6, the fix is the ladder's *physical* rung definitions, never the map — the
same rule as bound-moving.

## 3. "Hit" — pinned definition

If the object declared bounds: hit ⇔ realised margin ∈ [lower, upper].
If not: hit ⇔ sign(realised) = sign(predicted) **and** |error| ≤ tolerance, in the cost unit.
**Tolerance — resolved by owner ruling D3 2026-09-08 as a DEFERRAL, not a value:** it is not
pinned in v0. Until a versioned amendment pins it, an object that did not declare bounds is
**UNSCORABLE-BY-PREREGISTRATION** under §4 — declared, counted, never scored under a rule chosen
afterwards. The amendment must be pinned before any bounds-less object's score is quoted and
before the first ERA5-scorable row exists. *(Superseded draft text, preserved: "⟦INTEGRATION:
tolerance, in the cost unit⟧. The tolerance is pinned here, before any window closes.")*

## 4. Refusals and unscorables

Every emission yields exactly one row (`score`). A refusal is **CORRECT** if the coverage
condition it cited genuinely did not hold — checkable against the archive — else **FALSE**.
Refusal rate is reported (`refusal_accounting`); it is not penalised as such. An outcome that
cannot be computed (AIS gap, no realised field) is **UNSCORABLE**, declared, never dropped.

## 5. The switchover comparison

From the pinned switch date, `compare_sources` partitions scored rows by `emitted_source` on
**paired windows only** (windows where both sources have a scored row), reports both axes per
source, and the **veto rate** among overlay attempts. Pre-declared possible outcomes, all
publishable: overlay better · indistinguishable · worse · mostly vetoed. A high veto rate is a
finding about L1/L2, not a failure of the experiment.

## 6. Reporting cadence

Weekly close-out carries: rows scored this week, `margin_stats`, `brier_by_class`,
`reliability_table`, `refusal_accounting`. Intervals on the pooled Brier via `block_bootstrap_ci`
(`block_len` = ⟦INTEGRATION: 5⟧ windows) once ≥ 30 scored rows exist; dispersion only before.

## 7. Stopping conditions

1. Any change to the class→p map or the hit definition after the first window closes → the
   standing harness rules govern; the original stays in force.
2. A scored row whose `emitted_source` is not in {backbone, overlay} → stop-and-report.
3. An emission with no row → the record has a silent gap → stop-and-report.

## 8. Exclusion — windows closed before the pin (owner ruling D3, 2026-09-08)

Every guidance window whose `window_close` precedes this document's OTS-stamp instant is
**EXCLUDED-BY-PREREGISTRATION** from the scored record: excluded, named by `guidance_id`, and
counted in the correction-log entry of the same date (`public/CORRECTION_LOG_ENTRY_2026-09-08_scorer_timing.md`).
They are not scored quietly, and not scored under a rule written afterwards. The residual,
stated accurately: those emissions were sealed at emission time and remain valid sealed
predictions; what they lack is a pre-committed scoring rule. Any third party may score them
under any rule they choose, and we will publish the result whatever it says.

## 9. Response to an unfavourable verdict (owner ruling D8, 2026-09-08)

If the scored record is unfavourable — margin accuracy materially worse than this rule's
structure implies, or calibration showing a class hitting far from its pinned p (§2's example:
FULL at 0.6):

1. the weekly close-outs and the final table are **published unchanged** — the verdict stands
   as measured, in the same form T2-live already commits to;
2. a correction-log entry states the outcome without softening;
3. the class ladder's physical rung definitions and the corridor machinery are revisited **only
   as a new, separately pre-registered trial** — nothing is retuned on the scored data;
4. emissions continue under this pinned rule until that new pre-registration exists.

The favourable direction buys the mirror-image nothing: the rule does not loosen, the cadence
does not quicken, and no claim grows beyond §1's claims.

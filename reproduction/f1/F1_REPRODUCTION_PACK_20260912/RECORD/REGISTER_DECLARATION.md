# F1 register — standing declarations

Pinned alongside the register at integration, 2026-08-29. These declarations
travel with the register so that no later reader has to reconstruct the
reasoning from chat history.

## 1. The scorer/emission deadlock ruling (owner, 2026-08-29)

> The scorer pre-registration (B1) is pinned before the first window
> CLOSES; at first emission no outcome exists yet, so scoring machinery
> cannot gate emission.

B1 therefore gates on the first window close (at the declared trial start
and 12:00 UTC emission cadence, the earliest close is start+3 days, 13:00
UTC) — not on the first emission. This sequence is declared here so it
cannot later be read as a shortcut: emission comes first *by ruling*, and
the scorer arrives before anything can be scored.

## 2. M0 calibration measurement (2026-08-29)

In the prereg's pinned margin units (C_X·v²-weighted exposure-hours, §3),
typical |predicted_margin| is O(10²–10³) — e.g. ΔC_X 0.1 × v_rel²
150 m²/s² × 72 h = 1,080. The pinned M0 = 0.5 (§7.2) and the M0/4 tie band
(§7.3) therefore do not bind, and INDIFFERENT is emitted only at exact
corridor ties. The implementation carries the pinned values **unchanged**
— boundaries are never redrawn against an observed distribution (D4.4).
Reported as a v0.4 amendment candidate; any change is the owner's ruling,
landed as a prereg amendment **before** first emission or not at all.
Also declared in `corpus_intake/f1_optimizer_settings.json` (margin_units),
whose digest is pinned in the integration config.

## 3. Structural properties of the v0 optimizer family

The declared candidate family (constant heading offsets 0, ±2.5…±10°) always
contains the current corridor, so `predicted_margin ≤ 0` structurally and
CURRENT_BETTER is unreachable under this family — a declared property of the
S1-family idealisation (prereg §6), not a scoring defect. Ranking realism is
the scorer's domain (B1) against realised wind at close-out.

## 4. Register shape

`register.jsonl` — one guidance object per line, hash-chained
(prev_digest), pin timestamp = register write time (prereg §4).
`gaps.jsonl` — watched vessels the core could not cost on an emission day,
with the reason; a gap is a recorded coverage miss, never a silent skip,
never a run failure. `watchlist.json` — the active watchlist state
(21-day cap / 72-h no-position drop, prereg §2).

## 5. v0.4 annotation (Amendment A4, 2026-08-29 — annotated, never rewritten)

- §1's cadence-dependent figure moves with A4: at the 16:30 UTC emission
  cadence the earliest window close is trial_start+3 days, **17:30 UTC**
  (superseded: 13:00 UTC at the v0.3 12:00 UTC cadence). B1's gate is
  unchanged in substance: the scorer lands before the first close.
- §2's M0 measurement STANDS as the A4 derivation's source. A4 re-pinned
  M0 = 108 (ΔC_X 0.01 × v_rel² 150 m²/s² × 72 h, one-tenth of §2's
  typical 1,080) before first emission; §2's closing clause is thereby
  discharged — the change was the owner's ruling, landed as a prereg
  amendment **before** first emission.


## 6. v0.5 annotation (Amendment A5, 2026-08-30 — annotated, never rewritten)

- A5 was triggered by CC's PR-#95 discharge measurement: the archiver's
  cycle hour is not stable (18Z ×7, then 06Z ×2, then 00Z at 10:24Z on
  2026-08-29), and A4's 14-lead set (6..84) covered a 16:30 UTC emission
  from a 06Z cycle **only**, by 1.5 h — an undeclared load-bearing
  coincidence. Under A5, cycle selection is the coverage rule (freshest
  whose 20 leads 6..120 cover the window; skip non-covering; stop if
  none), and the pack name is no longer hard-pinned to a cycle hour.
- Nothing in §§1–5 moves: M0 = 108 stands, the cadence stands, the
  earliest window close stands (trial_start+3 days, 17:30 UTC), and the
  no-manoeuvre-cost idealisation stands. Forecast age now varies with
  the selected cycle (10.5 h for 06Z, 16.5 h for 00Z at the 16:30 UTC
  emission) and prices through §7.2's freshness dimension as declared.

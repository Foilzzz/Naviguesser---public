# CORRIDOR & COST SEMANTICS — what the numbers mean

Rule id `const_cog_sog_rhumb_1h_midpoint`, single source `SCORER/f1_daily_guidance.py`
(`compute_corridors`, `step_values`, `_wind_at`, `_interp_cx`). Declared in
`RECORD/f1_integration.json` (`corridor_rule`) and `POLAR/f1_optimizer_settings.json`.

## Corridors

- **Origin:** the vessel's most recent AIS position report in the 24 h before
  emission (recorded in the entry as `origin` with `fix_utc`). No fix → a
  recorded gap in `RECORD/gaps.jsonl`, never a fabricated origin.
- **Current corridor:** constant COG/SOG rhumb-line extrapolation from the
  origin; 72 one-hour bins over the window, sampled at bin midpoints; positions
  extrapolated from the fix instant.
- **Preferred corridor:** argmin exposure over the declared candidate family of
  constant heading offsets (`[0, ±2.5, ±5, ±7.5, ±10]`°). The current corridor
  (offset 0) is a member, so `predicted_margin ≤ 0` structurally; ties break
  deterministically by `(exposure, |offset|, offset)`.

## Cost

- Per bin: `C_X(θ) · v_rel²` where `v_rel` is the apparent wind (forecast wind
  vector minus the ship vector) and θ the relative wind angle with **head wind = 0°**.
- `C_X(θ)` is linear interpolation of the pinned angular table for the object's
  curve (e.g. `cargo_vessel|laden`), from `POLAR/parametric_reference_declared.json`
  (sha256 `57fd8e8d…f9c5`). The §5.3 θ=0 gate is re-asserted at every load:
  each table's `C_X(0)` must equal its head-wind anchor.
- **Unit:** C_X·v²-weighted exposure-hours. Margins, errors and the S3 tolerance
  (27) all live in this unit; it is a comparative exposure measure, **not** a
  fuel, CO₂ or dollar figure — the §1 never-claims travel with this pack.
- **Wind:** nearest grid point in space, linear between bracketing lead times,
  from the digest-verified cycle extract in `WIND/`. No extrapolation: a bin
  outside coverage is `None`.
- **Coverage is paired** across the whole candidate family: a bin counts only
  when EVERY offset covers it, so candidate exposures stay comparable. The margin
  is the paired per-bin mean scaled to 72 bins (`scale = 72 / paired`). Coverage
  short of 72/72 degrades confidence and is recorded in the entry's `integrity`
  block, never silent.

## Vessel type

`vessel_type` populates forward from the watchlist feed's type-5/24 statics
(amendment A3). UNKNOWN is a declared mode, exactly one confidence degradation;
UNKNOWN-type objects resolve to the declared `unknown` curve key.

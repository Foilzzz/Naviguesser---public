# F1 REPRODUCTION PACK — 2026-09-12

**The claim under test** (scorer prereg §1): *every F1 guidance object, once its
window closes, is scored on two separate, never-blended axes — margin accuracy
and confidence calibration — under a rule fixed before any outcome existed;
refusals and unscorables are rows in the same record.* This package proves
**record integrity + score reproducibility**. It never proves the guidance is
*good* — that is the trial's job.

Today the record is the **null record**: 38 register entries, **0 scored rows**,
15 windows EXCLUDED-BY-PREREGISTRATION §8 (named in
`PREREG/CORRECTION_LOG_ENTRY_2026-09-08_scorer_timing.md`), the remainder
bounds-less objects governed by the S3 amendment. Reproducing it exactly is a
real check; the first scored rows are reproduced by these same instruments with
no redesign.

## Run it

```
python reproduce.py
```

Exit 0 only on full agreement with `EXPECTED/EXPECTED.json`. Five checks:
register chain head-to-genesis (R1), pin timing (R3), record counts (R4),
emission-artefact agreement, and no-silence coverage. Any mismatch is a named
finding, printed, never edited. Zero dependencies; a reviewer can equally
re-implement every check from `SPEC/` — that is the point of L1.

- **L1 verify-only:** the OTS receipts in `PREREG/` against Bitcoin (your
  explorer, your client); the register chain by your own implementation of
  `SPEC/CHAIN_RULE.md`.
- **L2 recompute:** `reproduce.py` or your own implementation from `SPEC/`.
- **L3 provenance:** `WIND/REFETCH_RECIPE.md` — re-fetch one GEFS cycle from
  noaa-gefs-pds and match digests.
- **Worked example:** `SPEC/WORKED_EXAMPLE.md` traces one object end-to-end with
  every intermediate; regenerate it with `SPEC/trace_worked_example.py`.

## Declared trust boundaries

1. The scorer is a pure library (no I/O; `Emission`/`Outcome`/`ClassMap` in,
   `ScoredRow` out), pinned at `52e9d17d…faaa`. But `Outcome.realised_margin` is
   an *input* to it: **L1/L2 trust the entire outcome construction**, of which
   wind extraction is one part. That code ships in `RECORD/`, pinned — that is
   what turns this boundary from trust into check.
2. **No raw AIS is redistributed.** The per-window corridors embedded in the
   register are derived quantities (origin fix, COG/SOG, rule); adherence is
   recorded, never scored.
3. The pack proves the record is intact and the scoring is what the
   pre-registration declares. It never proves a fuel, CO₂ or dollar saving —
   the §1 never-claims travel with the pack.
4. **GEFS and ERA5 are not symmetric.** noaa-gefs-pds is anonymous; CDS is
   credentialed. L3 closes the GEFS derivation by re-fetch; ERA5 ships as
   derived series + manifests when scored rows exist, declared trusted-by-L1/L2.

## Layout

| dir | content |
|---|---|
| `PREREG/` | scorer prereg v0 + S3 amendment (both OTS-anchored) + §8 exclusion entry |
| `RECORD/` | register, emit artefacts, refusal artefacts, gaps, outcome-construction code |
| `SPEC/` | chain rule · statistic · corridor/cost semantics · worked example (+ its generator) |
| `POLAR/` | the pinned C_X artefact + optimizer settings the emitter digest-verifies |
| `WIND/` | the 11 register-referenced GEFS cycles (extracts + manifests) + refetch recipe |
| `SCORER/` | the pinned reference scorer + the pinned emitter (single rule source) |
| `EXPECTED/` | the measured counts this pack must reproduce |
| `MANIFEST.json` | sha256 + bytes of every member; the pack's outer digest is pinned and OTS-stamped at build |

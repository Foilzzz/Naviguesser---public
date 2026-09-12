# L3 PROVENANCE — re-fetch recipe (GEFS)

The wind extracts in this pack (`f1_wind/<cycle>/wind_box_<N>.json`) derive from
NOAA's public GEFS bucket. Re-fetching one cycle and re-deriving one window's
series closes the one derivation L1/L2 take on trust.

## Source

- Bucket: `s3://noaa-gefs-pds` (anonymous, no credentials — the GEFS/CDS
  asymmetry is declared in README §4: ERA5 cannot be re-fetched on these terms).
- URL pattern: `https://noaa-gefs-pds.s3.amazonaws.com/gefs.{YYYYMMDD}/{HH}/atmos/pgrb2ap5/`
- Messages: **UGRD and VGRD at 10 m** only, leads 6–120 h in 6 h steps, fetched
  by HTTP byte range from the `.idx` sidecar (never whole GRIB files).
- The builder is `analysis/f1_wind_extract_local.py` (owner-side; the recipe is
  declared here so a reviewer's own fetcher can substitute for it).

## Verify

1. Pick a cycle directory in this pack (e.g. `f1_wind/2026-09-11T00/`).
2. Its `manifest.json` pins every member's sha256 and byte size. Re-fetch the
   source messages for that cycle, re-extract the four boxes, and compare
   against the shipped members — or, at minimum, confirm the shipped members
   hash to the manifest (`sha256` over file bytes).
3. The `source_cycle` field (`20260911/00`) names the upstream run. GEFS cycles
   are immutable once published; a digest mismatch on a re-fetch is a finding
   about the pipeline, reported, not edited.

## Recommended exercise

The worked example's own cycle (**2026-09-11T00**) — an L3 finisher lands
directly on the written-out numbers in `SPEC/WORKED_EXAMPLE.md` — plus one
deliberately older cycle (2026-08-29T00 or 2026-09-01T00), so re-fetch is
exercised against non-recent data.

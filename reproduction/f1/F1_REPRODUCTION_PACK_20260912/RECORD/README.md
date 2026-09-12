# RECORD/ — the emission record, complete to 2026-09-11

- `register.jsonl` — the append-only register; one JSON object per line
  (`guidance`, `pin_utc`, `pin_valid_on_time`, `prev_digest`). The chain rule is
  SPEC/CHAIN_RULE.md.
- `emit_YYYY-MM-DD.json` — per-run artefact: `pinned` objects that run, register
  `head` after it, the cycle used, `late`/`dup`/`gaps` counters, `type_unknown`.
- `emit_2026-08-31.DECLARED_ZERO.md` — the slot ran and emitted zero objects.
  The absence of `emit_2026-08-31.json` is declared by this artefact, not silent.
- `F1_INVARIANT_2026-09-03_EMIT_ARTEFACT_MISSING.md` and
  `F1_INVARIANT_2026-09-06_EMIT_ARTEFACT_MISSING.md` — the two days the emit
  artefact itself went missing, declared at artefact level; the register rows
  for both days exist and reconcile.
- `dryrun_2026-08-29.json` — the pre-trial dry run (`mode: "dryrun"`). Not an
  emission; carried for completeness and excluded from emission accounting by
  `reproduce.py`.
- `gaps.jsonl` — recorded watchlist gaps (a watched vessel the emitter could not
  cost), never silent skips.
- `watchlist.json`, `declared_boxes.json`, `f1_integration.json` — the watched
  fleet, the declared corridor boxes, and the integration pins the emitter read.
- `outcome_construction_f1_shadow_scorer.py` — the outcome-construction code
  (computes `realised_margin` per closed window: both corridors executed through
  the realised wind field). Ships pinned because L1/L2 otherwise take the
  outcome construction on trust (spec §4.1). It imports the pinned emitter —
  `SCORER/f1_daily_guidance.py` — for the wind and cost primitives, by design:
  single rule source, never a second implementation.

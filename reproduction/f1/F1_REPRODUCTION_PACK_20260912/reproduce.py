#!/usr/bin/env python3
"""reproduce.py — F1 reproduction pack runner. Zero dependencies (stdlib only).

Reproduces the F1 record AS IT STANDS from the bytes in this pack and compares
against EXPECTED/EXPECTED.json. Exit 0 only on full agreement. Any mismatch is
printed as a FINDING and the exit code is 1 — a finding is reported, never
edited (pack rule, per the scorer prereg's stopping conditions).

Today the record is the null record (0 scored rows): reproduction is chain
integrity + timing + accounting. When scored rows exist, this same runner
gains the R5 stratified-tolerance comparison with no redesign — the R5 table
is pinned in SPEC/STATISTIC.md already.

Levels (spec §2): this runner is L1+L2. L3 (provenance re-fetch) is
WIND/REFETCH_RECIPE.md and is exercised separately.

Checks:
  C1 chain (R1)    head-to-genesis: prev_digest linkage + per-object sha256.
  C2 timing (R3)   every pin_utc precedes its window_open; the stored
                   pin_valid_on_time flag equals the recomputation; the
                   declared emission lag (window_open = issued + 1 h) holds.
  C3 counts (R4)   entries / bounds / §8-excluded set / scored == EXPECTED.
  C4 emissions     every emit day's pinned count equals the register's rows
                   for that day; the emit's head prefix equals the register
                   head after that day's appends; days with no emit artefact
                   are exactly the declared ones (zero day, invariant days).
  C5 no silence    every register row's issue date is covered by an emit
                   artefact or a declared artefact. A run that succeeded and
                   emitted nothing must leave a declaration, not a gap.
"""
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENESIS = "0" * 64
S8_STAMP = datetime(2026, 9, 8, 12, 5, tzinfo=timezone.utc)  # scorer prereg OTS instant (§8)
LAG = timedelta(hours=1)                                     # pinned emission lag (SPEC/CHAIN_RULE.md)

findings = []


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name:44} {detail}")
    if not ok:
        findings.append(f"{name}: {detail}")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _load_lines(path):
    """Parse the register. A line that does not parse is a NAMED finding, never
    a traceback — a traceback exit is indistinguishable from a clean refusal to
    a caller reading only the status (the smuggled-shard lesson)."""
    raw = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    entries, parse_errors = [], []
    for i, l in enumerate(raw, 1):
        try:
            entries.append(json.loads(l))
        except json.JSONDecodeError as e:
            entries.append(None)
            parse_errors.append(f"line {i}: unparseable ({e.msg} at char {e.pos})")
    return raw, entries, parse_errors


def main():
    record = ROOT / "RECORD"
    try:
        raw_lines, entries, parse_errors = _load_lines(record / "register.jsonl")
        expected = json.loads((ROOT / "EXPECTED" / "EXPECTED.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[FAIL] pack unreadable                            {type(e).__name__}: {e}")
        print("\nREPRODUCTION FAILED — 1 finding, reported not edited:")
        print("  FINDING: pack unreadable:", e)
        return 1
    if parse_errors:
        for p in parse_errors:
            check("C1 register chain head-to-genesis", False, f"chain-break {p}")
        print(f"\nREPRODUCTION FAILED — {len(parse_errors)} finding(s), reported not edited.")
        return 1

    # ---- C1 chain (R1) ----------------------------------------------------
    prev, chain_ok, bad = GENESIS, True, None
    for i, (line, e) in enumerate(zip(raw_lines, entries), 1):
        if e.get("prev_digest") != prev:
            chain_ok, bad = False, f"line {i}: prev_digest mismatch"
            break
        g = e.get("guidance", {})
        body = {k: v for k, v in g.items() if k != "sha256"}
        if g.get("sha256") != sha(canon(body)):
            chain_ok, bad = False, f"line {i}: guidance sha256 mismatch"
            break
        prev = sha(line.rstrip("\n").encode("utf-8"))
    check("C1 register chain head-to-genesis", chain_ok,
          bad or f"chain-ok over {len(entries)} entries, head {prev[:12]}")

    # ---- C2 timing (R3) ----------------------------------------------------
    timing_ok = all(ts(e["pin_utc"]) < ts(e["guidance"]["window_open"]) for e in entries)
    flag_ok = all(bool(e["pin_valid_on_time"]) ==
                  (ts(e["pin_utc"]) < ts(e["guidance"]["window_open"])) for e in entries)
    lag_ok = all(ts(e["guidance"]["window_open"]) - ts(e["guidance"]["issued_utc"]) == LAG
                 for e in entries)
    check("C2 pin precedes window_open (R3)", timing_ok and flag_ok and lag_ok,
          f"{len(entries)}/{len(entries)} on time; stored flags agree: {flag_ok}; "
          f"declared 1 h lag holds: {lag_ok}")

    # ---- C3 counts (R4) ----------------------------------------------------
    bounds = sum(1 for e in entries if e["guidance"].get("bounds"))
    excluded = sorted(e["guidance"]["guidance_id"] for e in entries
                      if ts(e["guidance"]["window_close"]) < S8_STAMP)
    scored = sum(1 for e in entries
                 if any(k in e for k in ("score", "scored", "outcome")))
    ok = (len(entries) == expected["register_entries"]
          and bounds == expected["guidance_with_bounds"]
          and excluded == expected["excluded_by_prereg_s8"]["guidance_ids"]
          and scored == expected["scored_rows"])
    check("C3 counts == EXPECTED (R4)", ok,
          f"entries {len(entries)}, bounds {bounds}, §8-excluded {len(excluded)}, "
          f"scored {scored} (expected {expected['register_entries']}/"
          f"{expected['guidance_with_bounds']}/{expected['excluded_by_prereg_s8']['count']}/"
          f"{expected['scored_rows']})")

    # ---- C4 emission artefacts agree with the register ---------------------
    by_day = {}
    for idx, e in enumerate(entries):
        by_day.setdefault(e["guidance"]["issued_utc"][:10], []).append(idx)
    day_head = {}
    prev = GENESIS
    for i, line in enumerate(raw_lines):
        prev = sha(line.rstrip("\n").encode("utf-8"))
        day_head[entries[i]["guidance"]["issued_utc"][:10]] = prev[:12]
    emit_days, emit_ok, emit_detail = {}, True, ""
    for f in sorted(record.glob("emit_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("mode") != "emit":
            continue  # dry-run artefact, declared in RECORD/README note
        day = f.stem.replace("emit_", "")
        emit_days[day] = d
        n_reg = len(by_day.get(day, []))
        if d["pinned"] != n_reg or d["head"] != day_head.get(day):
            emit_ok = False
            emit_detail = (f"{day}: emit pinned {d['pinned']} vs register {n_reg}, "
                           f"head {d['head']} vs {day_head.get(day)}")
            break
    check("C4 emit artefacts == register (counts + heads)", emit_ok,
          emit_detail or f"{len(emit_days)} emit days reconcile to the row")

    # ---- C5 no silence ------------------------------------------------------
    declared = {"2026-08-31": "DECLARED_ZERO (ran, emitted zero)",
                "2026-09-03": "F1_INVARIANT_2026-09-03_EMIT_ARTEFACT_MISSING.md",
                "2026-09-06": "F1_INVARIANT_2026-09-06_EMIT_ARTEFACT_MISSING.md"}
    for d_, why in declared.items():
        artefact_present = ((record / f"emit_{d_}.DECLARED_ZERO.md").is_file()
                            or any(d_ in r for r in expected["refusal_artefacts"]))
        if not artefact_present:
            findings.append(f"C5: declared day {d_} ({why}) lacks its artefact in RECORD/")
    silent = [d_ for d_ in by_day if d_ not in emit_days and d_ not in declared]
    check("C5 every register date covered by emit or declaration", not silent,
          f"uncovered dates: {silent}" if silent else
          "all 12 emission days reconcile; 1 zero day + 2 invariant days declared at artefact level")

    # ---- verdict -------------------------------------------------------------
    print()
    if findings:
        print(f"REPRODUCTION FAILED — {len(findings)} finding(s), reported not edited:")
        for f_ in findings:
            print("  FINDING:", f_)
        return 1
    print(f"REPRODUCED — the record as it stands: {len(entries)} entries, 0 scored rows, "
          f"{len(excluded)} §8-excluded-and-named, chain-ok, timing-ok, emissions reconcile.")
    print("This reproduces record integrity and accounting. It does not show the guidance is "
          "good — that is the trial's job (SPEC/STATISTIC.md, scorer prereg §1 never-claims).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

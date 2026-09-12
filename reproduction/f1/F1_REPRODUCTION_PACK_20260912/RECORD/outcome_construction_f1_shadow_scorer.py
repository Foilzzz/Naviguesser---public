"""f1_shadow_scorer — SHADOW scoring of pinned F1 guidance objects. v0.

DECLARATION — fixed before any measurement, per project discipline. If any
clause here changes after the first row is computed, the change is an
amendment with a version chain, never an edit.

1. QUANTITIES. The pinned ones from F1_FORWARD_GUIDANCE_TRIAL_PREREG v0.5
   §7.3, and only those: per closed window, realised margin (preferred minus
   current, C_X·v²-weighted exposure-hours, both corridors through the
   realised wind field), realised ranking under the pinned tie band
   (M0/4 = 27, classify_ranking reused by import), ranking-correct ⇔ realised
   ranking equals the emitted ranking; margin skill = |predicted − realised|
   and sign agreement. NOTHING ELSE is computed: no hit rate, no Brier — the
   scorer-v0 §3 tolerance is an ⟦INTEGRATION⟧ blank, and nobody may compute a
   hit until CC pins it.
2. STATUS OF ROWS. Every row is a SHADOW measurement. The trial's
   verdict-bearing scoring uses ERA5 (§7.1/§7.3) at the ≥ 6-day cadence; this
   instrument's realised field is the shortest-staged-lead GEFS proxy from
   accrual/f1_wind, digest-verified per member by the emitter's own
   _load_wind. Shadow rows exist to exercise the scoring path and to ground
   CC's F1_SCORER draft; they enter no verdict.
3. THE PIN IS THE CLAIM. predicted_margin and ranking are read from the
   register pin, never recomputed.
4. SYMMETRY. Realised costing reuses corpus_intake/f1_daily_guidance.py by
   import (C_X tables with the θ=0 gate, interpolation, constants, ranking
   classifier). Predicted and realised margins differ ONLY in the wind field
   and the current corridor's track — nothing else may differ.
5. CURRENT CORRIDOR (realised): the vessel's sailed track from the C1 shards
   (§6's verification clause). Sub-rules, shadow-declared, never tuned:
   S1 a window bin is track-covered ⇔ fixes bracket its midpoint within
      2.0 h on both sides, fixes ≥ 10 min apart;
   S2 the ship vector is the bracketing-fix DISPLACEMENT (not the quantised
      SOG/COG fields); position linear between the fixes.
6. PREFERRED CORRIDOR (realised): the pinned payload re-costed bin-by-bin
   under the realised proxy — same rhumb rule, same box (the origin's box,
   as at generation), no re-optimisation.
7. PAIRED MASK: bins where both realised corridors have wind AND the track
   bin is covered; margin = paired mean × 72/covered (the emitter's declared
   scaling). Zero paired bins, or a proxy lead absent for the whole window,
   or a missing corridor payload → UNSCORABLE with the cause named. Rows are
   never dropped.
8. WINDOWS: pins with window_close ≤ run time are scored and marked
   SHADOW-PREVIEW. §7.1's 6-day rule exists for ERA5 lag and does not gate
   this proxy instrument; the official path keeps its cadence.
9. The drill's identity case is the load-bearing guard: identical wind and
   identical track must reproduce the pinned margin to rounding. Any
   deviation is a reconstruction bug, and it stops the run.

Usage:
  python analysis/f1_shadow_scorer.py --drill
  python analysis/f1_shadow_scorer.py
"""
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "corpus_intake"))

import f1_daily_guidance as f1  # the emitter — reused, never reimplemented

REGISTER = ROOT / "accrual" / "f1" / "register.jsonl"
SHARD_DIR = Path(r"D:\naviguesser\aisstream")
GEFS_ROOT = ROOT / "accrual" / "f1_wind"
CFG_PATH = ROOT / "corpus_intake" / "f1_integration.json"
BOXES_PATH = ROOT / "accrual" / "declared_boxes.json"
OUT_JSON = ROOT / "corpus_intake" / "F1_SHADOW_SCORE_v0_1_20260907.json"
OUT_MD = ROOT / "corpus_intake" / "F1_SHADOW_SCORE_v0_1_20260907.md"

TRACK_BRACKET_H = 2.0     # S1 — shadow-declared
TRACK_MIN_FIX_GAP_MIN = 10.0  # S1

DECLARATION = (__doc__.split("Usage:")[0]).strip()


# ---------------------------------------------------------------- wind
class ProxyWind:
    """Shortest-staged-lead realised-proxy field for one box.

    Per (lat, lon, t): every staged cycle whose manifest+member verify and
    whose lead range brackets t is a candidate; the SMALLEST lead wins
    (declared — not the freshest cycle, the shortest horizon). Loads are
    digest-verified by the emitter's _load_wind and cached."""

    def __init__(self, gefs_root, box):
        self.box = box
        self.cycles = {}
        root = Path(gefs_root)
        for cdir in sorted(root.iterdir()) if root.is_dir() else []:
            if not (cdir / "manifest.json").is_file():
                continue
            try:
                ct = datetime.strptime(cdir.name, "%Y-%m-%dT%H").replace(
                    tzinfo=timezone.utc)
            except ValueError:
                continue
            self.cycles[cdir.name] = (ct, f1._load_wind(root, cdir.name, box))

    def at(self, lat, lon, t):
        best = None
        for cyc, (ct, ext) in self.cycles.items():
            lead = (t - ct).total_seconds() / 3600.0
            if lead < ext["leads_h"][0] or lead > ext["leads_h"][-1]:
                continue
            w = f1._wind_at(ext, lat, lon, lead)
            if w is None:
                continue
            if best is None or lead < best[2]:
                best = (w[0], w[1], lead, cyc)
        return best  # (u, v, lead_used, cycle_id) or None


# ---------------------------------------------------------------- tracks
def collect_fixes(shard_dir, mmsis, since, until):
    """One pass over the shards; {mmsi: [(ts, lat, lon)]} sorted."""
    fixes = defaultdict(list)
    for rec in f1.iter_shard_records(shard_dir, since, until):
        ev = f1.extract_vessel(rec)
        if not ev:
            continue
        mmsi, ts, lat, lon, sog, cog, vt = ev
        if mmsi in mmsis and lat is not None and lon is not None \
                and since <= ts <= until:
            fixes[mmsi].append((ts, float(lat), float(lon)))
    for m in fixes:
        fixes[m].sort()
    return fixes


def track_bin(track, t_mid):
    """(lat, lon, v_east, v_north) at t_mid from the sailed track, or None.
    S1/S2: bracketing fixes within TRACK_BRACKET_H, ≥ TRACK_MIN_FIX_GAP_MIN
    apart; ship vector from displacement.
    Bracket selection: nxt is the first fix after t_mid; prev is the LATEST
    fix ≤ t_mid that still satisfies the separation — adjacent-fix selection
    would let a dense burst (fixes seconds apart) fail the separation rule
    and void a well-observed bin, which is the defect drill case D added."""
    import bisect
    times = [f[0] for f in track]
    j = bisect.bisect_right(times, t_mid)
    if j == 0 or j == len(track):
        return None
    nxt = track[j]
    if (nxt[0] - t_mid).total_seconds() > TRACK_BRACKET_H * 3600:
        return None
    prev = None
    for i in range(j - 1, -1, -1):
        cand = track[i]
        if (t_mid - cand[0]).total_seconds() > TRACK_BRACKET_H * 3600:
            break
        if (nxt[0] - cand[0]).total_seconds() >= TRACK_MIN_FIX_GAP_MIN * 60:
            prev = cand
            break
    if prev is None:
        return None
    dt = (nxt[0] - prev[0]).total_seconds()
    frac = (t_mid - prev[0]).total_seconds() / dt
    lat = prev[1] + frac * (nxt[1] - prev[1])
    dlat = nxt[1] - prev[1]
    dlon = (nxt[2] - prev[2]) * math.cos(math.radians((prev[1] + nxt[1]) / 2))
    dist_m = math.hypot(dlat, dlon) * 60 * 1852.0 / 1.0  # deg-min → m
    v = dist_m / dt
    ve = v * (dlon / math.hypot(dlat, dlon)) if (dlat or dlon) else 0.0
    vn = v * (dlat / math.hypot(dlat, dlon)) if (dlat or dlon) else 0.0
    lon = prev[2] + frac * (nxt[2] - prev[2])
    return lat, lon, ve, vn


def corridor_bin(origin, cog_deg, sog_kt, t_mid):
    """Pinned-rule rhumb extrapolation — the emitter's formula, mirrored."""
    fix_ts = f1.parse_ts(origin["fix_utc"])
    dh = (t_mid - fix_ts).total_seconds() / 3600.0
    hdg = math.radians(cog_deg)
    lat = origin["lat"] + (sog_kt * dh) * math.cos(hdg) / 60.0
    lon = origin["lon"] + (sog_kt * dh) * math.sin(hdg) / \
        (60.0 * math.cos(math.radians(lat)))
    v = sog_kt * f1.KN_MS
    return lat, lon, v * math.sin(hdg), v * math.cos(hdg)


def cost_bin(wind, ship_ve, ship_vn, hdg_deg, angles, cxvals):
    """C_X(θ_rel)·v_rel² for one bin — the emitter's formula, mirrored."""
    awe, awn = wind[0] - ship_ve, wind[1] - ship_vn
    v_rel = math.hypot(awe, awn)
    to_deg = math.degrees(math.atan2(awe, awn)) % 360.0
    theta = abs(f1._wrap180((to_deg + 180.0) % 360.0 - hdg_deg))
    return f1._interp_cx(angles, cxvals, theta) * v_rel * v_rel


# ---------------------------------------------------------------- scoring
def score_pin(pin, cfg, boxes_cfg, gefs_root, fixes, now):
    """One register pin → one row. Never raises on data; UNSCORABLE carries
    the cause. Refusal-class exceptions (digest failure) DO propagate —
    those are stops, not rows."""
    g = pin["guidance"]
    row = {"guidance_id": g["guidance_id"][:12], "mmsi": g["mmsi"],
           "issued_utc": g["issued_utc"],
           "window_open": g["window_open"], "window_close": g["window_close"],
           "confidence": g["confidence"], "ranking_emitted": g["ranking"],
           "predicted_margin": g["predicted_margin"],
           "status": "SCORED", "cause": None}
    wo = f1.parse_ts(g["window_open"])
    tables = f1._load_cx_tables(cfg)
    angles, cxvals = tables[g["corridor_current"]["curve"]]
    box = f1._box_of(g["corridor_current"]["origin"]["lat"],
                     g["corridor_current"]["origin"]["lon"], boxes_cfg)
    wind = ProxyWind(gefs_root, box)
    track = fixes.get(g["mmsi"], [])

    cur = g["corridor_current"]
    pref = g["corridor_preferred"]
    pref_off = float(pref.get("heading_offset_deg", 0.0))
    pref_hdg = (pref["cog_deg"] + pref_off) % 360.0

    cur_vals, pref_vals, leads_used = [], [], []
    for k in range(int(f1.WINDOW_H)):
        t_mid = wo + timedelta(hours=k + 0.5)
        tb = track_bin(track, t_mid)
        if tb is None:
            continue
        hdg_c = math.degrees(math.atan2(tb[2], tb[3])) % 360.0
        wc = wind.at(tb[0], tb[1], t_mid)
        pb = corridor_bin(pref["origin"], pref_hdg, pref["sog_kt"], t_mid)
        wp = wind.at(pb[0], pb[1], t_mid)
        if wc is None or wp is None:
            continue
        cur_vals.append(cost_bin(wc, tb[2], tb[3], hdg_c, angles, cxvals))
        pref_vals.append(cost_bin(wp, pb[2], pb[3], pref_hdg,
                                  angles, cxvals))
        leads_used.append(wc[2])
    n = len(cur_vals)
    row["bins_paired"] = n
    row["multiplier"] = round(f1.WINDOW_H / n, 2) if n else None
    if n == 0:
        row["status"] = "UNSCORABLE"
        row["cause"] = ("no window bin with track coverage and realised "
                        "wind on both corridors (AIS gap or proxy coverage)")
        return row
    scale = f1.WINDOW_H / n        # emitter's declared paired-mean, 72-bin scaled
    realised = (sum(pref_vals) - sum(cur_vals)) * scale
    row["realised_margin"] = round(realised, 6)
    row["ranking_realised"] = f1.classify_ranking(realised)
    row["ranking_correct"] = row["ranking_realised"] == row["ranking_emitted"]
    row["abs_error"] = abs(realised - g["predicted_margin"])
    row["sign_agree"] = ((realised > 0) == (g["predicted_margin"] > 0))
    row["proxy_lead_min_h"] = round(min(leads_used), 1)
    row["proxy_lead_max_h"] = round(max(leads_used), 1)
    row["proxy_lead_mean_h"] = round(sum(leads_used) / n, 1)
    return row


# ---------------------------------------------------------------- drill
def drill():
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="f1scorer_drill_"))
    try:
        # --- synthetic wind: one cycle, constant u=8 m/s from the north
        # (u=0, v=-8 everywhere) at every lead; box covers the corridor.
        gefs = tmp / "gefs"
        cyc = gefs / "2026-09-01T00"
        cyc.mkdir(parents=True)
        lats = [20.0 + i for i in range(21)]
        lons = [-121.0 + i for i in range(12)]
        leads = list(range(6, 126, 6))
        fld = [[[-8.0] * 12 for _ in range(21)] for _ in leads]
        box = {"box_index": 0, "centre": [30.0, -115.0],
               "grid_step_deg": 1.0,
               "half_width_deg": {"lat": 10, "lon": 6},
               "lats": lats, "lons": lons, "leads_h": leads,
               "u10_ms": [[[0.0] * 12 for _ in range(21)] for _ in leads],
               "v10_ms": fld, "schema": "drill", "source_cycle": "x"}
        raw = json.dumps(box).encode()
        (cyc / "wind_box_0.json").write_bytes(raw)
        man = {"files": [{"path": "wind_box_0.json",
                          "sha256": hashlib.sha256(raw).hexdigest(),
                          "bytes": len(raw)}]}
        (cyc / "manifest.json").write_text(json.dumps(man), encoding="utf-8")

        cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
        boxes_cfg = {"boxes": [[[20.0, -121.0], [40.0, -109.0]]]}

        issued = datetime(2026, 9, 1, 16, 30, tzinfo=timezone.utc)
        wo = issued + timedelta(hours=1)
        fix_t = issued - timedelta(minutes=20)
        origin = {"lat": 34.5, "lon": -115.5,
                  "fix_utc": fix_t.isoformat().replace("+00:00", "Z")}
        # vessel sails due south at 10 kt: head wind (wind FROM north),
        # so the current corridor is the HIGH-exposure one; +10° offset
        # barely changes theta → predicted margin small negative; the
        # identity case needs track == current extrapolation exactly.
        sog, cog = 10.0, 180.0
        corridor = {"rule": "const_cog_sog_rhumb_1h_midpoint",
                    "origin": origin, "cog_deg": cog, "sog_kt": sog,
                    "curve": "cargo_vessel|laden", "bins_covered": 72}
        tables = f1._load_cx_tables(cfg)
        angles, cxvals = tables["cargo_vessel|laden"]

        # predicted margin computed with the emitter-mirrored math on the
        # SAME field: identity requires realised == predicted.
        cur_v, pref_v = [], []
        wind = ProxyWind(gefs, 0)
        for k in range(int(f1.WINDOW_H)):
            t_mid = wo + timedelta(hours=k + 0.5)
            la, lo, ve, vn = corridor_bin(origin, cog, sog, t_mid)
            w = wind.at(la, lo, t_mid)
            cur_v.append(cost_bin(w, ve, vn, cog, angles, cxvals))
            la2, lo2, ve2, vn2 = corridor_bin(origin, 190.0, sog, t_mid)
            w2 = wind.at(la2, lo2, t_mid)
            pref_v.append(cost_bin(w2, ve2, vn2, 190.0, angles, cxvals))
        predicted = sum(pref_v) - sum(cur_v)
        pin = {"guidance": {
            "guidance_id": "drill" + "0" * 60, "mmsi": "000000001",
            "vessel_type": 75, "issued_utc": issued.isoformat()
            .replace("+00:00", "Z"),
            "window_open": wo.isoformat().replace("+00:00", "Z"),
            "window_close": (wo + timedelta(hours=72)).isoformat()
            .replace("+00:00", "Z"),
            "cycle_id": "2026-09-01T00",
            "corridor_current": corridor,
            "corridor_preferred": dict(corridor, heading_offset_deg=10),
            "predicted_margin": predicted,
            "ranking": f1.classify_ranking(predicted),
            "confidence": "LOW", "integrity": {}}}

        # synthetic track = the current corridor exactly (fixes hourly)
        fixes = {"000000001": []}
        for h in range(-1, 80):
            t = fix_t + timedelta(hours=h)
            dh = h
            lat = origin["lat"] + (sog * dh) * math.cos(
                math.radians(cog)) / 60.0
            lon = origin["lon"]
            fixes["000000001"].append((t, lat, lon))

        fails = []
        row = score_pin(pin, cfg, boxes_cfg, gefs, fixes, None)
        if row["status"] != "SCORED":
            fails.append(f"identity UNSCORABLE: {row['cause']}")
        else:
            # Identity tolerance, declared: the realised path derives the
            # ship vector from bracketing-fix DISPLACEMENT (S2) while the
            # generation path uses the analytic SOG·KN_MS vector — the
            # residue is the KN_MS truncation plus latitude scaling, order
            # 1e-5 relative. The tolerance (1e-3 relative + 0.05 abs, i.e.
            # 0.05% of M0 and 540x below the tie band) separates numerical
            # noise from formula errors, which arrive as factors (the 72x
            # scaling bug this drill caught first) or sign flips.
            if abs(row["realised_margin"] - predicted) > max(
                    0.05, abs(predicted) * 1e-3):
                fails.append("identity: realised margin "
                             f"{row['realised_margin']} != predicted "
                             f"{predicted} — reconstruction bug")
            if not row["ranking_correct"]:
                fails.append("identity: ranking mismatch on identical field")
            if row["bins_paired"] != 72:
                fails.append(f"identity: {row['bins_paired']}/72 bins paired")

        # B) rotated wind (wind FROM the south: v=+8) must flip the cost of
        # the southbound track to LOW exposure → realised margin changes
        raw2 = json.dumps(dict(box, u10_ms=box["u10_ms"],
                               v10_ms=[[[8.0] * 12 for _ in range(21)]
                                       for _ in leads])).encode()
        cyc2 = gefs / "2026-09-02T00"
        cyc2.mkdir(parents=True)
        (cyc2 / "wind_box_0.json").write_bytes(raw2)
        (cyc2 / "manifest.json").write_text(json.dumps({"files": [
            {"path": "wind_box_0.json",
             "sha256": hashlib.sha256(raw2).hexdigest(),
             "bytes": len(raw2)}]}), encoding="utf-8")
        # provider now sees both cycles; shortest-lead rule keeps cycle 1
        # for most of the window — so instead verify the proxy-LEAD rule:
        w_a = ProxyWind(gefs, 0)
        t_probe = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
        got = w_a.at(34.5, -115.5, t_probe)
        if not got or got[3] != "2026-09-02T00" or abs(got[2] - 12.0) > 1e-6:
            fails.append(f"proxy did not pick the shortest lead: {got}")

        # C) no fixes → UNSCORABLE, row present, cause names coverage
        row_c = score_pin(pin, cfg, boxes_cfg, gefs, {"000000001": []}, None)
        if row_c["status"] != "UNSCORABLE" or not row_c["cause"]:
            fails.append("empty track did not surface as UNSCORABLE")

        # D) dense-burst bracketing: fixes every 20 s for one hour around a
        # bin midpoint must COVER the bin. Adjacent-fix selection fails the
        # 10-minute separation rule and voids a well-observed bin — the
        # defect the burst vessels (…7170: 77 fixes, 0 paired bins) exposed.
        burst0 = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
        dense = []
        for s in range(0, 3600, 20):
            t = burst0 + timedelta(seconds=s)
            dh = s / 3600.0
            dense.append((t, origin["lat"] - (sog * dh) / 60.0,
                          origin["lon"]))
        mid = burst0 + timedelta(minutes=30)
        got = track_bin(dense, mid)
        if got is None:
            fails.append("D dense burst: midpoint not covered — "
                         "bracket selection still adjacent-fix")
        elif abs(got[3] + sog * f1.KN_MS) > 0.05:
            fails.append(f"D dense burst: derived northward speed "
                         f"{got[3]:.3f} != {-sog * f1.KN_MS:.3f}")

        for f_ in fails:
            print("  FAIL:", f_)
        print("F1-SCORER-DRILL", "RED" if fails else "all 4 green",
              "(identity / shortest-lead / unscorable / dense-burst)")
        return 1 if fails else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- main
def main():
    if "--drill" in sys.argv:
        return drill()
    now = datetime.now(timezone.utc)
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    boxes_cfg = json.loads(BOXES_PATH.read_text(encoding="utf-8"))
    pins, gaps_seen = [], 0
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "guidance" in obj:
            pins.append(obj)
        else:
            gaps_seen += 1
    closed = [p for p in pins
              if f1.parse_ts(p["guidance"]["window_close"]) <= now]
    print(f"register: {len(pins)} pins, {gaps_seen} declared gap rows; "
          f"{len(closed)} windows closed at {now.isoformat(timespec='seconds')}")

    if closed:
        mmsis = {p["guidance"]["mmsi"] for p in closed}
        since = min(f1.parse_ts(p["guidance"]["window_open"]) for p in closed)
        until = max(f1.parse_ts(p["guidance"]["window_close"]) for p in closed)
        print(f"single shard pass over {len(mmsis)} watched vessels, "
              f"{since.date()} → {until.date()} …")
        fixes = collect_fixes(SHARD_DIR, mmsis, since, until)
        for m in sorted(mmsis):
            print(f"  mmsi …{m[-4:]}: {len(fixes.get(m, []))} fixes")

    rows = []
    for p in closed:
        try:
            rows.append(score_pin(p, cfg, boxes_cfg, GEFS_ROOT, fixes, now))
        except f1.Refuse as e:
            print(f"STOP (refusal, not a row): {e}")
            return 2
        r = rows[-1]
        if r["status"] == "SCORED":
            print(f"  {r['guidance_id']} {r['window_open'][:10]} "
                  f"{r['confidence']:>8} emitted {r['ranking_emitted']:>16} "
                  f"realised {r['ranking_realised']:>16} "
                  f"{'OK ' if r['ranking_correct'] else 'MIS'}"
                  f" pred {r['predicted_margin']:>10.1f} "
                  f"real {r['realised_margin']:>10.1f} "
                  f"bins {r['bins_paired']:>2} "
                  f"proxy {r['proxy_lead_min_h']}-{r['proxy_lead_max_h']}h")
        else:
            print(f"  {r['guidance_id']} {r['window_open'][:10]} "
                  f"UNSCORABLE — {r['cause']}")

    scored = [r for r in rows if r["status"] == "SCORED"]
    out = {"scorer": "F1 shadow scorer v0 — SHADOW rows, never verdicts",
           "built_utc": now.isoformat(timespec="seconds"),
           "declaration": DECLARATION,
           "register": {"path": str(REGISTER), "pins": len(pins),
                        "declared_gap_rows": gaps_seen,
                        "windows_closed_at_run": len(closed)},
           "rows": rows,
           "summary": {
               "scored": len(scored),
               "unscorable": len(rows) - len(scored),
               "ranking_correct": sum(1 for r in scored
                                      if r["ranking_correct"]),
               "rows_per_vessel": {m[-4:]: sum(
                   1 for r in scored if r["mmsi"].endswith(m[-4:]))
                   for m in sorted({r["mmsi"] for r in scored})},
               "margin_skill_median_abs_error": (
                   sorted(r["abs_error"] for r in scored)
                   [len(scored) // 2] if scored else None)}}
    # v0.1: pooled sign_agreement removed from the summary — on this sample
    # it is identical to ranking_correct on every row (CC verification), so
    # pooling both double-counts one bit. The per-row field stays in the JSON.
    OUT_JSON.write_text(json.dumps(out, indent=1), encoding="utf-8")

    mh = lambda m: hashlib.sha256(str(m).encode()).hexdigest()[:8]
    md = ["# F1 shadow score v0.1 — SHADOW-PREVIEW rows (GEFS proxy field)",
          "", "**These are shadow measurements, not the trial's scored "
          "rows.** The verdict-bearing path is §7.3 on ERA5 at the ≥ 6-day "
          "cadence. No hit rate and no Brier appear here: the scorer-v0 §3 "
          "tolerance is unpinned, and nobody may compute a hit until it is "
          "pinned.", "", f"Register: {len(pins)} pins, {gaps_seen} declared "
          f"gap rows, {len(closed)} windows closed at run.", "",
          "| window | vessel | class | emitted | realised | correct | "
          "pred margin | realised margin | bins | proxy leads (h) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["status"] == "SCORED":
            md.append(f"| {r['window_open'][:10]} | …{r['mmsi'][-4:]} "
                      f"| {r['confidence']} | {r['ranking_emitted']} "
                      f"| {r['ranking_realised']} "
                      f"| {'✓' if r['ranking_correct'] else '✗'} "
                      f"| {r['predicted_margin']:.1f} "
                      f"| {r['realised_margin']:.1f} | {r['bins_paired']} "
                      f"| ×{r['multiplier']} "
                      f"| {r['proxy_lead_min_h']}–{r['proxy_lead_max_h']} |")
        else:
            md.append(f"| {r['window_open'][:10]} | …{r['mmsi'][-4:]} "
                      f"| {r['confidence']} | {r['ranking_emitted']} | — | "
                      f"UNSCORABLE | {r['predicted_margin']:.1f} | — | 0 | — |")
    rpv = out["summary"]["rows_per_vessel"]
    md += ["", f"Scored {len(scored)} of {len(rows)} closed windows; "
           f"ranking correct in {out['summary']['ranking_correct']}. "
           f"**Rows per vessel: {rpv}** — the denominator is hulls, not "
           "windows; overlapping windows on one hull share track, field "
           "and synoptic state (CC verification 2026-09-07). ×mult is "
           "72/bins_paired — the extrapolation factor on the margin; no "
           "floor exists in the pinned text, flagged for pinning as a "
           "multiplier bound. No verdict attached."]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"artifacts: {OUT_JSON.name} ({OUT_JSON.stat().st_size} B), "
          f"{OUT_MD.name} ({OUT_MD.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

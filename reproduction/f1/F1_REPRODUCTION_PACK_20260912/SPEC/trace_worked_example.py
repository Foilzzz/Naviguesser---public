#!/usr/bin/env python3
"""trace_worked_example.py — regenerate SPEC/WORKED_EXAMPLE.md from pack bytes.

Zero dependencies (stdlib only). Recomputes ONE register entry's corridors and
predicted margin from the bytes in this pack — the pinned emitter (SCORER/),
the digest-verified wind extract (WIND/), the pinned C_X artefact (POLAR/) —
and checks the recomputed margin equals the recorded one. If it does not, the
trace is a finding, and it prints that rather than a worked example.

The bin loop below mirrors compute_corridors.step_values in the pinned emitter
(SCORER/f1_daily_guidance.py) deliberately: the margin check is what proves
the mirror has not drifted from the rule.

Usage: python trace_worked_example.py [--index N]   (default: the last entry)
"""
import argparse
import importlib.util
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_emitter():
    spec = importlib.util.spec_from_file_location(
        "f1_emitter", ROOT / "SCORER" / "f1_daily_guidance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=int, default=-1)
    args = ap.parse_args()
    f1 = load_emitter()

    lines = [l for l in (ROOT / "RECORD" / "register.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
    entry = json.loads(lines[args.index])
    g = entry["guidance"]

    # 0. object integrity under the chain rule (SPEC/CHAIN_RULE.md)
    body = {k: v for k, v in g.items() if k != "sha256"}
    obj_ok = g["sha256"] == f1.sha(f1.canon(body))

    # 1. recorded inputs
    cur = g["corridor_current"]
    pref_off = g["corridor_preferred"].get("heading_offset_deg", 0)
    flat0, flon0 = cur["origin"]["lat"], cur["origin"]["lon"]
    fix_ts, sog, cog = ts(cur["origin"]["fix_utc"]), cur["sog_kt"], cur["cog_deg"]
    now = ts(g["issued_utc"])
    cycle_id, curve_key = g["cycle_id"], cur["curve"]

    # 2. box + digest-verified wind + digest-verified C_X tables
    boxes = json.loads((ROOT / "RECORD" / "declared_boxes.json").read_text(encoding="utf-8"))
    box = f1._box_of(flat0, flon0, boxes)
    extract = f1._load_wind(ROOT / "WIND" / "f1_wind", cycle_id, box)
    cfg = json.loads((ROOT / "RECORD" / "f1_integration.json").read_text(encoding="utf-8"))
    tables = f1._load_cx_tables({"model_path": str(ROOT / "POLAR" /
                                 "parametric_reference_declared.json"),
                                 "model_sha256": cfg["model_sha256"]})
    angles, cxvals = tables[curve_key]
    settings = json.loads((ROOT / "POLAR" / "f1_optimizer_settings.json").read_text(encoding="utf-8"))
    offsets = settings["candidate_family"]["heading_offsets_deg"]

    # 3. per-bin trace (mirrors step_values; the margin check proves it)
    KN_MS = 0.514444
    cycle_time = datetime.strptime(cycle_id, "%Y-%m-%dT%H").replace(tzinfo=timezone.utc)

    def step_values(offset):
        hdg = (cog + offset) % 360.0
        ve = sog * KN_MS * math.sin(math.radians(hdg))
        vn = sog * KN_MS * math.cos(math.radians(hdg))
        out = []
        for k in range(int(f1.WINDOW_H)):
            t_mid = now + timedelta(hours=f1.WINDOW_OPEN_LAG_H + k + 0.5)
            dh = (t_mid - fix_ts).total_seconds() / 3600.0
            latk = flat0 + (sog * dh) * math.cos(math.radians(hdg)) / 60.0
            lonk = flon0 + (sog * dh) * math.sin(math.radians(hdg)) / (60.0 * math.cos(math.radians(latk)))
            lead = (t_mid - cycle_time).total_seconds() / 3600.0
            wind = f1._wind_at(extract, latk, lonk, lead)
            if wind is None:
                out.append(None)
                continue
            awe, awn = wind[0] - ve, wind[1] - vn
            v_rel = math.hypot(awe, awn)
            to_deg = math.degrees(math.atan2(awe, awn)) % 360.0
            theta = abs(f1._wrap180((to_deg + 180.0) % 360.0 - hdg))
            out.append({"k": k, "t_mid": t_mid.isoformat(), "lat": round(latk, 6),
                        "lon": round(lonk, 6), "lead_h": round(lead, 3),
                        "wind_u": wind[0], "wind_v": wind[1], "v_rel": v_rel,
                        "theta_deg": theta, "cx": f1._interp_cx(angles, cxvals, theta)})
        return out

    per = {o: step_values(o) for o in offsets}
    paired = [k for k in range(int(f1.WINDOW_H)) if all(per[o][k] is not None for o in offsets)]
    scale = float(f1.WINDOW_H) / len(paired)

    def binval(o, k):  # C_X·v_rel² for offset o, bin k
        b = per[o][k]
        return b["cx"] * b["v_rel"] ** 2
    means = {o: sum(binval(o, k) for k in paired) * scale for o in offsets}
    pref_recomputed = min(offsets, key=lambda o: (means[o], abs(o), o))
    margin = means[pref_recomputed] - means[0]
    margin_ok = (round(margin, 6) == g["predicted_margin"] and pref_recomputed == pref_off)

    # 4. report
    w = []
    w.append("# WORKED EXAMPLE — one F1 guidance object, end to end (GENERATED by")
    w.append("# SPEC/trace_worked_example.py from pack bytes; never transcribed)")
    w.append("")
    w.append(f"Entry index {args.index if args.index >= 0 else len(lines) + args.index} "
             f"of RECORD/register.jsonl — guidance_id `{g['guidance_id'][:16]}…`")
    w.append(f"object sha256 under the chain rule: {'MATCHES' if obj_ok else 'MISMATCH — FINDING'}")
    w.append("")
    w.append("## Recorded inputs (all from the register entry)")
    w.append(f"- issued_utc {g['issued_utc']} · cycle {cycle_id} · mmsi {g['mmsi']} "
             f"(vessel_type {g['vessel_type']} → curve `{curve_key}`)")
    w.append(f"- origin fix {flat0}, {flon0} at {cur['origin']['fix_utc']} · "
             f"COG {cog}° · SOG {sog} kt · box {box}")
    w.append(f"- window {g['window_open']} → {g['window_close']} (72 h, opens 1 h after emission)")
    w.append(f"- recorded: predicted_margin {g['predicted_margin']} · ranking {g['ranking']} · "
             f"confidence {g['confidence']} · bins_covered {cur['bins_covered']}")
    w.append("")
    w.append("## Recomputation")
    w.append(f"- paired bins (covered by EVERY candidate offset): {len(paired)} of 72; "
             f"declared scale 72/{len(paired)} = {scale:.6f}")
    w.append(f"- candidate family offsets: {offsets}")
    w.append(f"- argmin recomputed: {pref_recomputed} (recorded {pref_off}) — "
             f"{'match' if pref_recomputed == pref_off else 'MISMATCH — FINDING'}")
    w.append(f"- exposure, current corridor (offset 0): {means[0]:.6f} C_X·v²·h")
    w.append(f"- exposure, preferred corridor (offset {pref_recomputed}): {means[pref_recomputed]:.6f}")
    w.append(f"- margin = preferred − current = {margin:.6f} → recorded {g['predicted_margin']} — "
             f"{'EXACT MATCH' if margin_ok else 'MISMATCH — FINDING'}")
    w.append("")
    w.append("## The first three paired bins, every intermediate")
    w.append("| bin k | t_mid | lat | lon | lead h | wind u,v (m/s) | v_rel | θ° | C_X | C_X·v² |")
    w.append("|---|---|---|---|---|---|---|---|---|---|")
    for k in paired[:3]:
        b = per[0][k]
        w.append(f"| {k} | {b['t_mid']} | {b['lat']} | {b['lon']} | {b['lead_h']} | "
                 f"{b['wind_u']:.3f}, {b['wind_v']:.3f} | {b['v_rel']:.3f} | "
                 f"{b['theta_deg']:.1f} | {b['cx']:.4f} | {binval(0, k):.3f} |")
    w.append("")
    w.append("Reading: positions extrapolate the recorded fix at constant COG/SOG "
             "(rhumb, 1 h bins at midpoints); wind is nearest-grid-in-space, "
             "linear-in-time from the digest-verified cycle extract; v_rel is the "
             "apparent wind against the ship vector; θ is the relative angle with "
             "head wind 0°; C_X is linear interpolation of the pinned angular table; "
             "the margin is the paired-mean difference scaled to 72 bins. The current "
             "corridor is a member of the candidate family, so margin ≤ 0 structurally.")
    out = ROOT / "SPEC" / "WORKED_EXAMPLE.md"
    out.write_text("\n".join(w) + "\n", encoding="utf-8")
    print("\n".join(w[:24]))
    print(f"... wrote {out}")
    if not (obj_ok and margin_ok):
        print("FINDING: trace does not reproduce the recorded object — investigate, never edit")
        return 1
    print("TRACE VERIFIED — recomputed margin equals the recorded predicted_margin exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

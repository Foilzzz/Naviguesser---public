#!/usr/bin/env python3
"""F1 daily bounded guidance job — v1 (2026-08-29), A3-aligned, core landed.

Implements the integrity core AND, as of 2026-08-29 under owner directive
R2's 48 h clock, the corridor/margin numeric core of the F1 forward
(shadow) guidance trial, corpus_intake/F1_FORWARD_GUIDANCE_TRIAL_PREREG.md
(v0.3). Built BEFORE integration so the trial is never gated on this
machinery.

  MEASURED INPUT SCHEMA (2026-08-29, against the live C1 shards): records
  are FLATTENED — mmsi, time_utc, received_utc, lat, lon, sog_kt, cog_deg,
  heading_deg, nav_status, msg_type — and are POSITION REPORTS ONLY
  (PositionReport / StandardClassBPositionReport / ExtendedClassBPosition-
  Report; 259,694 records scanned, zero static messages). Integration
  finding F1-IF-1 measured that §2's VesselType 70-89 filter has no source
  in the C1 shards. UNDER AMENDMENT A3 (owner directive R2, 2026-08-29)
  F1-IF-1 IS RECLASSIFIED — unknown type is not a blocker, it is an
  integrity-state field: selection ADMITS type-unknown vessels, the
  guidance object carries vessel_type "UNKNOWN", and unknown type is
  exactly one degraded confidence dimension (§7.2) — REDUCED at best.
  The pinned mmsi->type map (populated forward by the watchlist feed's
  5/24 static capture) is an OPTIONAL, digest-verified input: present ->
  verified before selection; absent -> declared UNKNOWN mode. A dry run
  still marks provisional_type=1 and tallies type_unknown — selection on
  incomplete information is always marked, never silent.

  IMPLEMENTED AND DRILLED (recovery/drill_f1_daily.py):
    - the pin-before-window rule (§4): every guidance is hash-chain pinned
      into accrual/f1/register.jsonl BEFORE window_open; a late pin is
      recorded, flagged pin_valid_on_time=false, and counted — never
      deleted, never re-issued (§4, §10.1).
    - the hash chain: each entry carries sha256 of the previous raw line;
      verify_register() names the first broken link. Head digest is
      greppable (--head) for the weekly close-out quote (§4).
    - deterministic selection (§2, v0.3): VesselType 70-89 via the map,
      OR type UNKNOWN (A3, tallied), last fix SOG >= 7 kt in the previous
      24 h, K=5 by most recent fix, 21-day cap, 72-h no-position drop.
      The 70-89 filter binds every vessel whose type IS known — the map
      can only exclude a known non-cargo vessel, never admit one.
      Selection reads shards only — it never sees a computed figure (§2).
    - confidence classes (§7.2, v0.3: five dimensions — vessel-type-known
      is the fifth; UNKNOWN type = exactly one degradation) and ranking
      with the M0/4 tie band (§3/§7.3), M0 = 108 pinned (A4, 2026-08-29).
      INTERPRETATION, declared for integration review: coverage_ok counts
      as a dimension (good/degraded only); a margin below M0/2 counts as
      degraded. Where §7.2 is silent this file says what it does — a
      reader does not have to guess. MEASURED AT LANDING (2026-08-29): in
      the pinned margin units typical |predicted_margin| is O(10^2-10^3);
      the v0.3 M0 = 0.5 could not bind (INDIFFERENT only at exact float
      ties — the entry-35 shape), so A4 re-pinned M0 = 108 (ΔC_X 0.01 ×
      v_rel² 150 × 72 h, one-tenth of the typical scale) BEFORE first
      emission — prereg Amendment A4, REGISTER_DECLARATION.md §5.
    - GEFS cycle check (§5.2, A5 2026-08-30): the FRESHEST archived cycle
      whose manifest verifies AND whose extract leads cover the whole 72 h
      window at emission is consumed (bin midpoints need age+1.5..age+72.5 h
      inside every member's leads_h). A cycle failing verification is a
      refusal — never a silent substitute cycle; a non-covering cycle is
      SKIPPED to the next older (the declared A5 rule — the archiver's
      cycle hour is not stable, measured 2026-08-29); no covering cycle is
      a refusal, never the silent coverage_ok=False degradation. A5
      supersedes A4's plain freshest-verifies rule after CC measured that
      the 14-lead set covered ONLY a 06Z cycle (1.5 h margin) while the
      archiver had taken 00Z that morning.
    - preflight (emit): integration config present, every §11 blank pinned,
      model digest re-computed against bytes on disk BEFORE selection
      runs — a stale input is a build failure, not a warning; the type
      map, WHEN CONFIGURED (A3: optional), is digest-verified the same
      way; the selected GEFS cycle verifies and covers before anything is
      pinned; the optimizer settings and the A1 artefact's theta=0 load
      gate are re-verified run-level before any vessel is costed.
    - schema probe: parseable shard lines that yield NO position-bearing
      records are a refusal (format drift), never a silent empty ocean.
    - shadow mode (§9) is STRUCTURAL: this module imports no network
      library, and preflight scans its own source to prove it (the scan is
      drilled red-first, including against a mutated copy of this file).

  NUMERIC CORE — LANDED 2026-08-29 (supersedes the pre-staged stub, whose
  refusal property was drilled as D13/D14a and is discharged in the drill
  file's amendment record). compute_corridors() implements §6 exactly as
  declared in corpus_intake/f1_optimizer_settings.json (digest-pinned in
  the integration config): constant-COG/SOG rhumb-line extrapolation from
  the most recent fix, 72 one-hour bins sampled at bin midpoints, a
  declared candidate family of constant heading offsets (0, ±2.5..±10 deg,
  the current corridor a member so margin <= 0 is structural), apparent
  wind from the digest-verified wind extract (nearest grid point in space,
  linear in time, declared), exposure in C_X*v^2-weighted exposure-hours
  with the A1 artefact's declared linear C_X interpolation and the §5.3
  theta=0 gate re-asserted at every load. Coverage is PAIRED across the
  family (a bin counts only when every candidate covers it) so candidate
  exposures stay comparable; coverage_ok=False degrades confidence and is
  never silent. A watched vessel it cannot cost (no 24 h fix, no extract
  for its box) is a RECORDED GAP in accrual/f1/gaps.jsonl, never a silent
  skip and never a run failure; a systemic defect (settings/model/cycle
  digest) refuses the whole run before anything is pinned.

  INTEGRATION BLANKS (§11 v0.3 — emit refuses until pinned in
  corpus_intake/f1_integration.json): outbound-heading rule per box (§2 —
  a range OR list of ranges per box), corridor extrapolation rule (§3),
  A1 model path+digest (§5.3), optimizer settings path+digest (§6), GEFS
  retrieval declaration (§11), trial start date. The vessel-type source
  is NOT a blank (A3): vessel_types_path/vessel_types_sha256 are optional
  config keys, digest-verified when present.

Verdict lines (stable, greppable):
  F1-DRYRUN <date> selected=<n> watchlist=<n> provisional_heading=<0|1>
            provisional_type=<0|1> type_unknown=<n> drops=<n> [EMPTY_SELECTION]
  F1-EMIT <date> pinned=<n> late=<m> dup=<k> gaps=<g> head=<12-char>
  F1-REFUSED <reason...>
  F1-HEAD <64-char digest> verify=<detail>

Exit 0 = clean dry-run / emit; 2 = REFUSED (nothing written); 1 = error.
Empty selection is recorded as EMPTY_SELECTION — never silently counted as
coverage (§7.4(c) counts a pin per WATCHED vessel; an empty watchlist day
is a declared class, not a vacuous pass).
"""
import argparse, hashlib, json, math, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

M0 = 108.0               # §7.2 pinned, C_X·v^2-weighted exposure-hours (A4: ΔC_X 0.01 × v_rel² 150 × 72 h)
TIE_BAND = M0 / 4.0      # §7.3 (= 27 under A4)
K_WATCH = 5              # §2 bandwidth cap
MAX_WATCH_DAYS = 21      # §2
DROP_AFTER_H = 72.0      # §2
EMIT_HOUR = 16           # §4 daily 16:30 UTC (A4 — measured archiver behaviour)
EMIT_MINUTE = 30         # §4 daily 16:30 UTC (A4)
WINDOW_OPEN_LAG_H = 1.0  # §4 window opens 1 h after emission
WINDOW_H = 72.0          # §3
GENESIS = "0" * 64
KN_MS = 0.514444         # knots to m/s, declared constant

REGISTER = Path("accrual/f1/register.jsonl")
WATCHLIST = Path("accrual/f1/watchlist.json")
GAPS = Path("accrual/f1/gaps.jsonl")
CONFIG = Path("corpus_intake/f1_integration.json")
BOXES = Path("accrual/declared_boxes.json")

NETWORK_TOKENS = tuple("import " + n for n in
                       ("socket", "urllib", "requests", "http", "smtplib",
                        "ftplib", "websockets"))


class IntegrationBlank(Exception):
    """A §11 blank is unpinned or the numeric core is not staged. Loud."""


class Refuse(Exception):
    """Emit-mode refusal: named reason, nothing written."""


def parse_ts(s):
    if not s:
        return None
    s = str(s).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- §7.2/§7.3
def classify_confidence(forecast_age_h, fix_age_min, margin_abs, coverage_ok,
                        type_known=True):
    """§7.2 v0.3, physical dimensions first. FIVE dimensions: vessel-type-
    known is the fifth (A3) — UNKNOWN type is exactly one degradation, so
    an UNKNOWN-type emission is REDUCED at best. Declared interpretation
    where the section is silent: coverage_ok is a dimension (good/degraded);
    margin_abs < M0/2 is degraded. Boundaries are the pinned constants —
    never redrawn against an observed distribution."""
    if forecast_age_h is None or fix_age_min is None or margin_abs is None:
        return "LOW"  # a missing dimension cannot be better than LOW
    if forecast_age_h > 24.0 or fix_age_min > 120.0:
        return "LOW"
    degraded = 0
    if forecast_age_h > 12.0:
        degraded += 1
    if fix_age_min > 30.0:
        degraded += 1
    if margin_abs < M0:
        degraded += 1
    if not coverage_ok:
        degraded += 1
    if not type_known:
        degraded += 1
    if degraded == 0:
        return "HIGH"
    if degraded == 1:
        return "REDUCED"
    return "LOW"


def classify_ranking(predicted_margin):
    """§3 sign convention: preferred minus current; negative = preferred
    better. Tie band §7.3: |margin| <= M0/4 is INDIFFERENT (inclusive)."""
    if predicted_margin < -TIE_BAND:
        return "PREFERRED_BETTER"
    if predicted_margin > TIE_BAND:
        return "CURRENT_BETTER"
    return "INDIFFERENT"


# ------------------------------------------------------------------ §3
def build_guidance(mmsi, issued_utc, cycle_id, corridor_current,
                   corridor_preferred, predicted_margin, integrity,
                   vessel_type=None):
    """Assemble one §3 guidance object (v0.3: vessel_type field — integer
    70-89, or "UNKNOWN" when unset; the digest covers it like every other
    field, and UNKNOWN degrades confidence via §7.2's fifth dimension)."""
    issued = parse_ts(issued_utc)
    window_open = issued + timedelta(hours=WINDOW_OPEN_LAG_H)
    window_close = window_open + timedelta(hours=WINDOW_H)
    gid = sha(f"{mmsi}|{iso(window_open)}|{cycle_id}".encode("utf-8"))
    vt = int(vessel_type) if vessel_type is not None else "UNKNOWN"
    obj = {
        "guidance_id": gid,
        "mmsi": str(mmsi),
        "vessel_type": vt,
        "issued_utc": iso(issued),
        "window_open": iso(window_open),
        "window_close": iso(window_close),
        "cycle_id": str(cycle_id),
        "corridor_current": corridor_current,
        "corridor_preferred": corridor_preferred,
        "predicted_margin": float(predicted_margin),
        "ranking": classify_ranking(float(predicted_margin)),
        "confidence": classify_confidence(
            integrity.get("forecast_age_h"), integrity.get("ais_fix_age_min"),
            integrity.get("margin_abs"), integrity.get("coverage_ok", False),
            type_known=vessel_type is not None),
        "integrity": {
            "forecast_age_h": integrity.get("forecast_age_h"),
            "ais_fix_age_min": integrity.get("ais_fix_age_min"),
            "coverage_ok": bool(integrity.get("coverage_ok", False)),
            "margin_abs": integrity.get("margin_abs"),
        },
    }
    obj["sha256"] = sha(canon(obj))
    return obj


# ------------------------------------------------- §6 numeric core (landed)
def _wrap180(x):
    return (x + 180.0) % 360.0 - 180.0


def _load_settings(cfg):
    """The declared optimizer settings, digest-verified at load — a stale
    input is a build failure, not a warning (same discipline as §5.3)."""
    sp = cfg.get("optimizer_settings_path")
    if not sp:
        raise IntegrationBlank("optimizer_settings_path unpinned (§11)")
    p = Path(sp)
    if not p.exists() or sha(p.read_bytes()) != cfg.get("optimizer_settings_sha256"):
        raise Refuse(f"optimizer settings digest mismatch: {sp} — a stale "
                     "input is a build failure, not a warning")
    return json.loads(p.read_text(encoding="utf-8"))


def _load_cx_tables(cfg):
    """Angular C_X tables from the pinned A1 artefact, digest re-verified
    and the §5.3 theta=0 load gate re-asserted on EVERY load: each angular
    table's C_X(0) must equal its head-wind anchor, else the artefact is a
    transcription defect, not a modelling choice."""
    mp = Path(cfg["model_path"])
    if not mp.exists() or sha(mp.read_bytes()) != cfg["model_sha256"]:
        raise Refuse(f"model digest mismatch: {cfg['model_path']} — a stale "
                     "input is a build failure, not a warning")
    art = json.loads(mp.read_text(encoding="utf-8"))
    hw = art.get("windage_cx_headwind_by_type_loading") or {}
    tables = {}
    for k, v in (art.get("windage_cx_angular") or {}).items():
        if k == "metadata":
            continue
        angles, cx = v.get("angles_deg"), v.get("cx")
        if not (isinstance(angles, list) and isinstance(cx, list)
                and len(angles) == len(cx) and len(angles) >= 2):
            raise Refuse(f"A1 angular table {k!r} malformed — a sourcing "
                         "defect, not a modelling choice")
        anchor = (hw.get(k) or {}).get("value")
        if anchor is None or abs(cx[0] - anchor) > 1e-9:
            raise Refuse(f"A1 theta=0 gate FAILED for {k!r}: C_X(0)={cx[0]} "
                         f"disagrees with the head-wind anchor {anchor} (§5.3)")
        tables[k] = (angles, cx)
    if not tables:
        raise Refuse("A1 artefact carries no angular C_X tables — §5.3's "
                     "declared coverage is absent")
    return tables


def _interp_cx(angles, cx, theta):
    """Declared linear interpolation between tabulated points — the same
    rule the A1 artefact declares for itself."""
    if theta <= angles[0]:
        return cx[0]
    if theta >= angles[-1]:
        return cx[-1]
    for i in range(1, len(angles)):
        if theta <= angles[i]:
            frac = (theta - angles[i - 1]) / (angles[i] - angles[i - 1])
            return cx[i - 1] + frac * (cx[i] - cx[i - 1])
    return cx[-1]  # unreachable given the domain guard; kept explicit


def _latest_fix(shard_dir, mmsi, now):
    """The vessel's most recent position report in the previous 24 h — the
    corridor's origin. Its absence is a recorded gap, never a fabricated
    fix."""
    since = now - timedelta(hours=24)
    best = None
    for rec in iter_shard_records(shard_dir, since, now):
        got = extract_vessel(rec)
        if got is None:
            continue
        m, ts, lat, lon, sog, cog, _vt = got
        if m != str(mmsi) or lat is None or sog is None or cog is None:
            continue
        if not (since <= ts <= now):
            continue
        if best is None or ts > best[0]:
            best = (ts, float(lat), float(lon), float(sog), float(cog))
    if best is None:
        raise Refuse(f"no fix for {mmsi} in the previous 24 h — a corridor "
                     "cannot be extrapolated from nothing (the 72-h drop "
                     "rule's emission-side mirror)")
    return best


def _load_wind(gefs_root, cycle_id, box):
    """One box's wind extract for the cycle, member digest verified against
    the cycle manifest before a byte is trusted (§10.2's extract-side
    mirror). A mismatch is a refusal, never a substitute."""
    cdir = Path(gefs_root) / cycle_id
    man_p = cdir / "manifest.json"
    if not man_p.exists():
        raise Refuse(f"wind extract cycle dir has no manifest: {cdir}")
    try:
        man = json.loads(man_p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise Refuse(f"wind extract manifest unparseable: {man_p}")
    entries = man.get("files", man) if isinstance(man, dict) else man
    name = f"wind_box_{box}.json"
    rec = next((e for e in entries if e.get("path") == name), None)
    if rec is None:
        raise Refuse(f"wind extract manifest carries no {name} — the pack "
                     f"does not cover box {box}")
    fp = cdir / name
    if not fp.exists() or sha(fp.read_bytes()) != rec["sha256"]:
        raise Refuse(f"wind extract {name} FAILED digest verification — "
                     "stop, never substitute")
    return json.loads(fp.read_text(encoding="utf-8"))


def _wind_at(extract, lat, lon, lead_h):
    """(u10, v10) m/s at (lat, lon, lead): nearest grid point in space,
    linear between bracketing lead times — the declared interpolation.
    None outside spatial/temporal coverage (the caller's coverage flag,
    never an extrapolation). Member shape is the SHIPPED flat
    f1_wind_extract/0 (lats/lons top-level — A5 concordance 2026-08-30:
    the real pack's shape, measured, supersedes the nested draft text)."""
    lats, lons, leads = extract["lats"], extract["lons"], extract["leads_h"]
    if lat < lats[0] or lat > lats[-1] or lon < lons[0] or lon > lons[-1]:
        return None
    if lead_h < leads[0] or lead_h > leads[-1]:
        return None
    ilat = min(range(len(lats)), key=lambda i: abs(lats[i] - lat))
    ilon = min(range(len(lons)), key=lambda i: abs(lons[i] - lon))
    for j in range(1, len(leads)):
        if lead_h <= leads[j]:
            f = (lead_h - leads[j - 1]) / (leads[j] - leads[j - 1])
            u0, u1 = extract["u10_ms"][j - 1][ilat][ilon], extract["u10_ms"][j][ilat][ilon]
            v0, v1 = extract["v10_ms"][j - 1][ilat][ilon], extract["v10_ms"][j][ilat][ilon]
            return u0 + f * (u1 - u0), v0 + f * (v1 - v0)
    return None


def compute_corridors(mmsi, now, cycle_id, cfg, shard_dir=r"D:\naviguesser\aisstream",
                      gefs_root=None, boxes_cfg=None, vessel_type=None):
    """The §6 numeric core, landed 2026-08-29 under R2's 48 h clock.

    Current corridor: constant COG/SOG rhumb-line extrapolation from the
    most recent fix; 72 one-hour bins over the window, sampled at bin
    midpoints, positions extrapolated from the fix instant. Preferred
    corridor: argmin exposure over the declared candidate family of
    constant heading offsets — the current corridor is a member, so
    predicted_margin <= 0 structurally and ties break deterministically by
    (exposure, |offset|, offset). Exposure: C_X(theta_rel) * v_rel^2 per
    bin in the prereg's pinned units, apparent wind = forecast wind minus
    ship vector, theta_rel = |wrap(wind_FROM - course)| with head wind 0.
    Coverage is paired across the whole family; the margin is the paired
    per-bin mean scaled to 72 bins. Every input is digest-verified before
    it is trusted. Returns {current, preferred, predicted_margin,
    integrity} for build_guidance()."""
    settings = _load_settings(cfg)
    tables = _load_cx_tables(cfg)
    fix_ts, flat0, flon0, sog, cog = _latest_fix(shard_dir, mmsi, now)
    box = _box_of(flat0, flon0, boxes_cfg) if boxes_cfg else None
    if box is None:
        raise Refuse(f"last fix for {mmsi} is outside the declared boxes — "
                     "no wind extract covers it")
    root = gefs_root or (cfg.get("gefs_retrieval") or {}).get("dir")
    if not root:
        raise IntegrationBlank("§11 GEFS retrieval path unpinned")
    extract = _load_wind(root, cycle_id, box)
    try:
        cycle_time = datetime.strptime(cycle_id, "%Y-%m-%dT%H").replace(
            tzinfo=timezone.utc)
    except ValueError:
        raise Refuse(f"cycle id {cycle_id!r} is not the declared "
                     "YYYY-MM-DDTHH format — the wind pack contract names "
                     "its cycles")
    sel = settings["cx_curve_selection"]
    if vessel_type is None:
        curve_key = sel["unknown"]
    else:
        t = int(vessel_type)
        curve_key = sel["ais_70_79"] if 70 <= t <= 79 else \
            sel["ais_80_89"] if 80 <= t <= 89 else sel["unknown"]
    if curve_key not in tables:
        raise Refuse(f"declared C_X curve {curve_key!r} has no angular "
                     "table in the pinned A1 artefact")
    angles, cxvals = tables[curve_key]
    offsets = settings["candidate_family"]["heading_offsets_deg"]
    if 0 not in offsets:
        raise Refuse("declared candidate family lacks the 0 offset — the "
                     "current corridor must be a member (margin <= 0 is "
                     "structural)")

    def step_values(offset):
        """Per-bin C_X·v_rel² for one constant-heading corridor; None where
        the bin is outside extract coverage (never extrapolated)."""
        hdg = (cog + offset) % 360.0
        v_ms = sog * KN_MS
        ve = v_ms * math.sin(math.radians(hdg))
        vn = v_ms * math.cos(math.radians(hdg))
        out = []
        for k in range(int(WINDOW_H)):
            t_mid = now + timedelta(hours=WINDOW_OPEN_LAG_H + k + 0.5)
            dh = (t_mid - fix_ts).total_seconds() / 3600.0
            latk = flat0 + (sog * dh) * math.cos(math.radians(hdg)) / 60.0
            lonk = flon0 + (sog * dh) * math.sin(math.radians(hdg)) / \
                (60.0 * math.cos(math.radians(latk)))
            lead = (t_mid - cycle_time).total_seconds() / 3600.0
            wind = _wind_at(extract, latk, lonk, lead)
            if wind is None:
                out.append(None)
                continue
            awe, awn = wind[0] - ve, wind[1] - vn
            v_rel = math.hypot(awe, awn)
            to_deg = math.degrees(math.atan2(awe, awn)) % 360.0
            theta = abs(_wrap180((to_deg + 180.0) % 360.0 - hdg))
            out.append(_interp_cx(angles, cxvals, theta) * v_rel * v_rel)
        return out

    per = {o: step_values(o) for o in offsets}
    paired = [k for k in range(int(WINDOW_H))
              if all(per[o][k] is not None for o in offsets)]
    if not paired:
        raise Refuse(f"no covered window bin for {mmsi} on cycle {cycle_id} "
                     "— the extract does not reach this corridor at all")
    scale = float(len(per[0])) / len(paired)   # declared: paired mean, 72-bin scaled
    means = {o: sum(per[o][k] for k in paired) * scale for o in offsets}
    pref = min(offsets, key=lambda o: (means[o], abs(o), o))
    margin = means[pref] - means[0]
    rule_id = "const_cog_sog_rhumb_1h_midpoint"
    current = {"rule": rule_id,
               "origin": {"lat": round(flat0, 6), "lon": round(flon0, 6),
                          "fix_utc": iso(fix_ts)},
               "cog_deg": cog, "sog_kt": sog, "curve": curve_key,
               "bins_covered": len(paired)}
    preferred = dict(current, heading_offset_deg=pref)
    return {"current": current, "preferred": preferred,
            "predicted_margin": round(margin, 6),
            "integrity": {
                "forecast_age_h": round((now - cycle_time).total_seconds() / 3600.0, 6),
                "ais_fix_age_min": round((now - fix_ts).total_seconds() / 60.0, 6),
                "coverage_ok": len(paired) == int(WINDOW_H),
                "margin_abs": abs(round(margin, 6))}}


# ------------------------------------------------------------------ §4
def _line_digest(line_text):
    return sha(line_text.rstrip("\n").encode("utf-8"))


def register_head(path):
    if not path.exists():
        return GENESIS
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return _line_digest(lines[-1]) if lines else GENESIS


def register_ids(path):
    ids = set()
    if not path.exists():
        return ids
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ids.add(json.loads(line)["guidance"]["guidance_id"])
        except (json.JSONDecodeError, KeyError):
            continue
    return ids


def append_register(path, obj, now):
    """Append one guidance object. The pin timestamp is the write time (§4).
    A late pin is RECORDED with pin_valid_on_time=false — never deleted,
    never re-issued; the weekly close-out counts them (§10.1)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pin_utc = datetime.now(timezone.utc) if now is None else now
    on_time = pin_utc < parse_ts(obj["window_open"])
    entry = {"guidance": obj, "pin_utc": iso(pin_utc),
             "pin_valid_on_time": on_time,
             "prev_digest": register_head(path)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return on_time


def append_gap(path, now, mmsi, reason):
    """A watched vessel the core cannot cost is a recorded gap — never a
    silent skip (§7.4(c) counts pins per watched vessel), never a run
    failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"date": iso(now), "mmsi": str(mmsi), "reason": str(reason)[:300]}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def verify_register(path):
    """Walk the chain; return (ok, detail). Names the first broken link."""
    if not path.exists():
        return True, "empty"
    prev = GENESIS
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return False, f"chain-break line {i}: unparseable"
        if entry.get("prev_digest") != prev:
            return False, f"chain-break line {i}: prev_digest mismatch"
        g = entry.get("guidance", {})
        body = {k: v for k, v in g.items() if k != "sha256"}
        if g.get("sha256") != sha(canon(body)):
            return False, f"chain-break line {i}: guidance sha256 mismatch"
        prev = _line_digest(line)
    return True, "chain-ok"


# ---------------------------------------------------------------- §5.2
def pick_gefs_cycle(gefs_dir, now):
    """A5 (v0.5, 2026-08-30): the freshest archived cycle whose manifest
    verifies AND whose extract leads COVER the whole 72 h window at `now`
    (bin midpoints need age+1.5 .. age+72.5 h inside every wind_box
    member's leads_h). A failed verification is a refusal — never a
    substitute cycle (§5.2/§10.2, unchanged from A4). A non-covering
    cycle is SKIPPED to the next older (the declared A5 rule); no
    covering cycle at all is a refusal — never the silent
    coverage_ok=False degradation D24 drills at corridor level."""
    d = Path(gefs_dir)
    if not d.is_dir():
        raise Refuse(f"gefs archive path absent: {gefs_dir}")
    cycles = sorted([p for p in d.iterdir() if p.is_dir()])
    if not cycles:
        raise Refuse(f"gefs archive holds no cycles: {gefs_dir}")
    skipped = []
    for cand in reversed(cycles):                     # freshest first
        manifests = sorted(cand.rglob("manifest.json"))
        if not manifests:
            raise Refuse(f"gefs cycle {cand.name} has no manifest — a "
                         "manifest-less cycle in the archive is a stop, "
                         "never a skip")
        verified = []
        bad = []
        for m in manifests:
            try:
                entries = json.loads(m.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                raise Refuse(f"gefs manifest unparseable: {m}")
            entries = entries.get("files", entries) if isinstance(entries, dict) else entries
            for e in entries:
                f = m.parent / e["path"]
                if not f.exists() or sha(f.read_bytes()) != e["sha256"]:
                    bad.append(e["path"])
                elif f.name.startswith("wind_box_") and f.suffix == ".json":
                    verified.append(f)
        if bad:
            raise Refuse(f"gefs cycle {cand.name} manifest FAILED verification "
                         f"on {len(bad)} member(s): {bad[0]} — stop, never substitute")
        try:
            cyc_t = datetime.strptime(cand.name, "%Y-%m-%dT%H").replace(
                tzinfo=timezone.utc)
        except ValueError:
            raise Refuse(f"gefs cycle dir {cand.name!r} is not the declared "
                         "flat ISO cycle id — the archive shape is the contract")
        age_h = (now - cyc_t).total_seconds() / 3600.0
        need_lo = age_h + WINDOW_OPEN_LAG_H + 0.5
        need_hi = age_h + WINDOW_OPEN_LAG_H + (WINDOW_H - 1.0) + 0.5
        cover = bool(verified)
        for f in verified:
            leads = json.loads(f.read_text(encoding="utf-8")).get("leads_h") or []
            if not leads or leads[0] > need_lo or leads[-1] < need_hi:
                cover = False
                break
        if cover:
            return cand.name
        skipped.append(f"{cand.name} (window needs leads {need_lo:.1f}.."
                       f"{need_hi:.1f} h)")
    raise Refuse(f"no archived cycle covers the 72 h window at {iso(now)} — "
                 f"{len(skipped)} skipped: {skipped[0]} — stop, never silent "
                 "degradation")


# ------------------------------------------------------------------ §2
def _first_key(rec, keys):
    for k in keys:
        if k in rec and rec[k] is not None:
            return rec[k]
    return None


def iter_shard_records(shard_dir, since, until):
    """Yield every JSON-parseable line from shards overlapping
    [since, until]. The caller counts parseable vs position-bearing —
    that distinction is the schema probe."""
    d = Path(shard_dir)
    if not d.is_dir():
        return
    for p in sorted(d.glob("ais_*.ndjson")):
        day = parse_ts(p.stem.replace("ais_", "") + "T00:00:00Z")
        if day and (day > until or day + timedelta(days=1) <= since):
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def extract_vessel(rec):
    """(mmsi, ts, lat, lon, sog, cog, vessel_type) or None. The measured
    flattened C1 schema first (sog_kt/cog_deg), then bare keys, then the
    aisstream Message/MetaData nest (the F1 watchlist feed's shape is TBD —
    all three forms are accepted and the probe guards the whole)."""
    msg = rec.get("Message", {}) if isinstance(rec.get("Message"), dict) else {}
    meta = rec.get("MetaData", {}) if isinstance(rec.get("MetaData"), dict) else {}
    pos = msg.get("PositionReport", {}) if isinstance(msg.get("PositionReport"), dict) else {}
    stt = msg.get("ShipStaticData", {}) if isinstance(msg.get("ShipStaticData"), dict) else {}
    mmsi = _first_key(rec, ("mmsi", "MMSI", "UserID")) or \
        _first_key(meta, ("MMSI",)) or \
        _first_key(pos, ("UserID",)) or _first_key(stt, ("UserID",))
    ts = parse_ts(_first_key(rec, ("received_utc", "time_utc")) or
                  _first_key(meta, ("time_utc",)))
    if mmsi is None or ts is None:
        return None
    sog = _first_key(rec, ("sog_kt", "sog", "Sog", "SOG"))
    if sog is None:
        sog = pos.get("Sog")
    cog = _first_key(rec, ("cog_deg", "cog", "Cog", "COG"))
    if cog is None:
        cog = pos.get("Cog")
    vt = _first_key(rec, ("vessel_type", "VesselType", "Type"))
    if vt is None:
        vt = stt.get("Type")
    lat = _first_key(rec, ("lat", "Latitude"))
    if lat is None:
        lat = pos.get("Latitude")
    lon = _first_key(rec, ("lon", "Longitude"))
    if lon is None:
        lon = pos.get("Longitude")
    return (str(mmsi), ts, lat, lon, sog, cog, vt)


def load_watchlist(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def select_watchlist(shard_dir, boxes_cfg, heading_rules, types_map,
                     watchlist, now, require_heading, require_types):
    """§2 v0.3, the whole rule. Deterministic: type 70-89 (pinned map, when
    supplied) OR type UNKNOWN (A3 — admitted, tallied, degraded at §7.2;
    measured 2026-08-29 the C1 shards carry position reports only), last
    fix SOG >= 7 kt in the previous 24 h, outbound heading per box
    (integration blank), rank by most recent fix, K=5. Persistence: 21-day
    cap, 72-h no-position drop. The 70-89 filter binds every vessel whose
    type IS known — a known non-cargo vessel is never admitted. Returns
    (active, adds, drops, provisional_heading, provisional_type,
    type_unknown)."""
    since = now - timedelta(hours=24)
    latest, types = {}, {}
    parseable = with_pos = 0
    for rec in iter_shard_records(shard_dir, since, now):
        parseable += 1
        got = extract_vessel(rec)
        if got is None:
            continue
        mmsi, ts, lat, lon, sog, cog, vtype = got
        if vtype is not None:
            types[mmsi] = vtype
        if sog is None or lat is None:
            continue
        with_pos += 1
        if not (since <= ts <= now):
            continue  # §2: the previous 24 h of box traffic, nothing older
        if mmsi not in latest or ts > latest[mmsi][0]:
            latest[mmsi] = (ts, lat, lon, float(sog), cog)
    if parseable and not with_pos:
        raise Refuse("schema-probe: shard records parse but no position-"
                     "bearing record extracts — format drift, not an empty ocean")
    provisional_h = heading_rules is None
    provisional_t = types_map is None
    if provisional_h and require_heading:
        raise IntegrationBlank("§2 outbound-heading rules unpinned")
    cand, type_unknown = [], 0
    for mmsi, (ts, lat, lon, sog, cog) in latest.items():
        vt = types.get(mmsi)
        if vt is None and types_map is not None:
            vt = types_map.get(mmsi)
        if vt is None:
            type_unknown += 1
            # A3: unknown type is eligibility-with-degradation, declared —
            # the 70-89 filter below binds only vessels whose type IS known
        elif not (70 <= int(vt) <= 89):
            continue
        if sog < 7.0:
            continue
        if not provisional_h:
            box = _box_of(lat, lon, boxes_cfg)
            rule = heading_rules.get(box) if box else None
            if rule is None or cog is None or not _bearing_in_any(float(cog), rule):
                continue
        cand.append((mmsi, ts))
    cand.sort(key=lambda x: x[1], reverse=True)

    active = dict(watchlist)
    drops = []
    for mmsi, st in list(active.items()):
        entered = parse_ts(st.get("entered"))
        seen = parse_ts(st.get("last_seen"))
        if entered and (now - entered).days >= MAX_WATCH_DAYS:
            drops.append((mmsi, "21-day-cap"))
            del active[mmsi]
        elif seen and (now - seen).total_seconds() > DROP_AFTER_H * 3600:
            drops.append((mmsi, "72h-no-position"))
            del active[mmsi]
        elif mmsi in latest:
            st["last_seen"] = iso(latest[mmsi][0])
    adds = []
    for mmsi, ts in cand:
        if len(active) >= K_WATCH:
            break
        if mmsi not in active:
            active[mmsi] = {"entered": iso(now), "last_seen": iso(ts)}
            adds.append(mmsi)
    return active, adds, drops, provisional_h, provisional_t, type_unknown


def _box_of(lat, lon, boxes_cfg):
    """Box membership. Two declared shapes: the REAL pinned file
    (accrual/declared_boxes.json) is {"boxes": [[[lat,lon],[lat,lon]], ...]}
    — corner pairs in the aisstream order-free convention, keyed by INDEX
    (heading rules pin as {"0": {...}} per the pinned array order); and the
    named dict shape {"name": {lat_min, lat_max, lon_min, lon_max}} used by
    drill fixtures. Measured 2026-08-29 against the real file after A3's
    wider emit path first reached it."""
    if not boxes_cfg:
        return None
    boxes = boxes_cfg.get("boxes") if isinstance(boxes_cfg, dict) else None
    if isinstance(boxes, list):
        for i, pair in enumerate(boxes):
            (la1, lo1), (la2, lo2) = pair[0], pair[1]
            if min(la1, la2) <= lat <= max(la1, la2) and \
               min(lo1, lo2) <= lon <= max(lo1, lo2):
                return str(i)
        return None
    for name, b in (boxes_cfg or {}).items():
        if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
            return name
    return None


def _bearing_in(cog, rule):
    lo, hi = rule["deg_min"], rule["deg_max"]
    return lo <= cog <= hi if lo <= hi else (cog >= lo or cog <= hi)


def _bearing_in_any(cog, rule):
    """A box's outbound rule is one bearing range OR a list of ranges
    (Singapore's strait is legitimately outbound in both through-modes —
    the two-range shape is declared in the integration config)."""
    if isinstance(rule, list):
        return any(_bearing_in(cog, r) for r in rule)
    return _bearing_in(cog, rule)


# ------------------------------------------------------------------ §9
def scan_no_network(path):
    """Shadow mode is structural: this job imports no network library.
    Drilled red-first against a mutated copy of this very source."""
    src = Path(path).read_text(encoding="utf-8")
    return [t for t in NETWORK_TOKENS if t in src]


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true",
                    help="pin guidance into the register; refuses on any unpinned blank")
    ap.add_argument("--now", default=None, help="ISO override (drills)")
    ap.add_argument("--shards", default=r"D:\naviguesser\aisstream",
                    help="live AIS store (moved to D: 2026-09-05)")
    ap.add_argument("--gefs-dir", default="data/gefs_archive")
    ap.add_argument("--register", default=str(REGISTER))
    ap.add_argument("--watchlist", default=str(WATCHLIST))
    ap.add_argument("--gaps", default=str(GAPS))
    ap.add_argument("--boxes", default=str(BOXES))
    ap.add_argument("--config", default=str(CONFIG))
    ap.add_argument("--probe-python", default=None)
    ap.add_argument("--head", action="store_true", help="print register head digest and exit")
    ap.add_argument("--json", default=None, help="optional JSON record out path")
    a = ap.parse_args()

    register = Path(a.register)
    if a.head:
        ok, detail = verify_register(register)
        print(f"F1-HEAD {register_head(register)} verify={detail}")
        return 0 if ok else 1

    now = parse_ts(a.now) if a.now else datetime.now(timezone.utc)
    if a.probe_python:
        try:
            r = subprocess.run([a.probe_python, "-c", "print('ok')"],
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0 or r.stdout.strip() != "ok":
                print(f"F1-REFUSED interpreter-surface: {a.probe_python} "
                      f"exit={r.returncode} stdout={len(r.stdout)}B — the 00:11 shape")
                return 2
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"F1-REFUSED interpreter-surface unrunnable: {e}")
            return 2

    hits = scan_no_network(__file__)
    if hits:
        print(f"F1-REFUSED shadow-mode scan: network import present: {hits[0]}")
        return 2

    rec = {"run_utc": iso(now), "mode": "emit" if a.emit else "dry-run"}
    cfg = None
    types_map = None
    if Path(a.config).exists():
        cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    boxes_cfg = None
    if Path(a.boxes).exists():
        try:
            boxes_cfg = json.loads(Path(a.boxes).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    if a.emit:
        # every input verified BEFORE anything is selected or pinned
        if cfg is None:
            print(f"F1-REFUSED integration config absent: {a.config} — §11 "
                  f"blanks are pinned at integration, never after first emission")
            return 2
        blanks = [k for k in ("outbound_heading_rules", "corridor_rule",
                              "model_path", "model_sha256",
                              "optimizer_settings_path",
                              "optimizer_settings_sha256",
                              "gefs_retrieval", "trial_start")
                  if not cfg.get(k)]
        if blanks:
            print(f"F1-REFUSED integration blanks unpinned: {blanks[0]} (+{len(blanks)-1})")
            return 2
        model = Path(cfg["model_path"])
        if not model.exists() or sha(model.read_bytes()) != cfg["model_sha256"]:
            print(f"F1-REFUSED model digest mismatch: {cfg['model_path']} — "
                  f"a stale input is a build failure, not a warning")
            return 2
        # A3: the type map is OPTIONAL — but when configured it is verified
        # with the same stale-input-is-a-build-failure discipline
        if cfg.get("vessel_types_path") or cfg.get("vessel_types_sha256"):
            if not (cfg.get("vessel_types_path") and cfg.get("vessel_types_sha256")):
                print("F1-REFUSED vessel-types config half-pinned: path and "
                      "sha256 travel together or not at all (A3)")
                return 2
            tmap = Path(cfg["vessel_types_path"])
            if not tmap.exists() or sha(tmap.read_bytes()) != cfg["vessel_types_sha256"]:
                print(f"F1-REFUSED vessel-types digest mismatch: {cfg['vessel_types_path']}")
                return 2
            types_map = {str(k): v for k, v in
                         json.loads(tmap.read_text(encoding="utf-8")).items()}
        try:
            cycle_id = pick_gefs_cycle(a.gefs_dir, now)
        except Refuse as e:
            print(f"F1-REFUSED gefs: {e}")
            return 2
        # systemic inputs verified run-level BEFORE any vessel is costed —
        # a systemic defect refuses the whole run; it is never a per-vessel gap
        try:
            _load_settings(cfg)
            _load_cx_tables(cfg)
        except (IntegrationBlank, Refuse) as e:
            print(f"F1-REFUSED {e}")
            return 2

    watch_path = Path(a.watchlist)
    watchlist = load_watchlist(watch_path)

    try:
        active, adds, drops, prov_h, prov_t, type_unknown = select_watchlist(
            a.shards, boxes_cfg, (cfg or {}).get("outbound_heading_rules"),
            types_map, watchlist, now,
            require_heading=a.emit, require_types=a.emit)
    except (Refuse, IntegrationBlank) as e:
        print(f"F1-REFUSED selection: {e}")
        return 2

    if not a.emit:
        print(f"F1-DRYRUN {now.date()} selected={len(adds)} watchlist={len(active)} "
              f"provisional_heading={1 if prov_h else 0} provisional_type={1 if prov_t else 0} "
              f"type_unknown={type_unknown} drops={len(drops)}"
              + (" EMPTY_SELECTION" if not active else ""))
        rec.update(selected=adds, watchlist=len(active),
                   provisional_heading=prov_h, provisional_type=prov_t,
                   type_unknown=type_unknown,
                   drops=[list(d) for d in drops])
        if a.json:
            Path(a.json).write_text(json.dumps(rec, indent=2), encoding="utf-8")
        return 0

    gaps_path = Path(a.gaps)
    ids = register_ids(register)
    pinned = late = dup = gaps = 0
    for mmsi in active:
        vt = types_map.get(mmsi) if types_map else None
        try:
            corridors = compute_corridors(
                mmsi, now, cycle_id, cfg, shard_dir=a.shards,
                gefs_root=(cfg.get("gefs_retrieval") or {}).get("dir") or a.gefs_dir,
                boxes_cfg=boxes_cfg, vessel_type=vt)
        except IntegrationBlank as e:
            print(f"F1-REFUSED {e}")
            return 2
        except Refuse as e:
            append_gap(gaps_path, now, mmsi, e)
            gaps += 1
            continue
        obj = build_guidance(mmsi, iso(now), cycle_id,
                             corridors["current"], corridors["preferred"],
                             corridors["predicted_margin"], corridors["integrity"],
                             vessel_type=vt)
        if obj["guidance_id"] in ids:
            dup += 1
            continue
        if not append_register(register, obj, now):
            late += 1
        pinned += 1
    if active:
        watch_path.parent.mkdir(parents=True, exist_ok=True)
        watch_path.write_text(json.dumps(active, indent=2), encoding="utf-8")
    head = register_head(register)[:12]
    print(f"F1-EMIT {now.date()} pinned={pinned} late={late} dup={dup} gaps={gaps} head={head}"
          + (" EMPTY_SELECTION" if not active else ""))
    rec.update(pinned=pinned, late=late, dup=dup, gaps=gaps, head=head,
               cycle_id=cycle_id, type_unknown=type_unknown)
    if a.json:
        Path(a.json).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

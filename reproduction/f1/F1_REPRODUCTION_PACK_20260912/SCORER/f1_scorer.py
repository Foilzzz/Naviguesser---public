"""F1 scorer — how a guidance object is scored once its window has closed.

DESIGN
------
Two things are scored, separately, and never blended into one number:

1. MARGIN ACCURACY (continuous). The object predicted a margin — the cost the recommended
   route would save against the baseline route, computed through the *forecast*. After the
   window, both routes are executed through the *realised* weather and the realised margin is
   measured the same way. Error = predicted - realised. Reported as MAE, bias, and (where the
   object carried bounds) interval coverage.

2. CONFIDENCE CALIBRATION (proper scoring rule). Each object carries a confidence class. The
   class is mapped to a PINNED implied probability that the recommendation "hits":

        FULL -> 0.90     REDUCED -> 0.70     LOW -> 0.50

   and scored with the Brier score  (p_class - hit)^2,  hit in {0,1}.

   Brier is a *proper* scoring rule, which is the whole point: it cannot be gamed by always
   saying LOW. The asymmetry the ruling asked for falls out of it:

        FULL miss    = 0.81      REDUCED miss = 0.49      LOW miss = 0.25
        FULL hit     = 0.01      REDUCED hit  = 0.09      LOW hit  = 0.25

   A FULL miss costs 3.2x a REDUCED miss. A LOW hit is worth exactly as much as a LOW miss —
   being right when you said you didn't know earns nothing. That is the correct incentive.

   "Hit" is pinned as: the realised margin lies inside the object's declared bounds. If the
   object carried no bounds, hit = sign(realised) == sign(predicted) and |error| <= tolerance.

3. REFUSALS are rows, not exceptions. A refusal is CORRECT if the coverage condition it cited
   genuinely did not hold (checkable against the archive), else it is a FALSE REFUSAL. Refusal
   rate is reported; it is never penalised as such.

4. SWITCHOVER COMPARISON. The same scorer, partitioned by `emitted_source` in
   {backbone, overlay}, on the same windows. Plus the veto rate. That is the experiment.

Everything here is pure and deterministic. The class->probability map is an argument, never
a default hidden in code, so the pre-registration pins it explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional
import math

import numpy as np


# --------------------------------------------------------------------------- pinned config
@dataclass(frozen=True)
class ClassMap:
    """Implied hit probabilities per confidence class. PINNED in the pre-registration."""
    probs: dict            # e.g. {"FULL": 0.90, "REDUCED": 0.70, "LOW": 0.50}
    tolerance: float       # |error| tolerance for hit when the object carries no bounds

    def p(self, cls: str) -> float:
        if cls not in self.probs:
            raise KeyError(f"unknown confidence class {cls!r}; pinned classes: {list(self.probs)}")
        return self.probs[cls]


# --------------------------------------------------------------------------- records
@dataclass(frozen=True)
class Emission:
    """The scoreable subset of a guidance object. Refusals have refused=True and no margin."""
    object_id: str
    window_id: str
    vessel: str
    confidence: Optional[str]          # None for a refusal
    predicted_margin: Optional[float]  # cost units (hours or fuel), None for a refusal
    lower: Optional[float] = None      # declared bounds on the margin, if any
    upper: Optional[float] = None
    emitted_source: str = "backbone"   # "backbone" | "overlay"
    vetoed: bool = False               # overlay proposal vetoed -> backbone emitted
    refused: bool = False
    refusal_reason: Optional[str] = None


@dataclass(frozen=True)
class Outcome:
    object_id: str
    realised_margin: Optional[float]   # None if the window could not be scored
    unscorable_reason: Optional[str] = None
    refusal_condition_held: Optional[bool] = None   # for refusals: was the cited condition true?


@dataclass(frozen=True)
class ScoredRow:
    object_id: str
    window_id: str
    vessel: str
    emitted_source: str
    confidence: Optional[str]
    kind: str                 # "scored" | "refusal_correct" | "refusal_false" | "unscorable"
    error: Optional[float]    # predicted - realised
    hit: Optional[int]
    brier: Optional[float]


# --------------------------------------------------------------------------- scoring
def _hit(e: Emission, realised: float, cm: ClassMap) -> int:
    if e.lower is not None and e.upper is not None:
        return int(e.lower <= realised <= e.upper)
    same_sign = (math.copysign(1, realised) == math.copysign(1, e.predicted_margin)) or realised == 0
    return int(same_sign and abs(e.predicted_margin - realised) <= cm.tolerance)


def score(emissions: Iterable[Emission], outcomes: Iterable[Outcome], cm: ClassMap) -> list[ScoredRow]:
    """Join emissions to outcomes by object_id and score each. Every emission yields exactly
    one row — refusals and unscorables included — so the record has no silent gaps."""
    out = {o.object_id: o for o in outcomes}
    rows: list[ScoredRow] = []
    for e in emissions:
        o = out.get(e.object_id)
        base = dict(object_id=e.object_id, window_id=e.window_id, vessel=e.vessel,
                    emitted_source=e.emitted_source, confidence=e.confidence)
        if e.refused:
            if o is None or o.refusal_condition_held is None:
                rows.append(ScoredRow(**base, kind="unscorable", error=None, hit=None, brier=None))
            else:
                kind = "refusal_correct" if o.refusal_condition_held else "refusal_false"
                rows.append(ScoredRow(**base, kind=kind, error=None, hit=None, brier=None))
            continue
        if o is None or o.realised_margin is None:
            rows.append(ScoredRow(**base, kind="unscorable", error=None, hit=None, brier=None))
            continue
        h = _hit(e, o.realised_margin, cm)
        p = cm.p(e.confidence)
        rows.append(ScoredRow(**base, kind="scored",
                              error=e.predicted_margin - o.realised_margin,
                              hit=h, brier=(p - h) ** 2))
    return rows


# --------------------------------------------------------------------------- summaries
def margin_stats(rows: Iterable[ScoredRow]) -> dict:
    errs = np.array([r.error for r in rows if r.kind == "scored"], float)
    if errs.size == 0:
        return {"n": 0, "mae": None, "bias": None}
    return {"n": int(errs.size), "mae": float(np.mean(np.abs(errs))), "bias": float(np.mean(errs))}


def brier_by_class(rows: Iterable[ScoredRow]) -> dict:
    """Mean Brier per class, plus the pooled score. Lower is better."""
    by: dict[str, list[float]] = {}
    for r in rows:
        if r.kind == "scored":
            by.setdefault(r.confidence, []).append(r.brier)
    out = {c: {"n": len(v), "brier": float(np.mean(v))} for c, v in sorted(by.items())}
    pooled = [b for v in by.values() for b in v]
    out["_pooled"] = {"n": len(pooled), "brier": float(np.mean(pooled)) if pooled else None}
    return out


def reliability_table(rows: Iterable[ScoredRow], cm: ClassMap) -> dict:
    """Per class: implied p vs observed hit rate. The integrity-fatigue diagnostic — if FULL
    hits at 0.6, the ladder is miscalibrated and the fix is the ladder's physical definitions,
    never the class->p map (that is pinned)."""
    by: dict[str, list[int]] = {}
    for r in rows:
        if r.kind == "scored":
            by.setdefault(r.confidence, []).append(r.hit)
    return {c: {"n": len(v), "implied_p": cm.p(c), "observed_hit_rate": float(np.mean(v)),
                "gap": float(np.mean(v) - cm.p(c))} for c, v in sorted(by.items())}


def refusal_accounting(rows: Iterable[ScoredRow]) -> dict:
    rows = list(rows)
    n = len(rows)
    k = lambda kind: sum(1 for r in rows if r.kind == kind)
    return {"total_objects": n, "scored": k("scored"), "refusal_correct": k("refusal_correct"),
            "refusal_false": k("refusal_false"), "unscorable": k("unscorable"),
            "refusal_rate": (k("refusal_correct") + k("refusal_false")) / n if n else None}


def compare_sources(rows: Iterable[ScoredRow], emissions: Iterable[Emission]) -> dict:
    """The switchover experiment. Same scorer, partitioned by emitted_source, plus veto rate.
    Restricts to windows where BOTH sources have scored rows so the comparison is paired."""
    rows = list(rows); emissions = list(emissions)
    windows_by_source: dict[str, set] = {}
    for r in rows:
        if r.kind == "scored":
            windows_by_source.setdefault(r.emitted_source, set()).add(r.window_id)
    common = set.intersection(*windows_by_source.values()) if len(windows_by_source) > 1 else set()
    out = {}
    for src in sorted(windows_by_source):
        sub = [r for r in rows if r.kind == "scored" and r.emitted_source == src
               and (not common or r.window_id in common)]
        out[src] = {"margin": margin_stats(sub), "brier": brier_by_class(sub)["_pooled"]}
    n_overlay_attempts = sum(1 for e in emissions if e.emitted_source == "overlay" or e.vetoed)
    n_vetoed = sum(1 for e in emissions if e.vetoed)
    out["_veto_rate"] = (n_vetoed / n_overlay_attempts) if n_overlay_attempts else None
    out["_paired_windows"] = len(common)
    return out

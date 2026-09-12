# F1_SCORER_PREREG §3 — AMENDMENT TEXT v9 (FINAL — re-measured at the pin instant)

**This is amendment text, not an argument for one.** v6 argued; v7 is drafted to
be pinned. §1 is the replacement §3 in full; everything after it is the
supporting record and the findings that did not reach a ruling.

**Governing document:** `corpus_intake/overlay/F1_SCORER_PREREG_v1.md`, sha256
`199be2e3e1393fa4667f44ca97240b17658f144de31b1b3db8097617a4ab7138`, 6,822 B,
landed and merged 2026-09-09 (`2d6293b6`).

**Rulings executed:** pass 1 `OWNER_RULINGS_F1_SCORER_S3_20260910.md`
(`6bf7b14e…f21fb`) and pass 2 `OWNER_RULINGS_F1_SCORER_S3_PASS2_20260910.md`
(`9b488f7e8c0ce597a1e5bd609f08c0d2bedfdfc82a8c52149eac29327b3601fb`) — **rulings
1–7, all executed.**
**Measured evidence:** `s2c_reconciliation_20260909.json`, sha256
`51deafd296321276d3876eb944bfc0b5a344b507e360d7d83f9e5165d8d70452` — every id,
instant and count below is printed from that artefact, never transcribed.

**Supersedes v8 (`a5f6aac3…`), v7 (`4cc83c56…`), v6 (`a0151076…`), v5
(`b7be8946…`), v4, v3, v2 and the 2026-09-07 draft.**

---

## 0. STATUS — RE-MEASURED AT THE PIN INSTANT, TABLE UNCHANGED

**The standing precondition is discharged.** v8 required its counts re-measured
at the actual pin instant rather than carried forward. That has been done, on the
real `accrual/f1/register.jsonl`, and the result is the good one:

| | v8, 2026-09-09T21:31:50Z | re-measured, **2026-09-10T10:51:50Z** |
|---|---|---|
| register rows | 30 | **30** |
| §8-excluded | 15 | **15** |
| exposed (closed since the governing instant) | 5 | **5** |
| still open | 10 | **10** |
| sum reconciles | yes | **yes** |

**Zero windows changed class, and the five ids are byte-for-byte the same.** So
the table in §1 is not a carried-forward figure — it is a re-measured one that
happens to be identical, which is a different claim and the one now on record.
Governing instant **2026-09-08T12:11:25Z**, read from `timestamp/pins.json` per
ruling 7.

**Measured by instrument, not by hand:** `_s3_pin_regenerate.py`
(`b1f74cc68c4b6c677b15bc9f408a9340579160fbd948cae8e615e54f941ee2ac`), run
owner-side. One owner-side patch was needed and is declared in §12 — it does not
touch the measurement.

**THIS TEXT HAS AN EXPIRY, AND IT IS TODAY.** The 2026-09-07 emissions close at
**≈17:30Z on 2026-09-10**. Pinned before that, §1's table stands verbatim. Pinned
after it, the table is wrong — the newly closed windows join the exposed set
under ruling 3 and must be named. **Re-run the instrument and regenerate before
pinning if that hour has passed.** This is written into the document rather than
left as a message because a table with a deadline that only exists in a chat log
is a table someone will eventually pin stale.

**One change of form from ruling 5, carried from v8 and deliberate.** The ruling
names the tolerance as "27 C_X·v²-weighted exposure-hours — one §7.3 tie band".
§1 writes it as **the derivation, with 27 as its current evaluation**. The
ruling's own rationale is that anchoring to an already-pinned constant is a
derivation rather than an invention; a bare `27` would discard exactly that and
leave this tolerance and `TIE_BAND = M0/4` as two constants that must agree but
are recorded independently. If M0 is ever re-pinned, the tolerance moves with it
or is re-argued — written as a literal it would silently do neither.

---

## 1. THE REPLACEMENT §3, IN FULL

> ## 3. "Hit" — pinned definition
>
> **The cost unit.** Margins, errors and this tolerance are all in the unit the
> guidance object declares: **C_X·v²-weighted exposure-hours**, as pinned in the
> F1 trial pre-registration's §3 object schema and computed by
> `corpus_intake/f1_daily_guidance.py`, where the scale constant is
> `M0 = 108.0` (A4: ΔC_X 0.01 × v_rel² 150 × 72 h). The unit is stated here, in
> the same section as the tolerance, so that a tolerance figure is never read as
> a bare number.
>
> **Hit, when the object declared bounds:** hit ⇔ realised margin ∈ [lower, upper].
>
> **Hit, when it did not:** hit ⇔ sign(realised) = sign(predicted) **and**
> |error| ≤ **one §7.3 tie band**, i.e. `TIE_BAND = M0/4`, which under the pinned
> `M0 = 108.0` evaluates to **27 C_X·v²-weighted exposure-hours** (ruling 5,
> 2026-09-10).
>
> **The tolerance is written as that derivation and not as the number 27.** It is
> anchored to a constant the programme had already pre-registered, which is what
> makes it a derivation rather than an invention; recording it as a bare literal
> would leave it and `TIE_BAND` as two constants that must agree but are written
> independently. If `M0` is ever re-pinned, this tolerance moves with it or is
> re-argued explicitly — it may not silently do neither.
>
> **What this tolerance is stringent about, declared because a pooled hit rate
> hides it.** It is an *absolute* tolerance on a quantity whose observed range is
> 0 … −1,727.9576. Its stringency therefore varies enormously by row: at the
> largest observed margin it is 1.56% of the predicted value; at the smallest
> exposed row (1.8 tie bands) it is 55.6%; inside the INDIFFERENT band it exceeds
> 100%. **A hit rate pooled across those rows pools very unequal difficulty**, and
> any headline hit rate must say so or be read per margin-magnitude stratum. This
> is not an objection to the figure — an absolute tolerance in a physical unit is
> the right shape for "what error would a reader call right" — it is a property
> of it that must travel with it.
>
> **Zero convention (ruling 1).** A realised margin of exactly zero **sign-agrees
> with any prediction**. This is what the pinned reference implementation does
> (`naviguesser_overlay/f1_scorer.py`, `or realised == 0`), and stating it here is
> what allows an independent implementation of this rule to agree with it. The
> clause is load-bearing for negative zero: `copysign(1, -0.0)` is `-1.0`, so
> without it a hit would turn on the sign bit of a zero, which is not a physical
> distinction.
>
> **A zero is a computed zero, never a stand-in for "no score" (ruling 1).** An
> unscorable row is **excluded and declared** — it is never scored, and never
> recorded as a margin or error of 0.0. The distinction is **structural, not by
> value**: an unscorable row carries no realised margin at all and is a distinct
> row kind, so no reader can confuse "the two corridors were identical" with "we
> could not score this". Register entry `99beed5ed3dc…` is the worked case: its
> corridors are identical on curve, sog, cog and rule, which forces margin 0.0 —
> a computed zero.
>
> **The tolerance is pinned and OTS-stamped before the first window is SCORED.**
> No hit, hit rate, Brier score or reliability table may be computed by any
> instrument until the pin and its stamp exist.
>
> ### Exclusion carried forward to this amendment's stamp (ruling 3)
>
> **Which instant defines a boundary (ruling 7, 2026-09-10).** Wherever this
> pre-registration says "stamp instant", it means the document's `pinned_utc` in
> `timestamp/pins.json`. That is the instrument of record and the one a
> reconciliation can compute from; a pending OpenTimestamps receipt carries no
> reliable instant until it is upgraded, so making the receipt the boundary would
> make the boundary unmeasurable at the moment a decision needs it. The OTS-stamp
> instant is **derived and recorded from the receipt metadata**, never written as
> an independent constant beside `pinned_utc`.
>
> §8 excludes every window closing before **v1's** stamp instant. This amendment
> introduces a second boundary — its own stamp — and windows closing between the
> two would otherwise be scored under a tolerance chosen after their outcomes
> existed. **They are not.** Every window whose `window_close` precedes *this
> amendment's* OTS-stamp instant is **EXCLUDED-BY-PREREGISTRATION** on §8's terms:
> excluded, named, counted, and open to any third party to score under any rule
> they choose, with the result published whatever it says.
>
> **The exposure, named in full so it can never silently grow.** Measured against
> `accrual/f1/register.jsonl` at **2026-09-10T10:51:50Z**: 30 rows, 15
> §8-excluded, 10 still open, and **five** windows that were open at the
> governing instant (2026-09-08T12:11:25Z, `pins.json :: pinned_utc`, ruling 7)
> and have since closed. The table is regenerated from the register at the
> measurement instant, never transcribed:
>
> | guidance_id | issued_utc | window_close | confidence |
> |---|---|---|---|
> | `3ae936be5fc9cd211f7201c36670eb8f26a4a48aa41a04516336ee05d17fbb2d` | 2026-09-05T16:30:47.364322Z | 2026-09-08T17:30:47.364322Z | LOW |
> | `163fe992aaf9ffcaa79f333e6d8f417429da6e7f7dc08c167a50bed308a87d5f` | 2026-09-05T16:30:47.364322Z | 2026-09-08T17:30:47.364322Z | LOW |
> | `7b7749689443c0e14fd5c9b54856d300ccda7a1c5ac59abcf15112dfb4051619` | 2026-09-05T16:30:47.364322Z | 2026-09-08T17:30:47.364322Z | LOW |
> | `eb80cbfd5a70bd8255e52941f725a47d842d583430199bdd648dbe2a93e38719` | 2026-09-06T16:31:06.591543Z | 2026-09-09T17:31:06.591543Z | LOW |
> | `7a0ce7a0295a2d422b98c7fde11e08d1064a80c76a0d14b845677078f2178b70` | 2026-09-06T16:31:06.591543Z | 2026-09-09T17:31:06.591543Z | LOW |
>
> All five are **LOW** confidence and all carry `pin_valid_on_time = true`. They
> span **three vessels and two issue days** — so this exposure is not a random
> five: were it scored, it would land entirely in the LOW row of §7.2's
> reliability table. Declared, not averaged away.
>
> **The ranking enum carries a class the generator cannot produce.**
> `predicted_margin` is `preferred − current` over a candidate family that
> *contains* the current corridor, so it is **≤ 0 structurally**; the register's
> observed range is −1,727.9576 … 0.0. `CURRENT_BETTER` requires a margin above
> the tie band (+27.0) and is therefore unreachable. It is retained in the schema
> for forward compatibility and **declared dead**: any future emission of it is a
> change in the generator, not a result. In consequence, the sign clause above is
> a **one-sided directional test** — "did the realised margin also come out ≤ 0" —
> and must never be reported as a two-sided sign-agreement rate.
>
> **How the tolerance is chosen, and how it is not.** On a stated physical
> argument — what error in C_X·v²-weighted exposure-hours is small enough that a
> reader would call the guidance right — and **never** by reference to which rows
> it would convert into hits. A tolerance chosen to make the visible rows pass is
> the L1 §8.4 failure one layer over: a threshold set after seeing the result it
> will be judged by.

---

## 2. The unit — the premise correction behind ruling 2

Ruling 2 requires the unit named before the tolerance appears. Executed above.
But the ruling's premise — "named nowhere today" — is not what the tree says:

| where | what it says |
|---|---|
| `corpus_intake/F1_FORWARD_GUIDANCE_TRIAL_PREREG.md:34` | `predicted_margin float C_X·v²-weighted exposure-hours, preferred minus current (negative = preferred better)` |
| `corpus_intake/f1_daily_guidance.py:120` | `M0 = 108.0 # §7.2 pinned, C_X·v²-weighted exposure-hours (A4: ΔC_X 0.01 × v_rel² 150 × 72 h)` |

The derivation checks: 0.01 × 150 × 72 = 108. And the scorer prereg already says
*"in the object's **declared** cost unit"* — it defers deliberately, and the
object's declaration is the trial prereg's schema. **The chain resolves.**

So the unit did not need inventing; it needed carrying. That is what §1 does, by
citation rather than by restatement, so there is still exactly one authority for
it.

**The residual gap is narrower and real:** the register rows do not carry the
unit as a field, so the reproduction package would hand a reviewer bare numbers.
That belongs in the reproduction pack's `RECORD/` schema, not in this amendment.

## 3. Ruling 1's structural requirement — already satisfied, verified

Ruling 1 requires the scorer to distinguish a computed zero from a no-score
**structurally, not by value**. The pinned scorer already does:

- `Outcome.realised_margin` is `Optional[float]`; absent means absent.
- `score()` routes `o is None or o.realised_margin is None` to a row of
  `kind="unscorable"` with `error=None, hit=None, brier=None`.
- A scored row with a genuine zero is `kind="scored"` with a numeric error.

The two cases are different row kinds carrying different fields, so no consumer
can reach one by reading the other's value. **No code change is required by this
ruling** — the amendment states in prose a property the implementation already
has, which is the right order.

## 4. `CURRENT_BETTER` — RULED: keep-and-declare (ruling 6, 2026-09-10)

Written into §1 as a declared dead class, which is the option ruled. Removal
would lose information; widening the candidate family so the incumbent can lose
is a generator change needing its own pre-registration under §9. Neither is taken
now. The measurement behind the ruling:

`pref = min(offsets, …)` over a family containing offset 0 (the current
corridor), then `margin = means[pref] − means[0]` — so `margin ≤ 0` by
construction, confirmed by the emitter's own docstring and by the register's
range. `classify_ranking` returns `CURRENT_BETTER` only for `margin > TIE_BAND`
where `TIE_BAND = M0/4 = +27.0`. Unreachable.

Nothing here is a defect in the optimizer: argmin over a family containing the
incumbent is the right construction. The defect is that a pre-registered enum
and a pre-registered hit rule both describe a freedom the generator does not
have. **Nothing in the tree exercises the class** — it appears in no test — which
is why it stayed invisible.

**The consequence that must travel with the ruling**, and it is in §1: the sign
clause is a **one-sided directional test** — "did the realised margin also come
out ≤ 0" — and is **never reportable as a two-sided sign-agreement rate**. A
reader shown "sign agreement 71%" would reasonably infer the model could have
been wrong in the other direction. It could not.

## 5. The two artefact findings — both closed 2026-09-10

**The governing instant — RULED (ruling 7).** `pinned_utc` governs; the OTS
instant is derived from receipt metadata and never written independently. Folded
into §1.

*Measured cost of the choice: none, on this data.* The two instants differ by
**52 s** (`pinned_utc` 12:11:25Z; OTS proxy 12:10:33Z from the pending receipt's
mtime, labelled a proxy in the artefact, which is the honest labelling) and no
window closes between them, so the 15 / 0 / 10 split is invariant either way.

**An independent reason the invariance is structural, not a fact about this
data.** Emissions are daily at **16:30 UTC** and a window opens 1 h after
emission and runs 72 h (trial prereg §4), so **every window closes at ≈17:30 UTC**
— which the five exposed rows confirm (all close at 17:30:47Z or 17:31:06Z).
Both candidate boundary instants sit at ≈12:10–12:11 UTC, roughly five hours from
any close. Under the current cadence no window *can* close between them. The
empty list in the artefact is therefore corroborated by the schedule, not merely
observed — and the invariance survives future data as long as the cadence holds,
which is a stronger statement than the artefact makes for itself.

**The mislabelled field — FIXED in evidence v2**
(`a37516cf7dffa7a0a00eaee4419c30f35f3e8a8cc3cbe0da0b3afe237611dc14`). The empty
`class_b_windows` is renamed `closed_not_excluded_at_stamp_instant`, which is
what it measures. **Verified relabel-only:** every key shared between v1 and v2
carries an identical value; one key renamed, four added (the amendment note, the
artefact version, the boundary-invariance check, and v1's digest). Nothing was
re-measured. v1's bytes are preserved and remain the artefact §1 quotes.

## 6. The paired-bins floor (your item (a)) — and a hazard in setting it now

Supported, and the data argues for it independently. Measured on the shadow
rows, the extrapolation multiplier `72 / bins_paired` spans **×1.4 to ×72**:

| vessel | bins | multiplier | proxy lead (h) | ranking correct |
|---|---|---|---|---|
| …6370 | 1 | **×72.0** | 45.7–45.7 | ✗ |
| …7170 | 2 | ×36.0 | 23.5–47.5 | ✓ |
| …7000 | 34 | ×2.1 | 6.7–53.7 | ✗ |
| …7000 | 34 | ×2.1 | 6.0–53.0 | ✓ |
| …7000 | 38 | ×1.9 | 6.0–29.0 | ✗ |
| …7000 | 51 | ×1.4 | 6.5–53.5 | ✓ |
| …0469 | 51 | ×1.4 | 6.5–53.5 | ✗ |

The `bins` column makes this visible per row, but **the summary pools a ×72
extrapolation with a ×1.4 one as equal evidence** — `ranking_correct 3/7`
weights them identically.

The ×72 row is also the weakest on every other axis at once: fewest bins,
longest proxy lead, single bin. Your own GEFS atlas puts vector RMSE at ~45 h
near 2.3–2.6 m/s against ~1.8–2.0 m/s at 30 h, so its proxy is the noisiest as
well. It is the row a hostile reader finds first.

**THE HAZARD.** I have computed what each floor does to the headline, and so
will you:

    floor  1 bin  (≤ ×72)   7 scored, 3/7 = 43%
    floor  2 bins (≤ ×36)   6 scored, 3/6 = 50%
    floor  8 bins (≤ × 9)   5 scored, 2/5 = 40%
    floor 18 bins (≤ × 4)   5 scored, 2/5 = 40%
    floor 36 bins (≤ × 2)   3 scored, 1/3 = 33%

Choosing the floor after seeing that table is post-hoc selection — the same
shape as widening a grid after a VAL result. **Publishing the table is the
mitigation, not the offence**: the exposure is now declarable and its size is
measurable.

And its size is small. The headline moves 33–50% across the whole range, which
at n ≤ 7 is one row either way. **So pin the floor on the multiplier argument —
what extrapolation a reader would accept from a partially covered window — and
declare that the shadow table was visible when it was set.** My recommendation
is a floor expressed as a **multiplier bound**, not a bin count: a bin count
means nothing to a reader, whereas "no row is scored whose margin is
extrapolated more than ×N from covered bins" states the claim being made. Rows
below the floor become UNSCORABLE with the cause named, never dropped — §7
already has that shape.

## 7. The denominator (this is the one I would fix first)

`ranking_correct 3/7` is **not seven independent observations.**

- 7 scored rows come from **4 vessels**.
- One hull (…7000) supplies **4 of the 7 — 57%**.
- Its four windows **overlap by 5%, 24%, 38%, 58% and 67%** of a 72 h window.

Overlapping windows on one hull share track, wind field and synoptic state.
CLAUDE.md's standing rule is exact about this: *the denominator is the
independent EPISODE, not rows*, and interval estimates over serially correlated
series are block-bootstrap intervals blocked at the episode scale.

§7's `block_len = ⟦INTEGRATION: 5⟧ windows` already anticipates blocking, but
blocking by **window** does not fix this — the correlation here is *within one
vessel across overlapping windows*. **Blocks should be keyed on the vessel, or
on the vessel-window cluster, not on window index.** That is a pre-registration
decision and it is cheaper to make now, at n=7, than after 30 rows exist.

## 8. Selection (your item (b)) — measured, and stronger than "bursts"

Across the 12 rows, **the scored and unscorable sets are disjoint by vessel**:

- 4 vessels appear only in scored rows;
- 5 vessels appear only in unscorable rows;
- **0 of the 9 appear in both.**

If coverage failed by day, or at random, some hull would sit on both sides.
None does. **Coverage is a property of the vessel, not of the day** — so the
scored sample is a systematically selected subset of hulls: the well-received
ones. Well-received is not random with respect to geometry (proximity to
receivers, coastal transits), and the trial's population is therefore not the
target population.

This belongs in §5.4 as a declared selection effect, alongside the note that
the watchlist feed is unbuilt and selection currently reads the C1 store.

## 9. Two smaller things

**`sign_agree` and `ranking_correct` are identical on all 7 scored rows.** They
are distinct quantities in principle (the tie band can separate them) but they
coincide here, so reporting both suggests two independent measures where the
sample provides one. Worth a line saying so, or a reader double-counts.

**One `predicted_margin` is exactly `0.0` — RESOLVED 2026-09-09, computed zero.**
Raised in v2 as an ambiguity I could not settle from outside: a computed zero and
a "no alternative corridor" sentinel look identical in the register, and if it
were a sentinel its `abs_error` of 2,169 would be meaningless and would be
inflating the median. **It is a computed zero**, established two ways that do not
depend on each other:

- *From the data:* register entry `99beed5ed3dc…` has `corridor_current` ≡
  `corridor_preferred` on curve, sog, cog and rule — identical corridors force a
  margin of 0.0 (`s2c_reconciliation_20260909.json`).
- *From the code:* neither the scorer nor the emitter has a sentinel branch. The
  scorer never produces a `predicted_margin` at all; the emitter computes
  `margin = means[pref] − means[0]` arithmetically on every path, with no branch
  writing a literal `0.0`.

Two independent routes agreeing is the evidence. The row is also itself
§8-excluded, so it does not reach a score either way — but the convention it
would have tested is now stated in §1 rather than left to be inferred.

## 10. The §5.4 baseline exclusions, carried here because nothing else consumes them

**Measured first: no repo-side instrument reads a §5.4 reception baseline today.**
`naviguesser_overlay/f1_scorer.py` and `F1_SCORER_PREREG_v0.md` use the word
"baseline" in an unrelated sense — the *baseline route*, the counterfactual the
margin is computed against. **The two senses collide on the same word**, and that
collision is the reason to write the exclusions down explicitly rather than
"note them in the baseline instrument": a later reader wiring an exclusion into
the route baseline would be doing something meaningless and it would look right.

So the exclusions land here, in §5.4's selection-effect declaration, ahead of the
first figure that could be contaminated by them:

> **EXCLUDED INTERVALS — declared before any §5.4 reception or selection figure
> exists.** Consequence asserted here; **boundaries cited, never restated** —
> the constants are canonical in prereg Amendment A6 and in
> `accrual/INCIDENT_2026-09-07.md`, and the exclusion declaration
> (`accrual/f1_watchlist/BASELINE_EXCLUSION_2026-09-07.md`, sha256 `bfd5490c…`)
> carries the same discipline:
>
> 1. **Watchlist feed — the zero-reception interval is DEAD TIME, not quiet
>    time** (boundaries canonical in A6: go-live in A6's trigger paragraph,
>    relaunch in A6 item 4). The subscription was server-confirmed and never
>    serviced — `FiltersShipMMSI` with no `BoundingBoxes` companion, in
>    violation of the accrual line's pinned API contract (`AISSTREAM_ACCRUAL_PREREG.md`
>    `1fd9c8d8…` line 17, `BoundingBoxes` *required* since 2026-08-20), which the
>    server enforces **silently**. No reception rate, no selection-day traffic,
>    and no "connected and quiet" reading may be drawn from this interval. The
>    stale-kills within it are a guard reacting to a subscription defect and are
>    not evidence about watchlist traffic.
> 2. **C1 store — the 09-07 whole-tree outage window, cause unknown**
>    (boundaries canonical in `accrual/INCIDENT_2026-09-07.md`). Any §5.4 figure
>    drawing on the C1 store across that window excludes it or declares it.
>
> **Reception measurement begins at the relaunch instant** (A6 item 4), not at
> first contact — see the finding below.

**RULED 2026-09-10 (ruling 4): the anchor is the relaunch instant, not first
contact.** The reasoning, kept because it is why the ruling went that way, and
because the owner-side declaration still needs amending to match. Starting
a reception baseline at the first received frame excludes the connect-to-first-
frame latency **by construction** — every reception-rate figure so anchored is
biased slightly fast, and a "time to first frame" figure becomes undefined rather
than measurable. It is 1 min 52 s and changes nothing numerically today; it is
worth fixing now because it is a pre-registration, and because the shape — set
the start of measurement at the first success — is the one that is invisible once
rows exist. (The #14 half of this finding is **closed**: A6 v2 makes each instant
canonical in one place and cites rather than restates. What remains is the
substantive choice of anchor, which is the owner's to rule on; this draft takes
the relaunch instant and flags the divergence rather than adopting it silently.)

## 11. What I verified before writing any of the above

- md ↔ json: **320 values across the atlas**, 0 mismatched; the shadow table's
  12 rows reconcile against the JSON.
- Summary re-derived independently: scored 7, unscorable 5, ranking correct 3,
  median |error| 2,022.7732, sign agreement 0.428571 — all exact.
- `abs_error = |predicted − realised|` on every scored row, no mismatch.
- The declaration is well-formed: shadow status stated, no hit rate computed, no
  verdict attached, and the refusal to compute a hit is explicit about why.

## 12. The measurement instrument, and the defect found in it

The counts and the table in §1 were produced by `_s3_pin_regenerate.py`
(`b1f74cc68c4b6c677b15bc9f408a9340579160fbd948cae8e615e54f941ee2ac`, 8,778 B),
run owner-side against the real register. It is recorded here because a figure
whose instrument is not named is a figure nobody can re-derive.

**A defect in it, found by running it, and mine.** The pins lookup assumed
`pins.json` was a dict keyed by pin name. It is a **list**. The instrument
therefore could not find `F1_SCORER_PREREG_v0.pinned_utc` and refused, citing
ruling 7.

**The refusal was correct behaviour on a wrong assumption**, and that is the
part worth keeping. Written the other way — defaulting the instant when the
lookup missed — it would have measured against a silently substituted boundary
and produced a table that looked right. Instead it stopped and named the field it
could not find. The guard fired on its author's own mistake, which is the only
real test a guard gets.

Patched owner-side: **lookup only, semantics untouched, original bytes
preserved.** The measurement is unaffected — the governing instant it read,
2026-09-08T12:11:25Z, is the same instant ruling 7 designates, and the counts it
produced reconcile.

**Carried as a standing note:** the repo-side half of this project holds no
`accrual/` tree and no `timestamp/pins.json`, so any instrument written here
against those files is written against an *assumed* schema until it is run. Two
shapes were anticipated for the register rows and both were handled; the pins
file was not, because only one shape was imagined. The lesson is narrow and
specific — **anticipate shapes for every file an instrument reads, not just the
one whose schema was under discussion** — and it cost one refusal rather than one
wrong table, which is the trade the refusal-first design bought.

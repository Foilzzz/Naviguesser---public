# Correction-log entry — for landing (2026-09-08)

Status: **v1, for landing.** Numbered **36** on the best-known spine state (log ended at 34; the
vacuous-guard entry lands as 35; the PR #90 transcribed-constant instance was recommended its own
number — if that landed as 36, this becomes **37**). The number is CC's landing fact, measured
against the repo-side log; this workspace cannot measure it. Container format per the established
convention: `## N — YYYY-MM-DD — short title`.

---

## 36 — 2026-09-08 — the retroactive pin

**Failure shape: the retroactive pin — a pre-registration whose proof of priority is younger than the first measurement it governs.**

The F1 scorer's pre-registration carries a status line, written when it was drafted 2026-09-03,
requiring it to be pinned and OTS-stamped *before the first 72-hour guidance window closed*. It was
not. The scoring rule was not pinned before the first window closed — there is no softer statement
of the cause, and none is offered. The first window closed 2026-09-02T21:09Z; the pin landed
2026-09-08T12:11Z. For six days the programme emitted scored-able predictions with a scoring rule
that existed only as a draft under discussion — exactly the "we always meant to measure it this
way" the programme accuses the industry of. A draft under discussion is not a pin, and this entry
does not argue that it is one.

**The exposure, named and counted.** Measured from `accrual/f1/register.jsonl` at
2026-09-08T12:05Z (sha256 over the register read at that instant governs; the count is derived,
never transcribed), **15 windows** closed before the pin. Each is **EXCLUDED-BY-PREREGISTRATION**
from the scored record — not scored quietly, not scored under a rule written afterwards. Named by
full `guidance_id`:

| # | guidance_id | mmsi | issued_utc | window_close |
|---|---|---|---|---|
| 1 | 5d6825f9f21419f8dbf0505d946c1d3d025ebd64a71ad445eb59be9a699e40ac | 211526370 | 2026-08-30T20:09:02.550113Z | 2026-09-02T21:09:02.550113Z |
| 2 | 1a5f35782ad57e9eed8a6f5fefd2999835741050ccf0199f26372d27666c141c | 211870240 | 2026-08-30T20:09:02.550113Z | 2026-09-02T21:09:02.550113Z |
| 3 | ad2eb0c25f4710625955e3602953757c461d2118ab9883ef5dc70a0feedb2c17 | 255806485 | 2026-08-30T20:09:02.550113Z | 2026-09-02T21:09:02.550113Z |
| 4 | 7532e28f37c2ce7161b670174b545b5280f3c6a0f487d871cecf1c2a4b4fed56 | 353791000 | 2026-08-30T20:09:02.550113Z | 2026-09-02T21:09:02.550113Z |
| 5 | 99beed5ed3dc03cc82e6910cb1bd05f3cfdff055f3dd1c77a146eaaf0a893a99 | 246657000 | 2026-08-30T20:09:02.550113Z | 2026-09-02T21:09:02.550113Z |
| 6 | 7d4e4a0a77279d5e2b8042e8d09f62f5ac2875bca4fc04c36a21027306d2dd40 | 246657000 | 2026-09-01T16:30:37.591800Z | 2026-09-04T17:30:37.591800Z |
| 7 | c4df82fc60414fc5946191b7026f5cc59fd1f413645d107e4b67dbbabcf8009a | 246657000 | 2026-09-02T16:31:25.051672Z | 2026-09-05T17:31:25.051672Z |
| 8 | 40c22ad211a0e62b27c2a11bcfd1ad64c7b0729b413354e4896f9864b554fdcc | 636013757 | 2026-09-02T16:31:25.051672Z | 2026-09-05T17:31:25.051672Z |
| 9 | 906206244e6f7ea14f9b5b9ae55e4ad1dec8e96b0d78a44136ed6370f42a8e7a | 205509390 | 2026-09-02T16:31:25.051672Z | 2026-09-05T17:31:25.051672Z |
| 10 | 654e330d2e7a047b94e1c265dbf0edb721abe06220d4b32c7ae74ccce2555fee | 246657000 | 2026-09-03T22:58:33.489200Z | 2026-09-06T23:58:33.489200Z |
| 11 | 8a00668b9a15a7ea990de58c4c7894a16bd1266c3460c87093d938ed45b48ed3 | 368057170 | 2026-09-03T22:58:33.489200Z | 2026-09-06T23:58:33.489200Z |
| 12 | 622268bcd19a5dd68ffddb71d0c6121ea050aa58d94cdb328687bd56223c332b | 244050469 | 2026-09-03T22:58:33.489200Z | 2026-09-06T23:58:33.489200Z |
| 13 | 654bc1acfd1f4febdb338079da2e99b50e69d8dd529fc23fa7e6b4292fa8dfc4 | 246657000 | 2026-09-04T16:31:17.264610Z | 2026-09-07T17:31:17.264610Z |
| 14 | be49b35d3cdff139d0a91f3f40b234b6f1f94100fc0fce7a25b4040823e5f809 | 368057170 | 2026-09-04T16:31:17.264610Z | 2026-09-07T17:31:17.264610Z |
| 15 | 4dedf34cfd8652f4fdfe04c64ef67512ed1983de20c4882009688284ee9b5efd | 244050469 | 2026-09-04T16:31:17.264610Z | 2026-09-07T17:31:17.264610Z |

The audit that caught this counted twelve; the register shows fifteen at the pin's measurement
instant. The difference is measurement time — three more windows closed while the ruling was in
flight. A count that grows while the fix is being arranged is the exposure this shape names, and
it is stated here rather than reconciled away.

**The residual, stated accurately.** Those fifteen emissions were sealed at emission time — each
carries its own hash-chained register entry, and the register's anchoring is separately receipted.
They remain valid sealed predictions. What they lack is a pre-committed scoring rule. **Any third
party may score them under any rule they choose, and we will publish the result whatever it says.**
That offer is part of this entry and does not expire.

**What changed.** `F1_SCORER_PREREG` v0 was pinned 2026-09-08T12:11Z (pins register entry 24,
sha256 `199be2e3e1393fa4667f44ca97240b17658f144de31b1b3db8097617a4ab7138`, OTS-stamped the same
day) and governs every window closing after the pin. The exclusion is codified as §8 of the pinned
document itself, relative to the stamp instant — so the rule, not this entry, is what a future
reader checks. The missed deadline is declared in the document's own status line, with the draft
line preserved unaltered beside it.

**Caught by:** the 2026-09-04 state-of-play audit — the same review that found the receipts had
never been upgraded. One audit, two instances of the same deeper shape: a ceremony performed
(write the prereg, run `ots stamp`) mistaken for the property the ceremony exists to establish
(priority, anchoring). The property was never checked because the ceremony felt like the check.

**Publication note.** "Published", today, means staged in the owner-side `public/` tree pending
D2 deployment — the surface this entry exists on is not yet publicly reachable, which is its own
remediation item and is not hidden here. This entry moves to the public URL the day D2 closes.

---

## Cover note for the relay (not part of the entry)

- Numbering depends on the repo-side spine, which this workspace cannot measure: 36 if the #90
  instance was not separately logged, 37 if it was. CC's measurement at landing governs; renumber
  the container and this note together.
- The 15 IDs above were generated from `accrual/f1/register.jsonl` in the same pass that measured
  the count — quoted from that output, not from a stale listing.
- Landing moves the figure set (FIG-04/05/06 class) if the memo concordance counts log entries;
  the repin rides the landing commit, figure-only, declared in the repin line — same handling as
  entry 35.
- The third-party scoring offer in the entry is load-bearing for the residual claim. It costs
  nothing to make and everything to quietly drop; it stays.

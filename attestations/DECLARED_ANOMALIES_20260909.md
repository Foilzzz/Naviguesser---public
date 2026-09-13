# DECLARED ANOMALIES — attestations directory, 2026-09-09

This directory publishes the programme's attestation sidecars and their
OpenTimestamps receipts. Two declared anomaly classes are present, published
rather than hidden, per the programme's correction-log posture. Measured
2026-09-09 by a full verification pass (44/47 fully verified, zero receipts
pending; merkle paths cross-checked against two independent block explorers).

## (a) Retention-gap subjects — 4 sidecars

`1d02c2c7…`, `ecf9408c…`, `697fedc6…`, `e0c6d2cb…`

These sidecars attest digests whose subject documents are currently held only
in the programme's private git history (repo-side pinning predated owner-side
retention). Recovery of the four blobs by digest is in flight. The pin proves
a document with this digest existed by the anchor date; it does not, today,
let a reader check what it said. That gap is the finding, and it is declared.

## (b) Sidecar drift — 3 receipts fail file-binding

`1d02c2c7…`, `bfaf9a58…`, `ecf9408c…`

For these three, the Bitcoin anchor verifies, but the `.att.json` on disk is
not the byte sequence the receipt attests (the sidecar moved after stamping;
the programme's D1 remediation declared this on 2026-09-08). `ots verify` on
these three pairs fails today. Re-binding is mechanical where the subject
document is held (`bfaf9a58…`); the rest wait on (a).

A standing monthly integrity pass re-verifies every pinned artefact against
its stored digest; a mismatch on this tier is an incident, not an edit. This
file is amended, never rewritten: new anomalies append; resolved ones are
struck by a dated amendment line, not deleted.

---

## Amendment — 2026-09-12

**Class (a) is now 3 subjects, not 4.** `e0c6d2cb…` (T2_LIVE_PREREG_v02_repo)
is cured: the bytes were recovered from the programme's owner-side repository
mirror and hash to exactly the pinned digest
(`e0c6d2cb9f093fddd918af6f92d06b38d5d6017fcd1353abd962e29ee4421c58`, 9,073 B).
The pin is now checkable against the bytes, not only the digest.
`1d02c2c7…`, `ecf9408c…` and `697fedc6…` remain digest-only.

**Class (b), `bfaf9a58…` — re-binding executed, anchoring pending.** The
subject document (F1_FORWARD_GUIDANCE_TRIAL_PREREG_v03) is held and
digest-verified, so the re-binding the text above called mechanical was done:
the sidecar's current bytes were re-stamped 2026-09-12. The sidecar's own
content declares v03 superseded by v05 (`697fedc6c3d90ac5…`), and that
declaration is part of what the new receipt binds. The drifted receipt is
preserved beside the pair (`bfaf9a583801a282.att.json.ots.drifted-20260908`)
— never deleted. At this writing the new receipt is pending Bitcoin
confirmation; the daily anchoring monitor enforces the 24 h fresh-stamp
grace, and this line is struck when anchoring confirms. `1d02c2c7…` and
`ecf9408c…` still fail file-binding and wait on class (a).

**Two counts, two properties, both true.** The 44/47 figure above is the
2026-09-08/09 full verification pass — it measures *file-binding* (receipt
matches the bytes on disk). The daily anchoring monitor measures a different
property — whether each receipt is Bitcoin-anchored — and read 48/48 anchored
on 2026-09-11 (the register has grown since the pass). A reader should not
reconcile the two numbers against each other; they count different things.

*Amendment mechanics: appended, never rewritten, per this file's own rule.*

---

## Amendment — 2026-09-13

**Class (b), `bfaf9a58…` — anchoring CONFIRMED; the pending line in the 2026-09-12
amendment is struck.** The re-stamp anchored at **Bitcoin block 966574** (merkle root
`9584a7ccd1ff0402ac944b1aba60beca2793edda84ddce3b1d776444a727f47d` in the receipt).
The upgraded receipt also passes file-binding against the sidecar on disk — receipt and
sidecar both hash to `a146bb7a9917a22c1d53062e1092ace37f1016d9b71960ea95677d94eaa73575`
— so this subject is fully cured on both properties the classes measure: anchor and
bytes. Prior receipt states are preserved beside the pair
(`.ots.drifted-20260908`, `.ots.pending`, `.ots.pre-upgrade-20260913`) — never deleted.

Class (b) is now **2 subjects** (`1d02c2c7…`, `ecf9408c…`), both still waiting on
class (a), which stands at 3.

---

## Amendment — 2026-09-13 (second)

**Class (a) is now 2 subjects, not 3.** `697fedc6…`
(F1_FORWARD_GUIDANCE_TRIAL_PREREG_v05) is **cured**: the pinned bytes were recovered
from `CC_UPLOAD_F1_A5_LANDING_2026-08-30.zip` (member
`F1_FORWARD_GUIDANCE_TRIAL_PREREG.md`) and hash to exactly the pinned digest
(`697fedc6c3d90ac51f36b39281273f14fc86092dfc6b52f3840514f77bab4c14`, 30,327 B).
The recovered bytes are preserved beside the register at
`corpus_intake/F1_FORWARD_GUIDANCE_TRIAL_PREREG_v05_PINNED_697fedc6.md`. The live
document at the pinned path is v06 (Amendment A6), pinned separately under
`709269bd…` and verified against it today.

**`1d02c2c7…` (v04) and `ecf9408c…` (v05 first draft): hunted, not found — the gap
is now measured, not open.** Exhaustive owner-side hunt on 2026-09-13: every mid-size
blob in the repository mirror (1,479 candidates, raw and CRLF-normalised), and every
text file plus every text member of every zip in the owner workspace (23,386 files,
187 zips). Neither superseded byte sequence exists in anything held here — both were
amended in place within a day of pinning, before owner-side retention began. The pins
still prove each document existed by its anchor date; what is unrecoverable here is
the superseded *content*, and each pin's own note declares the succession
(v04 → v05 draft → v05 → current v06). The one remaining route is off-machine copies
(the relay counterparty's pack archive); it will be checked at the next session and
this line amended either way. Class (b) stays 2 subjects, waiting on exactly these
two — a re-bind has no subject to verify against until then.

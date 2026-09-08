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

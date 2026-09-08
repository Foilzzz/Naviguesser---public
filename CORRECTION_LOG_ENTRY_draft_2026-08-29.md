# Correction-log entry — v2 DRAFT for owner ruling (2026-08-29)

Status: **v2, supersedes v1 (2,430 B, `0ac2019f…140d`).** v1's family citations were mis-bound — measured by CC against the log before landing, exactly the check the entry itself argues for. Corrections: the centred-integral lesson and the PR #90 transcribed-constant instance are cited as *shapes*, not entry numbers (neither has a log entry); the false `#10/#11` and `#28` bindings are removed. CC's landing facts: the log ends at 34, so this lands as **35**; container `## N — YYYY-MM-DD — short title`; it moves FIG-04/05 (34→35) and FIG-06; collected/passed unmoved — a figure-only repin.

---

## 35 — 2026-08-29 — the vacuous guard

**Failure shape: the vacuous guard — a check that passes identically in the defective and the repaired state.**

A node guarding the C1 overlap finding asserted the finding's *superseded* status text. Because our amendment discipline keeps the original text in the document — quoted, marked superseded, never deleted — the superseded string is present in both versions by design. The node was therefore green on the defective version and green on the landed one. It guarded the existence of a string, not the property it was declared to guard, and no diff would ever have shown it.

Same family as the centred-integral lesson (a declared quantity that is identically zero for every possible input — branch-caught, carried in the trap list, never previously a numbered entry) and the transcribed-constant instance landed at PR #90 (a node comparing a transcribed constant against itself, structurally blind to the repair it was declared to catch — also previously unlogged). Both cited as shapes, not numbers: neither has a correction-log entry at this writing.

The amend-annotated discipline makes this shape *more* likely, not less: superseded text stays findable forever, so any existence-check over a document is blind to supersession unless it checks the supersession marker itself.

**Caught by:** second-pass review at PR #94 — the discharge pass asked whether the node *could* fail, not whether it was green. (This entry's own citations were checked the same way before landing; v1 bound these shapes to entry numbers they do not belong to, and the binding was corrected pre-landing.)

**What changed:** the node now asserts the finding's *live* status, red on the superseded version and green only on the landed one. The standing rule — codified in the 2026-08-27 drill-discipline PR and enforced over every drill script — covers the general case: any guard that expects failure must assert what the failure said. A guard that cannot fail is not a guard; a green bar over one is a false receipt.

---

## Cover note for the relay (not part of the entry)

- Number 35 per CC's measurement (log ends at 34, spine contiguous); container format `## N — YYYY-MM-DD — short title`.
- Landing moves FIG-04/05/06 — memo concordance repin rides the landing commit, figure-only, declared in the repin line.
- **Open follow-on ruling for the owner:** CC notes the PR #90 transcribed-constant instance has never been logged. If it merits an entry it should land as its own number (36) on its own text, not as a back-reference inside 35. Recommended: yes — the two entries cite each other, and the log's value is the taxonomy.

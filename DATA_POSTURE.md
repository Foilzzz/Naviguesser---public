# Data posture — plain words (2026-09-08, owner ruling R3)

This page states how Naviguesser holds its data. It is published because stating it is stronger
than being found out.

**AIS data.** Our live vessel-position record is accrued from AISStream, a free service that
publishes **no terms of service and no licence** (checked 2026-09-02; its documentation states no
restriction of any kind). The underlying AIS messages are public safety broadcasts.

What we do with it: **derived products only.** We never redistribute raw AIS records. Anything
that leaves this programme carries digests, counts, and aggregates — never vessel tracks, never
raw frames, never anything reconstructible into one. This is not a preference; it is enforced by
an automated check (audit check A14) that scans every published artefact — including the inside
of every pack we ship — and blocks publication if a position record appears.

**The licence question is OPEN, by owner decision.** We have not asked the operator for written
terms, and we will not until the programme moves to a paid, licensed AIS provider, which is the
intended cure on funding. Until then the exposure is ours and it is stated here, not discovered
later.

**The founding race corpus** — the historical sailboat instrument logs our calibration derives
from — **is used under no written licence.** It was obtained with informal permission. It is
never redistributed, never committed to a shared repository, and never present in any shipped
artefact; published figures derived from it carry its digest and row basis, not its bytes. A
retrospective written licence is a counsel question in the current brief.

**Weather data.** NOAA model output is US Government public domain. ERA5 and CMEMS products are
Copernicus data under their attribution licences, obtained under our own accounts.

**The asset is not the data.** AIS is broadcast public information. What this programme owns is
the *provable custody* of it: the unbroken, hash-chained, independently timestamped record, the
pre-registered methods, and the correction log you are reading this on.

*Audit check A14, the risk-register entry for the open licence question, and this page's own
digest are all part of the public record. If anything here ever stops being true, the correction
log will say so.*

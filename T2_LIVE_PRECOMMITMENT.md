# Public pre-commitment: the live fleet-drift verdict

**Naviguesser · 2026-08-28**

We are committing, publicly and in advance, to a result we have not seen.

## What is being measured

Since 26 August 2026 we have been collecting live AIS vessel-tracking data across four declared coastal-approach zones, under a published methodology. Each day's data is hash-pinned into an append-only register at daily close-out. When a day stops without a clean seal — two already have — it is declared in the same record with its cause, its gaps and its rejects, never bridged or smoothed. Over eight consecutive weekly windows we will measure whether the fleet's observed speed behaviour **drifts** — whether the same kinds of vessels, in the same places, move measurably differently at the end of the period than at the start.

The exact statistic and drift metric are being pinned inside the pre-registration **no later than 4 September 2026**, and in any case before the first window opens — window 1 does not start until they are fixed. Each fill lands as a dated, versioned amendment with its own hash, **published to this page at the moment it is pinned**. No statistic will be chosen after seeing the data it describes.

## The bound, pinned before any window closed

Cross-window drift exceeding **1.0 knot** = the trial reports the fleet's behaviour moved beyond the bound. Pinned 27 August 2026, before window 1 exists. Its source chain is public and checkable: AIS speed over ground is broadcast in 1/10-knot steps (ITU-R M.1371, SOG field) — the bound sits ten times above the instrument's floor — and real fleet speed variation is larger than the bound: Goicoechea & Abadie 2021 (*Energies* 14(22):7487, DOI 10.3390/en14227487) put the economically optimal container speed's own movement at ~1.8 kt across 2018–2019. (Source chain amended 29 August 2026 — see Amendments below.)

## The windows

Eight weekly windows: declared, ordered, non-overlapping. Window 1 is the first ISO week fully sealed *after* a day-7 operational calibration gate passes **and after the drift statistic has been pinned and published** — if the statistic is not pinned, window 1 does not open, and the delay is declared here, not absorbed silently. Calibration data never enters the verdict windows. A window with fewer than six of seven days sealed is declared insufficient, never silently thinned. The verdict follows within seven days of the eighth window sealing; on current scheduling that lands in the first week of November 2026, and window 1's opening will be announced through this same channel when the gate passes.

## The blind line

No drift statistic is computed on the live data before the eighth window seals — including by us. Weekly operations measure coverage, storage and data-quality rejects only. If we break this rule, the pre-registration requires that we stop and say so.

## The pins

- Live-trial pre-registration (v0.2), sha256: `e0c6d2cb9f093fddd918af6f92d06b38d5d6017fcd1353abd962e29ee4421c58`
- Accrual pre-registration (the collection methodology), sha256: `1fd9c8d8ec750e13ac7e08189bb05290fa6eda491c0c6e1b53554d376ae5b700`
- Drift-statistic amendment, by 4 September 2026: its hash is added to this list at the moment it is pinned — before window 1 opens, so the pin's timestamp can be checked against the trial's start, not just its verdict.

When the verdict is published, these documents are published with it. Anyone can then check that the method was pinned before the measurement — the hash either predates the result or it doesn't.

## What this trial can and cannot say

It measures coastal-approach behaviour only — terrestrial AIS coverage, by declaration, no open-ocean claim. It says nothing about any single vessel, nothing about hull condition, and nothing denominated in fuel, CO₂, or dollars. Its sibling study — the same 1.0 kt bound, pinned before computation, applied to six pre-registered monthly windows of 2023–2024 archived data — has already closed: cargo 0.60 kt, tanker 0.40 kt, both within the bound. The two studies corroborate each other; they are never merged into one claim.

## The commitment

The verdict, the per-window table, the full pre-registration with its amendment chain, and the correction-log entry for anything that went wrong along the way — **we will publish all of it, whatever it says.**

*Naviguesser — routing decisions that carry their own confidence.*

## Amendments

**29 August 2026 — citation verification of the bound's source chain.** The sentence originally read: *"Its source chain is public: ISO 19030-2's 1 kt reference-condition filter (via the HiPer2022 reproduction of the ISO filter table, on the public record); Goicoechea et al. 2021 (Energies 14(22):7487) measuring ~1.8 kt container-speed fluctuation in rougher conditions; and AIS speed quantisation of 0.1 kt — the bound sits ten times above the instrument's floor."* Verified clause by clause before publication. The AIS clause resolves at the primary standard — ITU-R M.1371 carries speed over ground in 1/10-knot steps. The Goicoechea citation resolves exactly as cited (DOI 10.3390/en14227487) but was mis-framed: the paper's ~1.8 kt is the movement of the *modelled economically optimal* container speed across freight-market conditions in 2018–2019, not a measurement of speed fluctuation in rougher weather — the sentence now states what the paper measures. The ISO 19030-2 / HiPer2022 clause could not be verified against any public source and is removed rather than left uncheckable. The 1.0 kt bound itself is unchanged and remains pinned before any window closes; this amendment touches only its stated justification.

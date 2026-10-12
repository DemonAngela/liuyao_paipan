# Sources, Scope, and Rule Provenance

The project encodes traditional Liuyao concepts as software, but traditional literature and modern schools do not always define every edge case identically. This document defines how rule provenance is handled in maintenance.

## Scope

The codebase currently covers:

- 64-hexagram and 384-line reference text/data;
- Najia and palace/hexagram metadata used by the production engine;
- Liuqin, Liushen, Shi/Ying, Xunkong, moving-line and transformed-hexagram data;
- Ganzhi/calendar calculations used by the engine;
- selected Sheng/Ke/Chong/He and strength-state relationships;
- an experimental time-divination endpoint whose traditional rule mapping is not yet considered stable.

## Evidence policy

A change to traditional-rule behavior should include at least one of the following:

1. a clearly identified classical or modern reference that can be independently checked;
2. a reproducible reference implementation with its version recorded;
3. an explicit project convention when multiple credible interpretations differ.

In every case, the expected result should be encoded as a regression test before or with the production change.

## Calendar baseline

Ganzhi year/month boundaries now use `lunar_python==1.4.8` as the pinned reproducible software reference. The production implementation uses that library's exact Lichun/monthly-`jie` transition semantics rather than fixed Gregorian dates.

The project explicitly chooses the same-civil-day late-Zi convention (`Exact2` / sect 2): `23:00-23:59` does not advance the day pillar early. The hour stem is derived from that chosen day stem.

This closes the former fixed-date approximation tracked in issue #1. The pinned implementation is a deterministic verification baseline, not a claim that one modern library or one traditional school is universally authoritative. A credible conflicting source should be documented as a reproducible rule-accuracy case rather than silently overriding the baseline.

Detailed regression scope is documented in [`VALIDATION.md`](VALIDATION.md).

## Source hierarchy

Sources are not treated as interchangeable. Maintenance discussions distinguish:

- classical source text;
- later interpretive or school-specific rules;
- modern calendar/astronomical computation references;
- reproducible software reference implementations;
- implementation conventions chosen for deterministic software behavior.

When credible sources conflict, the issue or pull request should document the conflict instead of presenting one interpretation as universally authoritative.

## Data provenance

Static files under `backend/data/` should have a reproducible generation or verification path wherever practical. Generated reference data should not be hand-edited without a corresponding test or generator change. The stale backup generator was removed so it cannot be mistaken for a supported data source. Issue #4 continues to track consolidation of the remaining Najia/64-hexagram implementations into one auditable source of truth.

## Current high-risk provenance work

- Issue #2: cited and reproducible time-divination rules.
- Issue #4: single source of truth for Najia/64-hexagram metadata.
- Issue #5: deeper source-backed expectations for core relationships beyond structural/exhaustive path validation.

Project documentation intentionally uses qualified language where these items remain unresolved.

# Sources, Scope, and Rule Provenance

The project encodes traditional Liuyao concepts as software, but traditional literature and modern schools do not always define every edge case identically. This document defines how rule provenance should be handled in maintenance.

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

## Source hierarchy

Sources are not treated as interchangeable. Maintenance discussions should distinguish:

- classical source text;
- later interpretive or school-specific rules;
- modern calendar/astronomical computation references;
- implementation conventions chosen for deterministic software behavior.

When two credible sources conflict, the issue or pull request should document the conflict rather than presenting one interpretation as universally authoritative.

## Data provenance

Static files under `backend/data/` should have a reproducible generation or verification path wherever practical. Generated reference data should not be hand-edited without a corresponding test or generator change. Issue #4 tracks consolidation of duplicate Najia/64-hexagram implementations into a single auditable source of truth.

## Current high-risk provenance work

- Issue #1: precise solar-term/Ganzhi boundaries and month-pillar validation.
- Issue #2: cited and reproducible time-divination rules.
- Issue #4: single source of truth for Najia/64-hexagram metadata.
- Issue #5: broader core-rule regression and property tests.

Until those items are resolved, project documentation intentionally uses qualified language rather than claiming universal or absolute correctness.

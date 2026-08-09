# Validation and Reproducibility

This project treats rule correctness as a maintenance problem that must be reproducible, reviewable, and explicit about conventions.

## Ganzhi / solar-term baseline

The production calendar layer pins `lunar_python==1.4.8` as its reproducible reference implementation. That upstream project exposes computed solar-term instants and separate exact Ganzhi methods for year/month boundaries.

Project convention:

- year pillar changes at the exact Lichun (立春) transition;
- month pillar changes at the exact monthly `jie` (节) transition;
- late Zi hour (`23:00-23:59`) keeps the same civil-day day pillar (`Exact2` / sect-2 semantics);
- the hour stem is then derived from that same chosen day stem;
- the REST API remains hour-granularity for compatibility; the Python API accepts minutes so boundary behavior can be validated precisely.

This baseline is a deterministic software reference, not a claim that one school or library is universally authoritative. If another credible source disagrees, the difference should be filed as a rule-accuracy issue with a reproducible case.

## Fixed corpus

`tests/fixtures/ganzhi_reference_cases.json` stores human-readable fixed cases. The corpus includes a case published by the reference library and a project regression case.

`tests/test_ganzhi_reference.py` additionally verifies:

- January cross-year behavior from 2020 through 2029;
- one-minute probes around every monthly `jie` transition for 2024-2026;
- the explicit late-Zi-hour day-boundary convention;
- a full daily-noon comparison for 2020-2029 (3,653 samples), which must have zero year/month/day mismatches against the pinned baseline.

## Engine/data validation

The existing test suite also checks:

- all 64 hexagrams and 384 line records are structurally present;
- line yin/yang values and positions are valid;
- qigua input contracts and three-coin mappings;
- real HTTP API request/validation paths;
- the stable Python integration surface in `backend.public`.

Issue #5 tracks deeper domain regression/property coverage for Shi/Ying, Najia, Liuqin, Liushen, moving-line relationships, and the full 4,096 base-hexagram/moving-mask combinations.

## Maintenance rule

A confirmed domain bug should become a regression case before or with the fix. A change that alters calendar or traditional-rule behavior must identify its source or project convention in the pull request.

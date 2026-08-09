# Roadmap

This roadmap tracks maintenance work that can be verified in code, tests, issues, and releases. It is intentionally not a promise of dates.

## Completed reliability foundation

- Replaced fixed-date Ganzhi month/year boundaries with a pinned `lunar_python==1.4.8` exact solar-term baseline (issue #1).
- Added January cross-year, exact solar-term transition, late-Zi convention, and 2020-2029 full daily-noon reference regression coverage.
- Automated structural execution of all 4,096 base-hexagram/moving-line-mask combinations.
- Added an installable Python package surface for non-HTTP integrations.
- Added CI, CodeQL, Dependabot, Docker release publishing, SBOM/provenance metadata, and GitHub artifact attestations.

## Remaining rule reliability

- Resolve issue #2 with cited time-divination rules and fixed regression cases.
- Consolidate Najia/64-hexagram data into a single auditable source of truth (issue #4).
- Expand source-backed expected-value coverage for Shi/Ying, Najia, Liuqin, Liushen, Xunkong, moving-line transformations, and relationship calculations (issue #5).
- Keep domain limitations visible until regression evidence supports stronger claims.

## Maintainer workflow

- Keep CI green across supported Python versions.
- Review dependency updates rather than blindly auto-merging them.
- Keep security scanning and release provenance enabled.
- Use structured issue templates for bugs, usage reports, and rule-accuracy reports.
- Use Codex, when available, for PR-impact review, issue reproduction/triage, regression-test drafting, documentation consistency, and release preparation while retaining human approval for every merge.

## Interoperability and adoption

- Maintain a reproducible GHCR container release path.
- Maintain REST and Python integration examples.
- Convert genuine compatibility reports into regression fixtures.
- Keep English-facing documentation sufficient for non-Chinese-speaking maintainers and integrators.

## Stable release criteria

A stable 1.0 release should require, at minimum:

- high-risk rule areas either validated or explicitly excluded from the stable contract;
- documented REST and Python compatibility expectations;
- repeatable CI, security checks, container provenance, and release process;
- a meaningful set of genuine external usage reports or integrations rather than maintainer-only testing.

# Changelog

All notable maintenance-facing changes will be recorded here. The project follows a simple pre-1.0 compatibility policy: breaking changes are allowed when required for correctness or safety, but they must be documented and covered by tests.

## Unreleased

## 0.1.0 - 2026-08-09

First public maintenance-focused pre-stable release candidate.

### Added

- MIT license, contribution guide, security policy, code of conduct, maintainer policy, roadmap, and GitHub collaboration templates.
- English project overview, API integration examples, source/provenance policy, and real usage report template.
- CI across Python 3.10, 3.11, and 3.12 plus reproducible Docker image builds.
- CodeQL security analysis and Dependabot dependency maintenance.
- Tag-driven release workflow for tests, GHCR container publishing, and GitHub release notes.
- Regression tests for request validation, three-coin line generation, and core static-data integrity.
- Public tracking issues for high-risk calendrical, time-divination, reference-data, test-coverage, and adoption work.

### Changed

- Request models reject malformed six-line and date inputs before core calculations run.
- Automatic line generation uses the documented three-coin 6/7/8/9 distribution.
- Frontend flows use backend validation endpoints consistently and surface HTTP failures.
- CORS is opt-in instead of permissive by default.
- README distinguishes verified behavior from known or experimental limitations.
- API metadata is aligned with the pre-stable `0.1.0` release line.

### Security

- Internal exception strings are no longer returned directly from the paipan API.
- CodeQL runs on pull requests and on a scheduled basis.

# Changelog

All notable maintenance-facing changes will be recorded here. The project follows a simple pre-1.0 compatibility policy: breaking changes are allowed when required for correctness or safety, but they must be documented and covered by tests.

## Unreleased

### Added

- MIT license, contribution guide, security policy, code of conduct, maintainer policy, roadmap, and GitHub collaboration templates.
- CI across Python 3.10, 3.11, and 3.12.
- Regression tests for request validation, three-coin line generation, and core static-data integrity.
- Public tracking issues for high-risk calendrical and time-divination correctness work.

### Changed

- Request models now reject malformed six-line and date inputs before core calculations run.
- Automatic line generation now uses the documented three-coin 6/7/8/9 distribution.
- Frontend flows use backend validation endpoints consistently and surface HTTP failures.
- CORS is opt-in instead of permissive by default.
- README distinguishes verified behavior from known or experimental limitations.

### Security

- Internal exception strings are no longer returned directly from the paipan API.

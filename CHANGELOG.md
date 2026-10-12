# Changelog

All notable maintenance-facing changes are recorded here. The project follows a pre-1.0 compatibility policy: breaking changes are allowed when required for correctness or safety, but they must be documented and covered by tests.

## Unreleased

## 0.2.0 - 2026-08-09

Correctness and interoperability release focused on making maintenance evidence reproducible.

### Added

- Pinned `lunar_python==1.4.8` as the reproducible Ganzhi/solar-term software baseline.
- Fixed validation corpus plus exact solar-term boundary tests, January cross-year tests, and explicit late-Zi-hour convention tests.
- Full 2020-2029 daily-noon comparison (3,653 samples) requiring zero year/month/day mismatches against the pinned baseline.
- Automated structural validation of all 4,096 base-hexagram/moving-line-mask engine paths.
- Installable Python package metadata and the small public `calculate_ganzhi` / `paipan` integration surface.
- Python integration and validation documentation.
- Release SBOM/provenance metadata and GitHub artifact attestation for published container images.

### Changed

- Replaced fixed-date year/month pillar approximations with exact Lichun/monthly-`jie` transition semantics from the pinned reference implementation.
- Documented the same-civil-day (`Exact2` / sect-2) late-Zi convention as an explicit project choice.
- Updated Uvicorn to 0.52.1.
- Updated checkout/setup-python and Docker release actions to Node 24-compatible major versions.
- CI now verifies editable package installation and the public Python integration surface across Python 3.10, 3.11 and 3.12.
- Removed the stale backup 64-hexagram generator so it cannot be mistaken for a maintained data source.

### Security / supply chain

- Release images include SBOM and max-level provenance metadata.
- GitHub build attestations bind the published GHCR image name to the digest produced by the release build.

## 0.1.0 - 2026-08-09

First public maintenance-focused pre-stable release.

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
- API metadata is aligned with the pre-stable release line.

### Security

- Internal exception strings are no longer returned directly from the paipan API.
- CodeQL runs on pull requests and on a scheduled basis.

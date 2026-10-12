# Liuyao Paipan

[![CI](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/test.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/test.yml)
[![CodeQL](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A reproducible open-source implementation of Liuyao (Six-Line I Ching) rules as inspectable software. The repository provides a Python integration API, FastAPI REST API, browser UI, structured 64-hexagram data, regression tests, Docker images, and explicit rule-provenance documentation.

> **Status: actively maintained, pre-1.0.** The project is for study, research, software verification, and reproducible discussion of traditional rules. It is not presented as the only authoritative interpretation and is not intended for medical, legal, financial, or other high-stakes decisions.

## Implemented surface

- three-coin six-line generation using the 6/7/8/9 distribution;
- manual and explicitly specified hexagrams;
- Najia, Liuqin, Shi/Ying, Liushen, Xunkong, moving lines and transformed hexagrams;
- selected Sheng/Ke/Chong/He relationship calculations;
- 64 hexagrams and 384 line-text records;
- reproducible Ganzhi year/month boundaries based on exact solar-term transition instants;
- a small Python-facing integration API;
- FastAPI REST endpoints and a browser UI;
- an experimental time-divination endpoint kept outside the stable rule contract.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m backend.main
```

Open `http://127.0.0.1:8000` or inspect `/docs`.

### Python integration

```python
from backend import calculate_ganzhi, paipan

ganzhi = calculate_ganzhi(1986, 5, 29, 0, 0)
chart = paipan(
    [1, 1, 1, 1, 1, 1],
    year=2026,
    month=4,
    day=23,
    hour=10,
)
```

The supported integration surface and input conventions are documented in [`docs/PYTHON_API.md`](docs/PYTHON_API.md).

### Docker

```bash
docker build -t liuyao-paipan .
docker run --rm -p 8000:8000 liuyao-paipan
```

Tagged releases publish a GHCR image. The release workflow also generates SBOM/provenance metadata and a GitHub artifact attestation for the container digest.

## Calendar validation

Ganzhi calculations pin `lunar_python==1.4.8` as a reproducible software reference. Year and month pillars use that reference implementation's exact solar-term transition instants. The project explicitly uses the same-civil-day (`Exact2` / sect-2) convention for `23:00-23:59`.

This is a documented deterministic project baseline, not a claim that one library or school is universally authoritative. See [`docs/VALIDATION.md`](docs/VALIDATION.md) and [`docs/SOURCES_AND_SCOPE.md`](docs/SOURCES_AND_SCOPE.md).

CI protects this behavior with:

- fixed human-readable reference cases;
- January cross-year checks for 2020-2029;
- one-minute probes on both sides of all 12 monthly `jie` transitions for 2024-2026;
- an explicit late-Zi-hour convention test;
- a 3,653-day daily-noon comparison for 2020-2029 that must have zero year/month/day mismatches against the pinned baseline.

## Broader verification

Pull requests run Python 3.10/3.11/3.12 tests, backend compilation, package-install/import checks, Docker builds, and CodeQL. The suite also validates request boundaries, three-coin mapping, 64-hexagram/384-line data integrity, real HTTP routes, the public Python API, and all 4,096 base-hexagram/moving-line-mask combinations structurally.

Dependabot maintains Python and GitHub Actions dependencies. Domain-rule changes require a reproducible case plus either a checkable source/reference or an explicit project convention.

## Known limitations

1. **Time divination remains experimental.** `/api/qigua/time` currently uses a simplified Gregorian-number algorithm and is not claimed as a fully cited traditional year/month/day/hour method; issue #2 tracks that work.
2. **Some strength and relationship rules are engineering simplifications.** They need more source-backed fixed cases before stronger compatibility claims are made.
3. **Najia/reference-data duplication still needs consolidation.** Issue #4 tracks a single auditable source of truth.
4. **Deeper semantic regression coverage is still expanding.** The 4,096 engine paths are now structurally exercised, while issue #5 tracks more source-backed expectations for Shi/Ying, Najia, Liuqin, Liushen and moving-line relationships.

## Maintenance evidence

The repository publishes its maintenance model rather than treating maintenance as invisible work:

- [`MAINTAINERS.md`](MAINTAINERS.md) — ownership and decision policy;
- [`ROADMAP.md`](ROADMAP.md) — reliability and interoperability work;
- [`CHANGELOG.md`](CHANGELOG.md) — compatibility/security changes;
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution requirements;
- [`SECURITY.md`](SECURITY.md) — vulnerability reporting;
- [`docs/RELEASING.md`](docs/RELEASING.md) — tested release process;
- [`docs/MAINTAINER_AUTOMATION.md`](docs/MAINTAINER_AUTOMATION.md) — PR review, triage, testing and release automation boundaries;
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — regression and reference-baseline policy.

Useful Codex maintainer work includes PR-impact review, issue reproduction, regression-test drafting, rule/data consistency checks, documentation/API consistency, dependency/security review, and release preparation. AI output remains subject to maintainer review and is never accepted by itself as evidence for a traditional-rule claim.

## Contributing

Bug reports, source-backed rule corrections, regression cases, documentation improvements, accessibility fixes, and real integrations are welcome. The project records only genuine public adoption signals and does not manufacture stars, forks, downloads, or interactions.

## License

MIT. See [`LICENSE`](LICENSE).

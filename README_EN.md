# Liuyao Paipan

[![CI](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/test.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/test.yml)
[![CodeQL](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source Liuyao (Six-Line I Ching) engine and web application built with Python, FastAPI, and vanilla JavaScript. The project turns traditional rule tables and calculations into inspectable software with a REST API, structured hexagram data, regression tests, and explicit documentation of unresolved rule ambiguities.

> **Status: actively maintained, pre-stable.** The project is intended for study, research, software verification, and reproducible discussion of Liuyao rules. It is not presented as the only authoritative interpretation of the tradition and should not be used for medical, legal, financial, or other high-stakes decisions.

## What it implements

- three-coin six-line generation using the 6/7/8/9 distribution;
- manual and explicitly specified hexagrams;
- an experimental time-divination endpoint;
- Najia, Liuqin, Shi/Ying, Liushen, and Xunkong data;
- moving lines, transformed hexagrams, and selected Sheng/Ke/Chong/He relationships;
- reference data for 64 hexagrams and 384 line texts;
- FastAPI REST endpoints and a browser UI.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m backend.main
```

Open `http://127.0.0.1:8000` or inspect the API at `/docs`.

### Docker

```bash
docker build -t liuyao-paipan .
docker run --rm -p 8000:8000 liuyao-paipan
```

Copyable REST/Python examples are in [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md).

## Verification

Pull requests run:

- Python 3.10, 3.11, and 3.12 test jobs;
- backend compilation checks;
- pytest regression/data-integrity tests;
- a Docker image build;
- CodeQL security analysis.

Dependabot is configured for Python and GitHub Actions dependencies.

The current test suite validates request boundaries, the three-coin line mapping, and structural integrity of the 64-hexagram / 384-line datasets. Broader domain regression coverage is tracked publicly in issue #5.

## Known limitations

The project intentionally documents unresolved correctness work instead of hiding it behind broad accuracy claims:

1. **Ganzhi and solar-term boundaries need a stronger reference suite.** Exact transition times and cross-year/month boundaries remain tracked in issue #1.
2. **Time divination is experimental.** The current endpoint does not yet claim to implement a fully cited traditional year/month/day/hour method; issue #2 tracks the replacement and fixed reference cases.
3. **Some strength and relationship rules are engineering simplifications.** They require more source-backed decision tables and regression cases before stronger compatibility claims are made.
4. **Najia/reference-data duplication needs consolidation.** Issue #4 tracks a single auditable source of truth.

See [`CODE_REVIEW.md`](CODE_REVIEW.md) and [`docs/SOURCES_AND_SCOPE.md`](docs/SOURCES_AND_SCOPE.md) for details.

## Maintenance model

The project treats maintenance as reviewable work rather than only feature development:

- [`MAINTAINERS.md`](MAINTAINERS.md) — maintainer responsibilities and decision policy;
- [`ROADMAP.md`](ROADMAP.md) — reliability, adoption, and maintenance roadmap;
- [`CHANGELOG.md`](CHANGELOG.md) — user-visible compatibility and security changes;
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution and testing requirements;
- [`SECURITY.md`](SECURITY.md) — vulnerability reporting;
- [`docs/RELEASING.md`](docs/RELEASING.md) — release process;
- [`docs/MAINTAINER_AUTOMATION.md`](docs/MAINTAINER_AUTOMATION.md) — candidate PR-review, issue-triage, regression-test, documentation, and release automation workflows.

High-risk rule changes require a reproducible case and either a checkable source/reference or an explicitly documented project convention.

## Where Codex can help

The repetitive part of maintaining this repository is review-heavy rather than purely generative. Useful maintainer automation includes:

- summarizing pull-request impact and identifying missing tests;
- triaging issues into reproducible cases and affected components;
- drafting regression tests for confirmed bugs;
- checking documentation against API/model changes;
- preparing release notes and compatibility summaries;
- assisting with security and dependency-review workflows.

All generated changes remain subject to maintainer approval and CI. AI output is not accepted as evidence for a traditional-rule claim by itself.

## Contributing and real-world usage

Bug reports, rule-source corrections, regression cases, documentation improvements, and real integrations are welcome. Usage reports should include the version/commit, environment, deployment mode, and a non-sensitive reproducible example where possible.

The project records only genuine public adoption signals. It does not manufacture stars, forks, downloads, or interactions.

## License

MIT. See [`LICENSE`](LICENSE).

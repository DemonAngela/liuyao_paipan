# Contributing

Thank you for contributing to `liuyao_paipan`.

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The development dependency file includes the runtime requirements plus the HTTP client and test runner used by API smoke tests.

## Development workflow

1. Create a branch from `main`.
2. Add or update tests for behavior changes.
3. Keep API behavior backward compatible when possible; document intentional breaks.
4. For calendrical or traditional-rule changes, provide a reproducible example and a checkable source/reference or explicit project convention.
5. Run the full test suite before submitting a pull request.
6. Submit a pull request with a clear impact/risk description.

## Areas needing contribution

- Calendar and Ganzhi validation against authoritative/reproducible references.
- Regression and property tests for the 64 hexagrams and changing lines.
- Najia/reference-data source-of-truth cleanup.
- API compatibility and integration smoke tests.
- Documentation, English explanations, and real deployment reports.

## Code quality

Do not change traditional rule implementations without a regression case. When sources disagree, document the disagreement rather than presenting one interpretation as universally authoritative.

Pull requests are expected to pass the Python version matrix, API tests, Docker image build, and CodeQL checks before merge.

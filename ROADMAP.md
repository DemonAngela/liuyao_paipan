# Roadmap

This roadmap tracks maintenance work that can be verified in code, tests, issues, and releases. It is intentionally not a promise of dates.

## Reliability foundation

- Resolve issue #1 with a reproducible solar-term/Ganzhi reference suite.
- Resolve issue #2 with cited time-divination rules and fixed regression cases.
- Expand coverage for Najia, Shi/Ying, Liuqin, Liushen, Xunkong, moving-line transformations, and relationship calculations.
- Remove duplicate or dead implementations that can drift from production behavior.
- Keep domain limitations visible until tests support stronger claims.

## Maintainer workflow

- Keep CI green across supported Python versions.
- Automate dependency update pull requests and security scanning.
- Add repeatable release notes and release validation.
- Use structured issue templates for bugs and rule-accuracy reports.
- Evaluate Codex for pull-request review, issue triage, regression-test generation, documentation checks, and release-note assistance while retaining human approval for every merge.

## Adoption and interoperability

- Provide a reproducible container image/build path for local deployment.
- Add API examples and machine-readable examples for integrators.
- Collect real-world compatibility reports and convert them into regression fixtures.
- Improve English-facing documentation so non-Chinese-speaking developers can understand the architecture and API boundaries.

## Stable release criteria

A stable release should require, at minimum:

- the high-risk calendrical and time-divination issues resolved or explicitly excluded from the stable contract;
- documented API compatibility expectations;
- repeatable CI and security checks;
- a documented release process;
- a meaningful set of external usage reports or integrations rather than maintainer-only testing.

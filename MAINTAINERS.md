# Maintainers

## Primary maintainer

- **DemonAngela** — project architecture, core rules, data changes, API compatibility, security response, releases, issue triage, and pull-request review.

## Maintenance policy

The project is maintained as an evidence-driven implementation. Changes to calendrical calculations, Najia data, line transformations, Liuqin, Liushen, Xunkong, or interaction rules should include reproducible examples and regression tests.

The primary maintainer is responsible for:

- triaging new bug and rule-accuracy reports;
- reviewing and merging pull requests;
- maintaining CI and dependency updates;
- reviewing security reports and dependency alerts;
- maintaining release notes and compatibility information;
- documenting unresolved rule or source ambiguities instead of silently choosing an interpretation;
- keeping the public roadmap and known limitations current.

## Decision making

Small implementation changes can be merged after tests pass and review finds no compatibility risk. Domain-rule changes require a cited source or an explicit project convention plus a regression case. When credible sources disagree, the disagreement should be documented and the chosen behavior made testable.

## Becoming a maintainer

Regular contributors who demonstrate sustained, technically careful participation may be invited to take on triage or review responsibilities. Maintainer status should reflect ongoing responsibility rather than commit count alone.

# Maintainer Automation Plan

This document describes maintenance work that is suitable for automation while keeping domain decisions under human review.

## Candidate Codex workflows

### Pull-request review

Use a read-only review step to summarize changed modules, identify missing tests, flag API compatibility risks, and call out edits to high-risk calendrical or rule data. The maintainer remains responsible for accepting or rejecting every finding and every code change.

### Issue triage

Convert incoming issue text into a proposed category, affected component, reproduction checklist, and priority suggestion. Rule-accuracy reports should never be auto-closed or treated as resolved without source verification.

### Regression-test generation

For confirmed bugs, use the issue reproduction as input to draft a failing regression test. Generated tests must be reviewed to ensure they encode the intended domain rule rather than the current implementation.

### Documentation consistency

Check that README/API examples match current request models, endpoints, environment variables, supported Python versions, and known limitations.

### Release workflow

Summarize merged pull requests into draft release notes, highlight compatibility or security changes, and verify that changelog entries match the diff. Release publication remains an explicit maintainer action.

### Security assistance

Use security tooling to prioritize dependency changes and review externally reachable API paths. Findings that involve domain correctness and findings that involve software security should be tracked separately.

## Guardrails

- No generated change is merged without CI and maintainer review.
- No traditional-rule claim is accepted solely because an AI model proposes it.
- Secrets and private reports are not copied into public prompts or issues.
- Automation should create reviewable artifacts, not silently mutate production data.
- Token/API usage should be bounded by diff size and task type when programmatic automation is introduced.

## Why API credits help

The repository has structured maintenance tasks that are repetitive but review-heavy: regression-test drafting, documentation verification, issue classification, PR analysis, and release-note preparation. API credits would let these workflows run consistently without replacing human judgment on domain rules or security decisions.

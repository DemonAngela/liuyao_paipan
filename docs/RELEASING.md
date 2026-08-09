# Releasing

Releases are maintainer-controlled and should represent a tested snapshot of the public repository.

## Before tagging

1. Confirm CI passes on the target commit.
2. Review open P1 correctness/security issues and note unresolved ones in release notes.
3. Update `CHANGELOG.md` with user-visible behavior, compatibility changes, and security-relevant changes.
4. Verify README examples and deployment instructions against the target commit.
5. Run at least one local or CI-backed API smoke test for the release candidate.

## Versioning

Before a stable 1.0 release, minor versions may contain compatibility changes required for correctness or safety. Such changes must be called out in the changelog. Patch releases should avoid deliberate API breaks.

## Publishing

Push an annotated or signed tag matching `v*` (for example `v0.2.0`). The Release workflow will:

- run the Python test suite;
- build the container image;
- publish versioned and `latest` images to GitHub Container Registry;
- create GitHub release notes from the tag.

The maintainer should then review the generated release notes and amend them if they omit known limitations or compatibility warnings.

## Rollback

If a release introduces a correctness or security regression, open an issue describing the impact and reproducible case, prepare a tested fix or revert, and publish a new patch release. Published tags should not be silently rewritten.

# Releasing

Releases are maintainer-controlled and should represent a tested, reproducible snapshot of the public repository.

## Before tagging

1. Confirm CI and CodeQL pass on the target commit.
2. Review open P1 correctness/security issues and note unresolved ones in release notes.
3. Update `CHANGELOG.md` with user-visible behavior, compatibility changes, and security-relevant changes.
4. Verify README, REST examples, and Python integration examples against the target commit.
5. Confirm package installation/import tests and Docker build tests pass.

## Versioning

Before stable 1.0, minor versions may contain compatibility changes required for correctness or safety. Such changes must be called out in the changelog. Patch releases should avoid deliberate API breaks.

The FastAPI metadata and Python package version are kept on the same release line.

## Publishing

The `Release` workflow can be triggered by a `v*` tag or manually with a version such as `v0.2.0`. For a manual release it creates and pushes the annotated tag after tests pass.

The workflow then:

- installs the same development/test dependencies used by CI;
- verifies the installable Python package and complete pytest suite;
- logs in to GitHub Container Registry;
- builds and publishes versioned and `latest` GHCR images;
- embeds SBOM and max-level provenance metadata in the container build;
- creates a GitHub artifact attestation bound to the published image digest;
- creates GitHub release notes from the verified tag.

Consumers can therefore verify both the source tag and the published container provenance instead of relying only on a mutable image tag.

## Release review

After publication, the maintainer should review generated release notes and amend them if they omit known limitations, compatibility changes, reference-baseline changes, or security-relevant information.

## Rollback

If a release introduces a correctness or security regression, open an issue describing the impact and reproducible case, prepare a tested fix or revert, and publish a new patch release. Published tags must not be silently rewritten.

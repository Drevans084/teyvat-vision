# Contributing to Teyvat Vision

Teyvat Vision is currently in pre-alpha development.

Contributions should prioritize correctness, traceability, and maintainability over implementation speed.

## Development Principles

Changes should:

- Preserve separation between recognition, validation, domain models, and export.
- Avoid silent fallback behavior.
- Include tests for new behavior.
- Include regression fixtures for recognition defects where applicable.
- Retain diagnostic information for ambiguous or failed recognition.
- Avoid introducing undocumented external service dependencies.
- Avoid committing large datasets, models, captures, or third-party assets without an approved storage policy.

## Development Environment

The project targets Python 3.13.

Create and activate a virtual environment before installing project dependencies.

    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1

## Quality Checks

Before submitting a change, the following checks should pass:

    ruff check .
    ruff format --check .
    mypy src
    pytest

## Architecture Changes

Significant architectural decisions should be documented using an Architecture Decision Record in `docs/adr/`.

Examples include:

- Runtime or framework selection
- Recognition backend selection
- Canonical data-model changes
- External-provider contracts
- Model storage strategy
- Export format architecture
- Resolution-normalization strategy
- Failure semantics

## Ground Truth

Do not use unverified legacy scanner output as training or validation truth.

Fixture provenance must be recorded and should identify whether truth was:

- Manually verified
- Derived from canonical game data
- Verified through an appropriate external provider
- Synthesized from independently verified assets

## Commit Scope

Prefer small, focused commits that leave the repository in a working state.

Do not mix unrelated refactoring, feature development, dataset changes, and formatting changes into a single commit.

## Branch and Pull Request Workflow

The `main` branch is protected.

Substantive development should normally occur on a short-lived branch and be merged through a pull request.

Recommended branch prefixes include:

- `feature/` for new functionality
- `fix/` for defect corrections
- `docs/` for documentation-only changes
- `test/` for test-focused changes
- `refactor/` for behavior-preserving structural changes
- `chore/` for repository, tooling, dependency, or maintenance work

Examples:

`feature/good-domain-model`

`fix/artifact-value-validation`

`docs/data-provider-contracts`

Before opening a pull request, run the local quality gates:

    uv lock --check
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy src
    uv run pytest
    git diff --check

Pull requests targeting `main` must pass the repository CI workflow before merge.

The protected `main` branch requires:

- A pull request
- The `Quality / Python 3.13` status check to pass
- The branch to be current with `main`
- All review conversations to be resolved
- Linear Git history

Force pushes and branch deletion are disabled for `main`.

Approving reviews are not currently required because the project is maintained by a single developer. This policy should be revisited when additional regular contributors participate.

Direct pushes to `main` should be avoided even when administrative access would otherwise permit them.

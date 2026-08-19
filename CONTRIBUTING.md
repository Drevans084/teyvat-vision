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
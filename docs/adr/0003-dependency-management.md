# ADR 0003: Use uv for Dependency Management and Environment Reproducibility

- Status: Accepted
- Date: 2026-08-19

## Context

Teyvat Vision will depend on several distinct categories of Python packages.

These are expected to include:

- Production application dependencies
- Computer-vision and numerical libraries
- Desktop UI dependencies
- Production inference dependencies
- Development and quality tooling
- Test infrastructure
- Research and machine-learning training dependencies

The project must support reproducible development environments and avoid
depending on undocumented local package installations.

A developer should be able to clone the repository and reconstruct the
intended development environment without reproducing a historical sequence of
manual `pip install` commands.

The project already uses `pyproject.toml` as its primary Python project
configuration.

Python packaging standards also provide dependency groups for development
requirements that should not become part of the distributed application's
runtime metadata.

Teyvat Vision additionally needs a lockfile strategy so direct and transitive
dependency versions can be reproduced across development environments and CI.

## Decision

Teyvat Vision will use `uv` as its Python project dependency and environment
management tool.

`pyproject.toml` will remain the authoritative declaration of project
requirements.

`uv.lock` will contain the resolved dependency graph and will be committed to
Git.

Developers and CI should synchronize environments from the project metadata
and lockfile rather than independently constructing environments through
manual package installation.

The normal project workflow will use commands such as:

    uv sync
    uv add <package>
    uv add --group dev <package>
    uv lock
    uv run <command>

Direct modification of the active virtual environment using ad hoc
`pip install` commands should not be part of the normal project workflow.

Temporary experimentation may occur outside the managed project environment,
but a dependency required by committed project code must be represented in
the project configuration.

## Dependency Classification

Dependencies will be classified according to their purpose.

### Runtime Dependencies

Packages required for normal execution of Teyvat Vision will be declared as
project dependencies.

Conceptually:

    [project]
    dependencies = [...]

Examples may eventually include computer-vision, GUI, numerical, or inference
libraries.

No specific runtime library is accepted by this ADR.

### Development Dependencies

Development-only tools will use the standardized `dev` dependency group.

Conceptually:

    [dependency-groups]
    dev = [...]

This group will contain tools required for activities such as:

- Testing
- Linting
- Formatting
- Static type checking
- Coverage analysis
- Repository quality checks

### Research and Training Dependencies

Machine-learning research and training dependencies will not automatically
become production application dependencies.

A separate dependency group will be created if and when research/training
dependencies are required.

Conceptually:

    [dependency-groups]
    research = [...]

Potential examples include:

- PyTorch
- Training-specific augmentation libraries
- Dataset-analysis libraries
- Notebook or research tooling

The exact group contents will be determined when the research environment is
designed.

## Lockfile Policy

`uv.lock` will be tracked in Git.

The lockfile is considered part of the reproducible project definition.

Changes to dependencies should normally modify both:

- `pyproject.toml`
- `uv.lock`

Dependency changes should be reviewed like source-code changes.

A dependency update must not consist solely of modifying the local virtual
environment.

CI should eventually verify that the lockfile and project configuration are
synchronized.

## Virtual Environment

The normal local project environment will remain:

`.venv`

The `.venv` directory is local development state and will not be committed.

The environment should be reproducible from the committed project files.

A developer should therefore be able to remove `.venv`, recreate or
resynchronize it, and return to a functional project environment without
manually reconstructing dependency state.

## Version Constraints

Direct dependencies should use deliberate version constraints.

The project should avoid two extremes:

1. Pinning every direct dependency permanently without reason.
2. Leaving important compatibility boundaries entirely unconstrained.

The lockfile will provide exact resolved versions for reproducibility.

`pyproject.toml` will describe the project's supported dependency constraints.

This allows dependency compatibility policy and exact environment
reproducibility to remain separate concerns.

## Dependency Admission

Adding a dependency is an architectural and maintenance decision, not merely
an implementation convenience.

Before adding a significant dependency, consider:

- What problem does it solve?
- Is that functionality already available in the existing stack?
- Is the project actively maintained?
- Does it support the project's Python and Windows targets?
- What transitive dependencies does it introduce?
- What is its license?
- How does it affect application packaging?
- How does it affect executable size?
- Does it introduce native runtime requirements?
- Does it introduce security or supply-chain concerns?

Major framework or runtime dependencies may require their own ADR.

## Alternatives Considered

### pip and requirements.txt

`pip` remains a standard Python package installer and can support reproducible
workflows when combined with appropriate requirements and constraint files.

It was not selected as the primary project dependency workflow because Teyvat
Vision benefits from integrated project dependency management, standardized
dependency groups, environment synchronization, and a project lockfile.

`pip` remains part of the broader Python ecosystem and may still be used
internally by tooling where appropriate.

### pip-tools

`pip-tools` provides strong requirements compilation and locking workflows.

It was not selected because uv provides dependency declaration, project
locking, environment synchronization, and command execution within a single
project-oriented workflow.

Using both would add tooling overlap without a demonstrated need.

### Poetry

Poetry provides dependency management, locking, packaging, and environment
management.

It was not selected because Teyvat Vision already uses standard
`pyproject.toml` project metadata and does not require a separate
Poetry-specific project model.

The project prefers standard Python metadata and dependency groups with a
smaller additional tooling layer.

### Manual Virtual Environment Management

Continuing to create `.venv` with the standard library and manually installing
packages would initially require very little additional tooling.

It was rejected as the long-term project workflow because it does not by
itself provide an authoritative, locked, reproducible dependency graph.

## Consequences

Developers and CI will be able to construct consistent project environments
from committed files.

Dependency changes will become explicit and reviewable.

The repository will gain an additional tool dependency on uv.

The project will commit a `uv.lock` file in addition to `pyproject.toml`.

Developers must learn a small set of uv commands rather than managing the
project primarily through direct `pip install` operations.

Production, development, and research dependencies can remain clearly
separated.

The approach reduces the risk that a local environment works only because of
packages or versions that were never recorded in source control.

## Revisit Conditions

This decision should be revisited if:

- uv no longer satisfies the project's reproducibility requirements.
- A standardized Python lockfile workflow becomes clearly preferable for the
  project's needs.
- Packaging or deployment requirements conflict materially with the uv
  project model.
- CI or contributor workflows reveal significant disadvantages that outweigh
  the benefits of the current approach.
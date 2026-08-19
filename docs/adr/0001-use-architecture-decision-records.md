# ADR 0001: Use Architecture Decision Records

- Status: Accepted
- Date: 2026-08-19

## Context

Teyvat Vision is a ground-up application with significant architectural decisions involving computer vision, machine learning, desktop UI technology, external data providers, domain modeling, export compatibility, testing, diagnostics, and packaging.

Many of these decisions involve tradeoffs whose reasoning may not remain obvious later in development.

The repository is also intended to preserve the reasoning behind significant technical choices and demonstrate disciplined software-engineering practices.

Without a durable decision record, future contributors would have to infer architectural intent from implementation details, commit history, or outdated discussion.

## Decision

Teyvat Vision will use Architecture Decision Records (ADRs) for significant technical decisions.

ADRs will be stored in:

`docs/adr/`

Each ADR will contain, at minimum:

- Decision identifier and title
- Status
- Date
- Context
- Decision
- Consequences

When appropriate, ADRs may additionally document:

- Alternatives considered
- Validation evidence
- Revisit conditions
- Related ADRs

ADR files will use sequential identifiers and descriptive names.

Example:

`0002-python-runtime-and-application-stack.md`

Accepted ADRs will not be rewritten to conceal or replace historical decisions.

If an accepted architectural decision changes substantially, a new ADR will document the replacement decision and mark the previous ADR as superseded.

## Consequences

Architectural decisions will have a durable and reviewable history.

Future contributors will be able to understand why a design exists rather than inferring intent solely from source code.

Changes to major architectural choices will be visible in version control.

The project incurs a small documentation cost whenever significant architectural decisions are made. This cost is accepted in exchange for improved maintainability, traceability, and technical clarity.
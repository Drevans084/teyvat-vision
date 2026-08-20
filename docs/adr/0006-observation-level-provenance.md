# ADR 0006: Keep Provenance at the Observation Level

- Status: Accepted
- Date: 2026-08-19

## Context

Teyvat Vision must preserve traceable evidence for recognized, derived, verified,
and synthetic data without allowing uncertainty or source metadata to corrupt
the canonical account model.

A single domain entity may contain values established through different
mechanisms. For example, a character identity may be resolved through visual
recognition, a level through numeric recognition, static metadata through a
versioned game-data provider, and selected account state through an external
account-data provider.

Assigning one provenance value to an entire entity is therefore too coarse.

Wrapping every canonical value directly in provenance and recognition metadata
would make the core domain model dependent on scanner implementation details and
would complicate exporters, validation, comparison, and other downstream uses.

## Decision

Teyvat Vision will keep canonical account state separate from observation
evidence.

Canonical domain objects such as `Character`, `Weapon`, `Artifact`,
`MaterialStack`, and `AccountSnapshot` will contain validated domain values and
will not wrap every field in provenance metadata.

Evidence will be represented at the observation level.

An observation will identify the canonical subject and field or property being
observed and may carry information such as:

- the observed or derived value;
- provenance classification;
- source and source reference;
- recognition confidence where applicable;
- diagnostic or capture references;
- recognition strategy or recognizer identity;
- timestamps where operationally useful.

Multiple observations may support the same canonical value.

The canonical account snapshot represents the accepted account state. The
observation/evidence layer records why that state was accepted and provides the
information needed for diagnostics, auditing, retraining, and later
re-evaluation.

## Provenance Classes

The currently accepted provenance classifications are:

- `manual_verified`
- `game_data_derived`
- `api_verified`
- `synthetic_from_verified_assets`

These classifications describe trusted truth provenance. Scanner recognition
evidence may reference trusted assets or validation sources without being
misrepresented as ground truth itself.

## Boundaries

The canonical domain model must not depend on OCR, computer-vision, API-client,
or exporter-specific types.

Recognition failures and ambiguity remain explicit and must not be converted
into canonical values solely to satisfy the account model.

A missing observation is not equivalent to a negative observation.

An absent canonical value must not be fabricated from an empty, zero, or
default recognition result.

GOOD-specific identity and field naming remain exporter concerns and must not
become observation identifiers.

## Consequences

### Positive

- Canonical account objects remain simple and strongly typed.
- Individual fields may have different provenance.
- Multiple evidence sources may support or challenge one canonical value.
- Diagnostics can retain confidence and capture references without polluting
  exporters.
- Recognition algorithms can evolve without changing the canonical account
  schema.
- Manual verification can coexist with automated evidence.

### Costs

- Teyvat Vision must maintain a stable way to address subjects and fields in the
  evidence layer.
- Account state and evidence require cross-validation.
- Equipment and other duplicate-capable entities will eventually require stable
  instance identities rather than only game-definition identities.
- Diagnostic storage and evidence retention policies will require explicit
  design.

## Rejected Alternatives

### Entity-level provenance

Rejected because one entity can contain fields established by different
sources and recognition strategies.

### Provenance wrappers around every canonical value

Rejected because this couples the core domain model to evidence mechanics and
makes normal domain operations unnecessarily complex.

### Provenance only in logs

Rejected because logs are not a stable, queryable contract for explaining or
reproducing accepted account state.

## Follow-up

Define an observation/evidence model only after its subject-addressing strategy
is established.

In particular, weapon and artifact instances must eventually be distinguishable
even when multiple owned items share the same canonical game-definition
identity.

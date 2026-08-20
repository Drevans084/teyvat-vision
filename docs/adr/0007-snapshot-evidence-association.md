# ADR 0007: Associate Observation Evidence with Canonical Snapshots

- Status: Accepted
- Date: 2026-08-20

## Context

Teyvat Vision keeps canonical account state separate from observation evidence.

`AccountSnapshot` represents accepted account state, while `Observation[T]`
records evidence that may support, challenge, explain, or help diagnose that
state.

Once observations are associated with a particular snapshot, Teyvat Vision
needs to ensure that the evidence is actually meaningful for that snapshot.

An observation therefore needs two kinds of validation:

1. its subject must be represented by the associated snapshot;
2. its semantic field must be valid for that represented subject.

This validation must not make the evidence layer responsible for deciding which
observed value becomes canonical state.

Multiple observations may legitimately disagree with one another or with the
accepted snapshot. Rejecting conflicting observations would discard information
needed for diagnostics, comparison, retry logic, later re-evaluation, and
recognizer improvement.

## Decision

Teyvat Vision will use `SnapshotEvidence` to associate an `AccountSnapshot` with
the observations related to that snapshot.

`SnapshotEvidence` will validate observation addressing.

For each associated observation:

- character observations must reference an exact character represented in the
  snapshot;
- material observations must reference an exact material represented in the
  snapshot;
- weapon observations must reference the exact account-owned weapon instance
  through `OwnedItemId`;
- artifact observations must reference the exact account-owned artifact instance
  through `OwnedItemId`;
- the observation field must be a supported semantic field for the represented
  subject;
- artifact substat observations must reference a substat actually represented by
  that artifact instance.

`ObservationTarget` itself remains independently constructible and does not own
snapshot-schema validation. This keeps the observation primitive usable before
canonical state has been assembled.

`SnapshotEvidence` does not require:

`observation.value == canonical value`

A matching observation is valid evidence.

A conflicting observation is also valid evidence.

The associated `AccountSnapshot` remains the accepted canonical state and is not
mutated by observation association or validation.

## Subject and Field Validation

Character and material observations use canonical definition identities.

Weapon and artifact observations use `OwnedItemId` because multiple account-owned
instances may share the same game-definition identity.

Semantic field names belong to the domain evidence contract rather than to
export formats.

Examples include:

- `level`
- `ascension`
- `constellation`
- `talents.normal`
- `refinement`
- `quantity`
- `main_stat.value`
- `substats.crit_rate`

Exporter-specific paths or GOOD-specific property names must not become
observation field identifiers.

## Conflicting Evidence

Conflicting evidence is preserved rather than rejected.

For example, a snapshot may contain:

`character.level == 90`

while an associated observation contains:

`character.level == 80`

That observation may represent:

- an incorrect recognition result;
- stale external data;
- a lower-confidence alternate recognizer;
- evidence captured before canonical resolution;
- information useful for diagnostics or regression analysis.

The disagreement does not make the observation structurally invalid.

Selecting, ranking, reconciling, or applying competing evidence is a separate
responsibility from snapshot/evidence association.

## Boundaries

`SnapshotEvidence` is responsible for:

- snapshot association;
- exact subject membership validation;
- semantic field validation.

`SnapshotEvidence` is not responsible for:

- choosing the accepted value;
- comparing confidence between observations;
- resolving conflicting observations;
- mutating canonical state;
- recognition retries;
- OCR or computer-vision behavior;
- persistence or evidence-retention policy;
- exporter serialization.

These concerns belong to later application, recognition, persistence, or
resolution layers.

## Consequences

### Positive

- Canonical state remains independent from uncertain recognition evidence.
- Invalid subject references are rejected.
- Invalid semantic field references are rejected.
- Duplicate-capable equipment is addressed by exact owned-instance identity.
- Conflicting evidence can be preserved for diagnostics and future resolution.
- Recognition algorithms may evolve without changing canonical account objects.
- Export formats remain isolated from evidence addressing.

### Costs

- Snapshot association requires explicit cross-model validation.
- Semantic field contracts must evolve when canonical domain models evolve.
- Later application logic will need an explicit policy for resolving competing
  evidence.
- Evidence comparison and accepted-state mutation cannot be inferred merely from
  `SnapshotEvidence`.

## Rejected Alternatives

### Store observations directly on `AccountSnapshot`

Rejected because canonical accepted state should not own recognition uncertainty,
diagnostics, or provenance metadata.

### Reject observations whose values differ from canonical state

Rejected because disagreement is useful evidence and may be required to explain
recognition failures or later re-evaluate accepted state.

### Validate semantic fields inside `ObservationTarget`

Rejected because targets may exist before a complete canonical snapshot is
available, and the primitive evidence model should not depend on a particular
snapshot instance.

### Address weapons and artifacts only by definition identity

Rejected because an account may own multiple copies of the same weapon or
multiple artifacts from the same set. Evidence must address the exact owned
instance.

## Follow-up

Evidence comparison, prioritization, conflict resolution, and application to
canonical state should be designed as a separate layer only when a concrete
workflow requires them.

They are not part of the `SnapshotEvidence` association contract.

# ADR 0005: Treat GOOD as an Exporter Boundary

- Status: Accepted
- Date: 2026-08-19

## Context

Teyvat Vision must export data that is compatible with Genshin Optimizer.

Current Genshin Optimizer source defines GOOD as an external import format with
top-level support for:

- characters
- artifacts
- weapons

The current GOOD schema does not represent every category or piece of metadata
that Teyvat Vision intends to track.

Examples of Teyvat Vision data that may not belong in current GOOD include:

- materials
- recognition confidence
- recognition method
- provenance
- source hashes
- scanner session metadata
- unresolved recognition states
- diagnostic references
- scanner-only identities
- provider disagreement metadata

Recognition and scanning also require richer failure semantics than an export
format should encode.

If recognition code constructs GOOD objects directly, the scanner becomes
coupled to an external serialization contract.

That would make changes to GOOD affect recognition, validation, and domain
logic unnecessarily.

## Decision

GOOD will be implemented as an exporter boundary.

Teyvat Vision will first produce a canonical internal account model.

The intended flow is:

    Capture / Recognition
        ↓
    Recognition Result
        ↓
    Domain Validation
        ↓
    Canonical Teyvat Vision Model
        ↓
    Export Mapping
        ↓
    GOOD v3
        ↓
    External Compatibility Validation

Recognition code must not directly construct GOOD records.

Domain objects must not use GOOD field names solely because GOOD requires them.

GOOD-specific canonical keys will be resolved through explicit export mapping.

## Canonical Domain Model

The internal model should preserve more information than GOOD.

Conceptually:

    AccountSnapshot
        ├── metadata
        ├── characters[]
        ├── weapons[]
        ├── artifacts[]
        ├── materials{}
        ├── provenance
        ├── recognition metadata
        └── unresolved records

The internal model is the authoritative representation of a completed scan.

GOOD is one view of that model.

## Exporter Contract

Exporters should conform to a common interface.

Conceptually:

    Exporter
        format_id
        display_name
        validate(snapshot)
        export(snapshot, destination)

The GOOD exporter will:

1. Accept only a canonical Teyvat Vision account snapshot.
2. Validate that every exportable record has a valid GOOD mapping.
3. Exclude unsupported Teyvat Vision-only fields.
4. Reject invalid or unresolved records according to export policy.
5. Serialize the current GOOD contract.
6. Validate the serialized result before reporting success.

## GOOD Version Target

Teyvat Vision will target GOOD v3 unless upstream changes require a newer
version.

The current upstream parser still accepts GOOD versions 1, 2, and 3.

Teyvat Vision does not need to emit versions 1 or 2 unless a future
compatibility requirement justifies doing so.

## Unsupported Internal Data

Data that current GOOD does not represent must not be:

- silently discarded before the export boundary
- forced into unsupported GOOD fields
- encoded through undocumented custom extensions

Instead, such data remains available in the Teyvat Vision canonical model and
native snapshot format.

Examples include materials and scanner diagnostic metadata.

## Failure Semantics

An unresolved recognition result is not equivalent to a valid empty or zero
value.

The GOOD exporter must therefore distinguish between:

- valid and exportable
- valid but not represented by GOOD
- unresolved
- ambiguous
- failed recognition
- invalid canonical mapping

Strict GOOD export should fail or block when required exportable records are
unresolved.

A future best-effort export mode may be considered separately, but it must be
explicit and must never silently fabricate values.

## Mapping Layer

GOOD keys are external identifiers.

Mappings should be explicit and testable.

Examples include:

    Teyvat Vision character identity
        ↓
    GOOD character key

    Teyvat Vision weapon identity
        ↓
    GOOD weapon key

    Teyvat Vision artifact set identity
        ↓
    GOOD artifact set key

    Teyvat Vision stat identity
        ↓
    GOOD stat key

Display strings must not be used as the mapping contract.

## Compatibility Validation

A serialized JSON document being syntactically valid is not sufficient.

The GOOD exporter must be tested against current Genshin Optimizer semantics.

Compatibility tests should include:

- minimal valid character
- minimal valid weapon
- minimal valid artifact
- equipped weapon location
- equipped artifact location
- Traveler variants
- valid stat keys
- valid artifact set keys
- invalid key rejection
- unresolved record rejection
- successful import into current Genshin Optimizer

## Alternatives Considered

### Use GOOD as the Internal Domain Model

Rejected.

GOOD does not represent all Teyvat Vision data and would unnecessarily couple
scanner architecture to an external format.

### Write GOOD Directly From Recognition

Rejected.

This would mix recognition, domain validation, identity mapping, and
serialization.

It would also make it easier for failed recognition to become malformed export
data.

### Extend GOOD With Custom Teyvat Vision Fields

Rejected as the default approach.

Undocumented extensions reduce interoperability and may be ignored or rejected
by downstream tools.

Scanner-specific metadata belongs in the native Teyvat Vision format.

## Consequences

Recognition and export can evolve independently.

Teyvat Vision can support multiple exporters without duplicating scanning
logic.

The internal model can retain richer diagnostic and provenance data than GOOD.

GOOD schema changes are isolated primarily to mapping, serialization, and
compatibility tests.

The project incurs additional transformation code between the internal model
and export formats.

That transformation is intentional and should remain explicit.

## Revisit Conditions

This decision should be revisited if:

- GOOD evolves into a complete canonical account format that represents all
  required Teyvat Vision data.
- Genshin Optimizer replaces GOOD with a new import contract.
- A future official HoYoverse interchange format becomes the dominant external
  compatibility standard.
  
# GOOD Format Research

- Research date: 2026-08-19
- Target: Genshin Optimizer
- Repository: `frzyc/genshin-optimizer`
- Repository branch inspected: `master`
- Repository commit inspected: `61c5556a55f79a08520dda95cb128aeac3588908`
- GOOD implementation: `libs/gi/good`
- Status: Verified against current upstream source

## Purpose

This document records the external GOOD contract that Teyvat Vision must
support for compatibility with Genshin Optimizer.

This is a research document, not the Teyvat Vision internal domain model.

The internal Teyvat Vision model must remain independent from GOOD so that
scanner behavior and recognition data are not constrained by an external
serialization format.

## Current GOOD Container

The current Genshin Optimizer GOOD schema is defined in:

`libs/gi/good/src/schemas/good-format.ts`

The accepted top-level structure is conceptually:

    {
        "format": "GOOD",
        "source": "...",
        "version": 3,
        "characters": [],
        "artifacts": [],
        "weapons": []
    }

The current schema requires:

- `format`
- `source`
- `version`

The following collections are optional:

- `characters`
- `artifacts`
- `weapons`

## Supported GOOD Versions

The current parser accepts:

- GOOD version 1
- GOOD version 2
- GOOD version 3

Teyvat Vision will target GOOD v3 unless a later upstream contract requires a
newer version.

Backward compatibility with GOOD v1 or GOOD v2 is not currently a Teyvat
Vision requirement.

## Important Change From Legacy Assumptions

The current GOOD schema does **not** contain a `materials` collection.

This differs from older scanner behavior and documentation that associated
GOOD exports with materials.

Teyvat Vision must therefore not assume that every category scanned by the
application has a representation in current GOOD.

Materials will remain part of the Teyvat Vision canonical account model, but
must be handled through:

- Teyvat Vision's native snapshot format
- Other compatible exporters where appropriate
- A future GOOD version if upstream adds material support

The GOOD exporter must not emit unsupported fields merely to preserve behavior
from legacy scanners.

## Genshin Optimizer Import Path

The current Genshin Optimizer database upload path parses uploaded JSON and
checks:

    parsed.format === "GOOD"

When true, the application creates an import database and processes the data
through its GOOD import path.

Unknown formats are rejected by this upload path.

This confirms that GOOD remains the compatibility contract Teyvat Vision
should target for Genshin Optimizer database import.

## Character Contract

The current character schema contains:

- `key`
- `level`
- `constellation`
- `ascension`
- `talent`

Talent data contains:

- `auto`
- `skill`
- `burst`

Current validation boundaries include:

- level: 1 through 100
- constellation: 0 through 6
- ascension: 0 through 6
- talent levels: constrained according to the character's ascension

Character identity is represented by a canonical Genshin Optimizer character
key rather than a localized display name.

### Teyvat Vision Implication

Recognition should resolve a character into the canonical Teyvat Vision
identity first.

GOOD character keys should then be produced by an explicit mapping layer:

    visual/account identity
        ↓
    Teyvat Vision canonical character ID
        ↓
    GOOD character key

GOOD keys must not become the primary internal identity used by recognition
code.

## Weapon Contract

The current weapon schema contains:

- `key`
- `level`
- `ascension`
- `refinement`
- `location`
- `lock`

Current validation boundaries include:

- level: 1 through 90
- ascension: 0 through 6
- refinement: 1 through 5

The weapon key must exist in Genshin Optimizer's current game data.

If a weapon has an equipped `location`, Genshin Optimizer validates that the
weapon type is compatible with that character when character data is
available.

Weapon rarity is not supplied as part of the GOOD weapon record. It is derived
from canonical weapon data.

### Teyvat Vision Implication

Once weapon identity is known, static metadata such as weapon rarity should
come from the canonical game-data layer rather than being redundantly encoded
into GOOD.

Equipment ownership must map to a valid GOOD character location or remain
unequipped in the GOOD representation.

Scanner-only identities that do not exist as GOOD character keys must not be
serialized as ordinary GOOD character locations.

## Artifact Contract

The current artifact schema contains:

- `setKey`
- `slotKey`
- `level`
- `rarity`
- `mainStatKey`
- `location`
- `lock`
- `substats`

The schema additionally supports optional fields:

- `totalRolls`
- `astralMark`
- `elixirCrafted`
- `unactivatedSubstats`

Each substat contains:

- `key`
- `value`
- optional `initialValue`

Current artifact level validation is constrained to:

- level 0 through 20

Artifact identities are represented using canonical:

- artifact set keys
- slot keys
- main-stat keys
- substat keys
- character location keys

### Teyvat Vision Implication

Artifact recognition should not construct GOOD objects directly.

The recognizer should produce a richer internal artifact representation with:

- recognized values
- confidence
- recognition method
- validation status
- provenance
- scanner session identity
- unresolved-state information

Only validated artifacts should be transformed into GOOD records.

## Validation Behavior

Genshin Optimizer uses schema validation and normalization when importing GOOD.

This means a JSON document being syntactically valid is not enough.

Individual records can still be invalid because of:

- unknown canonical keys
- invalid ranges
- incompatible equipment ownership
- malformed stat data
- other schema violations

Teyvat Vision must therefore validate exports before presenting them as
successful GOOD output.

## Exporter Boundary

Recognition code must never depend directly on GOOD field names.

The intended boundary is:

    Recognition
        ↓
    Teyvat Vision Canonical Domain Model
        ↓
    Domain Validation
        ↓
    GOOD Mapping
        ↓
    GOOD v3 Serialization
        ↓
    Compatibility Validation

This allows GOOD to evolve without requiring recognition logic to change.

## Compatibility Test Requirement

Before the GOOD exporter is considered implemented, Teyvat Vision must have
fixture tests that verify:

1. A minimal valid character exports successfully.
2. A minimal valid weapon exports successfully.
3. A minimal valid artifact exports successfully.
4. Equipped weapon ownership is serialized correctly.
5. Equipped artifact ownership is serialized correctly.
6. Traveler variants resolve to the expected current GOOD keys.
7. Invalid canonical identities are rejected before export.
8. An exported Teyvat Vision GOOD file imports into the current Genshin
   Optimizer without invalid objects.

## Upstream Files Verified

The following current Genshin Optimizer files were inspected:

- `libs/gi/good/src/schemas/good-format.ts`
- `libs/gi/schema/src/character/schema.ts`
- `libs/gi/schema/src/weapon/schema.ts`
- `libs/gi/schema/src/artifact.ts`
- `libs/gi/ui/src/components/database/UploadCard.tsx`

## Open Questions

The following items still require targeted research before the GOOD exporter is
implemented:

- Exact current Traveler keys for each element.
- Complete current artifact set-key list.
- Complete current weapon-key list.
- Complete current character-key list.
- Complete main-stat and substat key sets.
- Whether GOOD v1/v2 differences require any special rejection or migration
  behavior in Teyvat Vision.
- Whether optional artifact fields such as `astralMark`,
  `unactivatedSubstats`, and `elixirCrafted` are visible and scan-worthy from
  the current Genshin UI.
- Whether any current Genshin Optimizer import normalization could conceal an
  invalid Teyvat Vision export and therefore requires stricter local
  validation.

## Decision Impact

The current upstream contract confirms several architectural requirements:

1. Teyvat Vision needs its own canonical account model.
2. GOOD is an exporter target, not the internal scanner schema.
3. Materials must remain independent from GOOD.
4. Canonical identity mappings must be explicit and versioned.
5. Current upstream schema tests must be part of compatibility testing.

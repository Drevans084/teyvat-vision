# ADR 0004: Use Internal Canonical Identities Behind Provider Boundaries

- Status: Accepted
- Date: 2026-08-19

## Context

Teyvat Vision must combine data from multiple external and internal sources.

Potential sources include:

- Raw extracted Genshin game data
- Normalized static-data APIs
- Optional public-account providers
- Local cached data
- Visual recognition results
- Export-specific schemas such as GOOD

These sources do not share a single stable identifier system.

Examples of possible identities include:

- Raw game IDs
- Provider-specific keys
- Localized display names
- Asset or icon names
- GOOD character keys
- GOOD weapon keys
- GOOD artifact-set keys

Using an external provider key directly as the application's primary identity
would couple the Teyvat Vision domain model to that provider.

Using localized display strings would be even less reliable because display
names may vary by language, formatting, aliases, or UI presentation.

The scanner must also support offline operation and survive provider changes
without forcing recognition logic to change.

## Decision

Teyvat Vision will maintain its own canonical identity layer.

External providers will be accessed through explicit provider interfaces.

Provider-specific records will be transformed into canonical Teyvat Vision
records before entering the application domain.

The intended identity flow is:

    upstream source identity
        ↓
    provider-specific parser
        ↓
    canonicalization
        ↓
    Teyvat Vision canonical identity
        ↓
    external mappings
        ├── GOOD key
        ├── localized display name
        ├── visual asset identifier
        └── provider-specific identifiers

Where a stable raw Genshin game ID exists and has been validated as suitable
for long-term use, that ID should normally anchor the Teyvat Vision canonical
identity.

The canonical layer must not assume that all entities have the same kind of
raw identifier.

## Provider Separation

Static game data and account/showcase data are separate concerns.

Teyvat Vision will use separate provider contracts.

Conceptually:

    GameDataProvider
        version()
        characters()
        weapons()
        artifact_sets()
        materials()
        assets()

and:

    AccountDataProvider
        fetch_account(identifier)

Potential static implementations include:

- AnimeGameDataProvider
- GenshinDevProvider
- LocalCacheProvider

Potential account implementations include:

- EnkaProvider
- FutureOfficialProvider

Account providers must not become required for normal scanning.

## Local Cache

Teyvat Vision will maintain a local static-data cache.

The cache is not an independent source of truth.

Cached data must retain provenance identifying where it came from.

At minimum, cached source metadata should include:

- provider name
- provider version or upstream game version
- upstream commit or content hash where available
- retrieval timestamp
- canonicalization schema version
- transformation version

The cache must support normal scanner operation when optional online services
are unavailable.

## Recognition Boundary

Recognition code should resolve visible game state into canonical Teyvat Vision
identities.

Recognition code must not directly emit:

- GOOD keys
- genshin.dev slugs
- Enka-specific identifiers
- localized display strings as primary identity

A visual recognizer may use external assets or metadata during recognition, but
its accepted output must resolve through the canonical identity layer.

## Source Disagreement

If two providers disagree, Teyvat Vision must not silently use whichever value
was fetched most recently.

Disagreement handling must be deterministic.

Where appropriate, the system should retain:

- conflicting values
- provider names
- provider versions
- source timestamps
- selected canonical value
- reason for selection

A provider disagreement must never silently corrupt an existing canonical
identity.

## Licensing Boundary

Provider access does not automatically grant redistribution rights.

The provider architecture must distinguish between:

- consuming an upstream service
- parsing an upstream repository
- caching upstream data locally
- redistributing upstream data
- redistributing derived data
- redistributing game assets

The application must not bundle upstream datasets or assets until the relevant
licensing and redistribution requirements have been reviewed.

## Alternatives Considered

### Use GOOD Keys as Canonical IDs

Rejected.

GOOD is an external export/import contract and can change independently of
Teyvat Vision.

Some Teyvat Vision data, including materials and scanner-specific metadata, is
not represented by the current GOOD schema.

### Use Localized Names

Rejected.

Localized names are presentation data rather than stable machine identities.

They are unsuitable as primary keys.

### Use One Community Provider as the Canonical Database

Rejected.

This would create an unnecessary single point of failure and couple the
application to a third-party schema.

### Merge Provider Records Directly

Rejected.

Implicit merging makes disagreement behavior difficult to reason about and can
hide source corruption or stale data.

## Consequences

Recognition, validation, caching, and export can evolve independently.

Provider changes do not require the entire application to adopt new identity
semantics.

Additional providers can be added without changing the canonical domain
contract.

The project incurs the cost of maintaining mapping tables and canonicalization
logic.

Those mappings become critical infrastructure and must be versioned and
tested.

Provider provenance must be treated as data rather than discarded after
normalization.

## Revisit Conditions

This decision should be revisited if:

- HoYoverse publishes an official stable identifier and data contract suitable
  for direct use as the internal canonical model.
- A future GOOD specification becomes a formally stable universal game-data
  identity standard rather than an export format.
- Evidence shows that the selected raw game IDs are not stable enough to serve
  as canonical anchors.
  
# Game Data Source Research

- Research date: 2026-08-19
- Purpose: Evaluate external data sources for Teyvat Vision
- Status: Initial provider research complete

## Objective

Teyvat Vision should use machine-readable game data wherever doing so can
replace unnecessary visual recognition.

External sources must not become hidden single points of failure.

The canonical architecture should separate:

- Static game-data providers
- Account/showcase providers
- Local cache
- Internal canonical identities
- Export-specific mappings

The scanner must remain usable when optional network services are unavailable.

## Evaluation Criteria

Providers are evaluated against:

- Data freshness
- Coverage
- Stable machine identifiers
- Localization support
- Asset availability
- Offline-cache suitability
- API stability
- Rate limits
- Licensing clarity
- Redistribution rights
- Dependency risk
- Suitability as canonical data
- Suitability as validation data

# 1. AnimeGameData

Repository:

`DimbreathBot/AnimeGameData`

## Intended Role

Primary candidate for raw static Genshin game data.

## Current State

The repository describes itself as containing release data for Genshin Impact.

It contains extracted game-data structures used by many community tools.

The repository was observed receiving Genshin 7.0 data updates during August
2026.

Relevant data areas historically include:

- `ExcelBinOutput`
- `TextMap`
- readable/generated data
- other extracted release data

The repository README asks users to report problems with `ExcelBinOutput` and
`TextMap` data and notes that maintaining the dumps is time-consuming.

## Strengths

- Very close to upstream game data.
- Frequently updated around game releases.
- Contains machine-oriented identifiers and structures.
- Suitable for deriving canonical entity metadata.
- Does not require a player account.
- Can potentially be cached locally for offline use.
- Historically used by existing Genshin tooling.

## Risks

The repository contains extracted game data rather than a stable application
API.

Its structure may change when the game changes.

Teyvat Vision must not expose AnimeGameData's raw structure directly to the
rest of the application.

A provider/parser boundary is required.

## Licensing

No explicit software/data license was identified in the repository README
during this research pass.

The README asks for attribution when the data is used by sites, tools, guides,
or similar projects, but this is not equivalent to a formal redistribution
license.

### Teyvat Vision Policy

Until licensing is clarified:

- Teyvat Vision may investigate and develop parsers against the repository.
- Teyvat Vision should record the exact upstream commit used.
- Raw AnimeGameData files should not automatically be redistributed inside
  Teyvat Vision releases.
- Extracted game assets should not automatically be committed to the Teyvat
  Vision repository.
- Any bundled derived dataset must receive a separate licensing and
  redistribution review.

The provider design must allow the source to be replaced if needed.

## Architectural Classification

Candidate status:

**PRIMARY STATIC DATA PROVIDER**

Confidence:

**High for technical usefulness**

Redistribution confidence:

**Unresolved**

# 2. genshin.dev

Repository:

`genshindev/api`

## Intended Role

Secondary static-data source and optional fallback/cross-check provider.

## Current API Model

genshin.dev explicitly states that it does not interact with the user's game
account.

It serves static game data.

Documented endpoint patterns include:

    /
    /:type
    /:type/all
    /:type/:id
    /:type/:id/list
    /:type/:id/:imageType

The API also supports optional localization through a language parameter.

## Strengths

- Straightforward HTTP API.
- Human-friendly normalized records.
- Supports entity listing.
- Supports individual entity retrieval.
- Provides images for some entities.
- Supports localization.
- Explicitly separates static game data from user-account data.
- Easier to consume than raw extracted game files.

## Weaknesses

The normalized identifiers and schema are defined by genshin.dev rather than
being raw game identifiers.

This makes it less attractive as the sole source of canonical Teyvat Vision
identity.

Update timing may lag behind direct extracted game-data sources.

Teyvat Vision must not assume that every entity or every new game field is
available immediately after a patch.

## Licensing

The genshin.dev repository explicitly states:

`Open Software License v3.0`

Any use of code, data, or assets from the project must be reviewed against the
requirements of that license before redistribution.

Consuming the API over HTTP is architecturally different from copying its
repository data or assets into Teyvat Vision.

## Architectural Classification

Candidate status:

**SECONDARY STATIC DATA PROVIDER**

Potential uses:

- Cross-checking names and metadata
- Optional fallback metadata
- Convenient localization
- Development-time comparison
- Potential image retrieval

It should not initially be the sole source of canonical identity.

# 3. Enka.Network

Repository:

`EnkaNetwork/API-docs`

## Intended Role

Optional public-account/showcase provider.

Enka is not a full account inventory source.

## UID API

The documented UID endpoint is conceptually:

    https://enka.network/api/uid/{UID}/

A successful response may contain:

- `playerInfo`
- `avatarInfoList`

If `avatarInfoList` is absent, the player's Character Showcase is closed or
does not expose characters.

## Request Requirements and Constraints

Enka documentation requests a custom `User-Agent`.

UID endpoints use dynamic rate limits.

UID responses include a `ttl` value representing the period during which
cached data will continue to be returned before another showcase request is
made upstream.

Clients are expected to respect this caching behavior rather than repeatedly
querying the same UID.

Documented response conditions include:

- invalid UID
- missing player
- game maintenance
- rate limiting
- general server errors
- service failures

Teyvat Vision must handle these explicitly if Enka support is implemented.

## Strengths

- Provides structured public showcase data.
- Useful for independently validating showcased characters.
- Useful for verifying showcased weapons and artifacts.
- Can reduce redundant recognition where the data is known to correspond to
  visible showcased characters.
- Can provide account/player metadata.
- Does not require private HoYoLAB authentication cookies.

## Limitations

Enka only sees data exposed through public showcase mechanisms.

It cannot prove that an unlisted character or item is absent from the account.

It cannot replace scanning for:

- Full weapon inventory
- Full artifact inventory
- Materials
- Characters not exposed in the showcase
- Other private account state

Missing Enka data must never be interpreted as non-ownership.

## Ground-Truth Policy

Enka data may be useful as:

- `api_verified` fixture provenance
- Cross-validation for showcased equipment
- Development diagnostics

It should not automatically override contradictory directly visible game
state.

Disagreements must be surfaced rather than silently merged.

## Architectural Classification

Candidate status:

**OPTIONAL ACCOUNT VALIDATION PROVIDER**

It is not a core scanner dependency.

# 4. Local Cache

## Intended Role

Teyvat Vision requires a local static-data cache regardless of which upstream
provider is selected.

The local cache should allow normal recognition and export to continue when
network services are unavailable.

Cached records should retain provenance such as:

- provider
- upstream version
- upstream commit or source hash
- fetch timestamp
- local schema version
- transformation version

The application must be able to determine which source produced a canonical
record.

## Cache Rule

The local cache is not an independent source of truth.

It is a persisted representation of data obtained from a specific versioned
provider.

# 5. Provider Boundary

Static data should be accessed through a provider interface rather than
directly throughout the application.

Conceptually:

    GameDataProvider
        version()
        characters()
        weapons()
        artifact_sets()
        materials()
        assets()

Potential implementations:

    AnimeGameDataProvider
    GenshinDevProvider
    LocalCacheProvider

Account data should use a separate contract:

    AccountDataProvider
        fetch_account(identifier)

Potential implementations:

    EnkaProvider
    FutureOfficialProvider

Static game data and user-account data are different trust domains and should
not share one generic provider abstraction.

# 6. Canonical Identity Strategy

No external provider key should automatically become Teyvat Vision's primary
identity.

The intended mapping is:

    raw upstream game ID
        ↓
    provider record
        ↓
    Teyvat Vision canonical identity
        ↓
    external mappings
        ├── GOOD key
        ├── display/localized name
        ├── visual asset name
        └── provider-specific key

Where a stable raw game ID exists, it should normally anchor the canonical
identity.

Localized display strings should never be primary identifiers.

Provider-specific slugs should not become primary identifiers unless evidence
shows they are the actual stable game identifier.

# 7. Source Disagreement Policy

If two providers disagree, Teyvat Vision must not silently choose whichever
response arrived last.

A disagreement should retain:

- source A value
- source B value
- source versions
- source timestamps
- mapping decision
- reason for the decision

Canonicalization rules must be deterministic and testable.

# 8. Recommended Initial Provider Ranking

Current recommendation:

1. AnimeGameData
   - Primary static data candidate
   - Closest to raw game data
   - Parser and licensing risks must be isolated

2. Local Cache
   - Mandatory operational layer
   - Enables offline scanning
   - Retains provider provenance

3. genshin.dev
   - Secondary static provider
   - Useful cross-check and convenience source
   - Not initially canonical

4. Enka.Network
   - Optional public-account validation
   - Never required for complete scanning
   - Never proof of non-ownership

# 9. Dependencies We Explicitly Reject as Foundational

Teyvat Vision should not make the following foundational requirements:

- Private HoYoLAB session cookies
- Reverse-engineered authenticated account APIs
- Packet-capture-based account extraction
- Enka availability
- genshin.dev availability
- Any single community HTTP service
- Display-name-based canonical identities

# 10. Open Questions

Before implementing the static data layer, research must still resolve:

- Which AnimeGameData tables contain the minimum canonical entity data needed
  by Teyvat Vision.
- Which raw IDs are stable across game versions.
- How Traveler variants are represented upstream.
- How artifact set and piece identities map to GOOD keys.
- How weapon and character IDs map to current Genshin Optimizer keys.
- Which material categories should exist in the Teyvat Vision native model.
- Whether icon filenames provide a sufficiently stable bridge between
  screenshots and canonical records.
- Whether Teyvat Vision may legally redistribute any derived static dataset.
- Whether a build-time fetch/generation workflow is preferable to runtime
  static-data downloads.
- How cache migrations should work when the local canonical schema changes.

# 11. Initial Architectural Direction

The current evidence supports the following architecture:

    Upstream Static Sources
        ↓
    Provider-Specific Parsers
        ↓
    Canonicalization / Validation
        ↓
    Versioned Local Cache
        ↓
    Teyvat Vision Domain

Optional account providers operate beside this path:

    Enka
        ↓
    AccountDataProvider
        ↓
    Optional validation/enrichment

Neither path should write GOOD records directly.

GOOD serialization remains a downstream exporter concern.

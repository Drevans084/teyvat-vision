# Game Data Source Research

- Research dates: 2026-08-19 through 2026-08-21
- Purpose: Evaluate external data sources for Teyvat Vision
- Status: Initial provider and symbolic-asset research complete

## Objective

Teyvat Vision should use machine-readable game data wherever doing so can
replace unnecessary visual recognition.

External sources must not become hidden single points of failure.

The canonical architecture should separate:

- static game-data providers;
- account and showcase providers;
- symbolic asset relationships;
- external asset resolvers;
- local metadata and asset caches;
- internal canonical identities;
- recognition evidence;
- export-specific mappings.

The scanner must remain usable when optional network services are unavailable.

## Evaluation criteria

Providers are evaluated against:

- data freshness;
- coverage;
- stable machine identifiers;
- localization support;
- asset-reference availability;
- image-resolution availability;
- offline-cache suitability;
- API stability;
- rate limits;
- licensing clarity;
- redistribution rights;
- dependency risk;
- suitability as canonical data;
- suitability as validation data.

# 1. AnimeGameData2

Provider identifier:

`Dimbreath/AnimeGameData2`

## Intended role

Primary provider for raw static Genshin game data and symbolic asset
relationships.

## Audited snapshot

The implemented provider and related audits use:

| Property | Value |
| --- | --- |
| Game version | `7.0.0` |
| Revision | `26df1dfbdf05a82bbb1d97506859f3e1c40718d8` |
| Provider | `Dimbreath/AnimeGameData2` |

The exact revision is retained as provider provenance so results can be
reproduced and later source changes can be compared deterministically.

## Current state

AnimeGameData2 contains extracted release data for Genshin Impact.

The audited snapshot provides the tables and text maps required for the
implemented Teyvat Vision static-data provider.

Relevant data areas include:

- `ExcelBinOutput`;
- `TextMap`;
- character configuration and fetter data;
- weapon configuration;
- artifact display, codex, and reliquary data;
- material configuration;
- symbolic icon fields.

The local audit checkout is external input. It is not committed to the Teyvat
Vision repository.

## Implemented canonical coverage

The AnimeGameData2 provider currently produces:

| Entity kind | Canonical definitions |
| --- | ---: |
| Characters | 122 |
| Weapons | 263 |
| Artifact sets | 63 |
| Materials | 770 |

Each entity family has documented membership rules and focused tests covering
valid records, exclusions, malformed source data, localization, canonical
classification, and ordering behavior.

## Strengths

- Very close to extracted upstream game data.
- Updated around game releases.
- Contains machine-oriented identifiers and relationships.
- Provides the fields required for canonical entity metadata.
- Provides symbolic icon references for every canonical provider member in the
  audited snapshot.
- Does not require a player account.
- Can be cached locally for offline use.
- Allows deterministic parsing from a recorded revision.
- Has proven useful to existing Genshin tooling.

## Risks

AnimeGameData2 contains extracted game data rather than a stable application
API.

Its structure may change when the game changes.

Teyvat Vision must not expose AnimeGameData2’s raw structure directly to the
rest of the application.

All source parsing must remain behind the provider boundary, with explicit
validation and focused source-contract tests.

## Licensing

No explicit software or data license was identified during the initial
research pass.

Attribution requests or community usage do not substitute for a formal
redistribution license.

### Teyvat Vision policy

Until licensing is clarified:

- Teyvat Vision may investigate and develop parsers against the dataset.
- Teyvat Vision must record the exact upstream revision used.
- Raw AnimeGameData2 files must not automatically be redistributed inside
  Teyvat Vision releases.
- Extracted game assets must not automatically be committed to the Teyvat
  Vision repository.
- Downloaded images must remain outside Git.
- Any bundled derived dataset requires a separate licensing and redistribution
  review.

The provider design must allow the source to be replaced if necessary.

## Architectural classification

Candidate status:

**PRIMARY STATIC DATA PROVIDER**

Confidence:

**High for technical usefulness**

Redistribution confidence:

**Unresolved**

# 2. genshin.dev

Repository:

`genshindev/api`

## Intended role

Secondary static-data source and optional fallback or cross-check provider.

## Current API model

genshin.dev explicitly states that it does not interact with the user’s game
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

Teyvat Vision must not assume that every entity, field, or new game version is
available immediately after a patch.

## Licensing

The genshin.dev repository explicitly states:

`Open Software License v3.0`

Any use of code, data, or assets from the project must be reviewed against the
requirements of that license before redistribution.

Consuming the API over HTTP is architecturally different from copying its
repository data or assets into Teyvat Vision.

## Architectural classification

Candidate status:

**SECONDARY STATIC DATA PROVIDER**

Potential uses:

- cross-checking names and metadata;
- optional fallback metadata;
- convenient localization;
- development-time comparison;
- potential fallback image resolution.

It should not initially be the sole source of canonical identity.

# 3. Enka.Network

Repository and documentation:

- `EnkaNetwork/API-docs`
- <https://api.enka.network/>
- <https://github.com/EnkaNetwork/API-docs>
- <https://github.com/EnkaNetwork/API-docs/blob/master/docs/gi/api.md#icons-and-images>

## Intended roles

Enka has two separate potential roles:

1. optional public-account and showcase provider;
2. optional symbolic asset resolver.

These roles belong behind different contracts and must not be combined into a
single generic provider.

Enka is not the canonical static game-data provider and is not a full account
inventory source.

## UID API

The documented UID endpoint is conceptually:

    https://enka.network/api/uid/{UID}/

A successful response may contain:

- `playerInfo`;
- `avatarInfoList`.

If `avatarInfoList` is absent, the player’s Character Showcase is closed or
does not expose characters.

## Request requirements and constraints

Enka documentation requests a custom `User-Agent`.

UID endpoints use dynamic rate limits.

UID responses include a `ttl` value representing the period during which
cached data will continue to be returned before another showcase request is
made upstream.

Clients are expected to respect this caching behavior rather than repeatedly
querying the same UID.

Documented response conditions include:

- invalid UID;
- missing player;
- game maintenance;
- rate limiting;
- general server errors;
- service failures.

Teyvat Vision must handle these explicitly if Enka account support is
implemented.

## Account-data strengths

- Provides structured public showcase data.
- Can independently validate showcased characters.
- Can verify showcased weapons and artifacts.
- Can reduce redundant recognition when API data is proven to correspond to
  visible showcased equipment.
- Can provide account and player metadata.
- Does not require private HoYoLAB authentication cookies.

## Account-data limitations

Enka only sees data exposed through public showcase mechanisms.

It cannot prove that an unlisted character or item is absent from the account.

It cannot replace scanning for:

- full weapon inventory;
- full artifact inventory;
- materials;
- characters not exposed in the showcase;
- other private account state.

Missing Enka account data must never be interpreted as non-ownership.

## Account ground-truth policy

Enka account data may be useful as:

- `api_verified` fixture provenance;
- cross-validation for showcased equipment;
- development diagnostics.

It must not automatically override contradictory directly visible game state.

Disagreements must be surfaced rather than silently merged.

## Icon and image endpoint

Official Enka documentation states that character, weapon, and artifact icons
can be requested through:

    https://enka.network/ui/[icon_name].png

AnimeGameData2 provides the symbolic reference. Enka may resolve that reference
to image content.

Enka does not determine which references belong to canonical entities.

No documented bulk icon archive or complete icon-export endpoint was
identified during this research.

## Audited symbolic-reference resolution

A sequential HTTP `HEAD` audit checked all 1,811 unique symbolic references
derived from the AnimeGameData2 7.0.0 snapshot.

| Entity group | Unique references | Resolved | Unresolved | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Characters | 244 | 244 | 0 | 100.00% |
| Artifact pieces | 299 | 299 | 0 | 100.00% |
| Weapons | 500 | 492 | 8 | 98.40% |
| Materials | 768 | 594 | 174 | 77.34% |
| **Total** | **1,811** | **1,629** | **182** | **89.95%** |

All successful responses were reported as images.

The official documentation explicitly describes character, weapon, and
artifact images. It does not promise complete material-icon coverage.

Observed material resolution must therefore be treated as opportunistic rather
than guaranteed.

## Asset-resolution policy

Enka availability must never alter AnimeGameData2 canonical membership.

The asset layer must preserve symbolic references even when Enka returns
`404`.

A resolver result must distinguish:

- resolved image;
- unresolved reference;
- transient network failure;
- invalid response.

A missing Enka image means the external resolver could not currently provide
the asset. It does not mean the symbolic relationship or canonical entity is
invalid.

## Architectural classification

Account candidate status:

**OPTIONAL ACCOUNT VALIDATION PROVIDER**

Asset candidate status:

**OPTIONAL ASSET RESOLVER**

Enka is not a core scanner dependency.

# 4. Symbolic asset relationships

## Intended role

Static providers associate canonical subjects with typed symbolic references.

The audited AnimeGameData2 fields support:

| Asset role | Entity kind |
| --- | --- |
| `character_icon` | Character |
| `character_side_icon` | Character |
| `weapon_icon` | Weapon |
| `weapon_awakened_icon` | Weapon |
| `material_icon` | Material |
| `artifact_flower` | Artifact set |
| `artifact_plume` | Artifact set |
| `artifact_sands` | Artifact set |
| `artifact_goblet` | Artifact set |
| `artifact_circlet` | Artifact set |

## Audited coverage

The AnimeGameData2 snapshot produced:

| Measurement | Result |
| --- | ---: |
| Subject and reference relationships | 1,839 |
| Unique symbolic references | 1,811 |
| Invalid or blank references | 0 |
| Missing referenced reliquary piece IDs | 0 |
| Subject-role pairs with multiple references | 0 |
| References shared by multiple subjects | 14 |
| References shared across entity kinds | 0 |

Every expected canonical subject has the required role coverage.

Four circlet-only artifact sets correctly omit the other four artifact roles.

## Identity rule

A symbolic asset reference is not a canonical identity.

Fourteen references are shared by multiple subjects. Therefore:

- global reference uniqueness must not be required;
- an icon match may produce multiple canonical candidates;
- every subject-and-role relationship must be preserved;
- recognition must combine icon evidence with structural, visual, and
  canonical constraints.

# 5. Local caches

## Static-data cache

Teyvat Vision requires a local static-data cache regardless of which upstream
provider is selected.

The static-data cache should allow normal recognition and export to continue
when network services are unavailable.

Cached records should retain provenance such as:

- provider;
- upstream version;
- upstream revision or source hash;
- fetch timestamp;
- local schema version;
- transformation version.

The application must be able to determine which source produced a canonical
record.

## External asset cache

Downloaded images belong in a separate external asset cache.

The asset cache must:

- remain outside Git;
- be reproducible from a symbolic-reference manifest;
- deduplicate downloads by symbolic reference or verified content hash;
- preserve every canonical subject-and-role relationship;
- support resumable downloads;
- retain unresolved references;
- record resolver provenance;
- validate successful image responses;
- permit Enka to be replaced by another resolver.

A future cache manifest should retain:

- canonical subject;
- asset role;
- symbolic reference;
- source URL;
- resolver;
- response status;
- content type;
- content length;
- SHA-256 digest;
- retrieval timestamp;
- local cache key.

Licensing, upstream terms, and redistribution rights must be reviewed before
any cached image collection is distributed.

## Cache rule

Neither cache is an independent source of truth.

A cache is a persisted representation of data or content obtained from a
specific versioned provider or resolver.

# 6. Provider and resolver boundaries

Static data should be accessed through a provider interface rather than
directly throughout the application.

Conceptually:

    GameDataProvider
        version()
        source()
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

    EnkaAccountDataProvider
    FutureOfficialAccountProvider

External image resolution should use another contract:

    AssetResolver
        resolve(reference)

Potential implementations:

    EnkaAssetResolver
    LocalAssetCacheResolver
    FutureAlternativeAssetResolver

Static game data, account data, and external image resolution are different
trust domains.

They must not share one generic provider abstraction.

Static game-data loading must never perform network asset resolution.

# 7. Canonical identity strategy

No external provider key should automatically become Teyvat Vision’s primary
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
        ├── display or localized name
        ├── typed symbolic asset relationship
        └── provider-specific key

Where a stable raw game ID exists, it should normally anchor the canonical
identity.

Localized display strings must never be primary identifiers.

Provider-specific slugs and symbolic asset names must not become primary
identifiers.

# 8. Source disagreement policy

If two providers disagree, Teyvat Vision must not silently choose whichever
response arrived last.

A disagreement should retain:

- source A value;
- source B value;
- source versions;
- source timestamps;
- mapping decision;
- reason for the decision.

Canonicalization rules must be deterministic and testable.

Resolver availability is not a canonical-data disagreement. It is a separate
external-resolution outcome.

# 9. Recommended provider ranking

Current recommendation:

1. AnimeGameData2
   - Primary static data provider.
   - Closest to extracted game data.
   - Supplies canonical metadata and symbolic asset relationships.
   - Parser and licensing risks remain isolated.

2. Local caches
   - Mandatory operational layers.
   - Enable offline scanning.
   - Retain provider and resolver provenance.
   - External binary assets remain outside Git.

3. genshin.dev
   - Secondary static provider.
   - Useful cross-check and convenience source.
   - Not initially canonical.

4. Enka.Network
   - Optional public-account validation provider.
   - Optional asset resolver.
   - Never required for canonical membership or complete scanning.
   - Never proof of non-ownership.

# 10. Dependencies explicitly rejected as foundational

Teyvat Vision must not make the following foundational requirements:

- private HoYoLAB session cookies;
- reverse-engineered authenticated account APIs;
- packet-capture-based account extraction;
- Enka availability;
- genshin.dev availability;
- any single community HTTP service;
- display-name-based canonical identities;
- symbolic-asset-based canonical identities;
- network access during static game-data loading;
- OCR as the default or foundational recognition architecture.

Inventory Kamera’s captured screenshots and Tesseract-derived results may
support external regression research, but they are not static game-data input
and must not define the new recognition architecture.

PaddleOCR or another OCR engine may only be considered later through a
separate, evidence-backed architectural decision.

# 11. Remaining questions

The initial provider and symbolic-asset research resolved:

- the minimum AnimeGameData2 tables required for the current canonical entity
  families;
- character membership behavior;
- weapon membership behavior;
- artifact-set and slot membership behavior;
- material membership behavior;
- the available symbolic asset fields;
- typed symbolic asset roles;
- current Enka resolution coverage;
- the requirement to keep canonical membership independent of resolver
  availability;
- the requirement to keep downloaded assets outside Git.

Remaining questions include:

- whether all selected raw game IDs remain stable across future game versions;
- how all canonical identities map to current GOOD keys;
- whether Teyvat Vision may legally redistribute any derived static dataset;
- whether any external image content may legally be redistributed;
- how static-data cache migrations should work when the canonical schema
  changes;
- how external asset-cache migrations and invalidation should work;
- whether Enka or another provider later publishes a supported bulk asset
  endpoint;
- which visual comparison techniques perform best against representative live
  captures;
- which variable fields, if any, cannot be recovered reliably without a
  separately evaluated text-recognition component.

# 12. Architectural direction

The current evidence supports this static-data path:

    Upstream Static Sources
        ↓
    Provider-Specific Parsers
        ↓
    Canonicalization and Validation
        ↓
    Canonical Definitions and Symbolic Asset Relationships
        ↓
    Versioned Local Static-Data Cache
        ↓
    Teyvat Vision Domain

Optional image resolution operates beside the static-data path:

    Symbolic Asset Reference
        ↓
    AssetResolver
        ↓
    External Asset Cache
        ↓
    Visual Recognition Evidence

Optional account providers use a separate path:

    Enka or Future Account Source
        ↓
    AccountDataProvider
        ↓
    Optional Validation and Enrichment

None of these paths should write GOOD records directly.

GOOD serialization remains a downstream exporter concern.

# 13. Supporting research records

Detailed reproducible findings are recorded in:

- `docs/research/anime-game-data2-artifact-audit.md`;
- `docs/research/anime-game-data2-material-audit.md`;
- `docs/research/anime-game-data2-asset-audit.md`;
- `scripts/audits/audit_anime_game_data_artifacts.py`;
- `scripts/audits/audit_anime_game_data_materials.py`;
- `scripts/audits/audit_anime_game_data_weapons.py`;
- `scripts/audits/audit_anime_game_data_assets.py`.

External AnimeGameData2 snapshots, resolved images, and personal Inventory
Kamera evidence are intentionally excluded from the repository.
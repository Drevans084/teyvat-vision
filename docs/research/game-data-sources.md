# Game Data Source Research

- Initial research date: 2026-08-19
- Last updated: 2026-08-21
- Purpose: Evaluate external data sources for Teyvat Vision
- Status: Primary static provider selected and under implementation

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

# 1. AnimeGameData2

Repository:

`Dimbreath/AnimeGameData2`

## Intended Role

Primary source for raw static Genshin game data.

## Selection

Teyvat Vision selected AnimeGameData2 after determining that an earlier
AnimeGameData experiment used the wrong or superseded source.

AnimeGameData2 is also the modern upstream source used by Inventory Kamera.
This provides a proven compatibility reference while allowing Teyvat Vision to
replace Inventory Kamera's name-based lookup architecture with typed canonical
records and stable raw game IDs.

## Audited Source Revision

The Phase 1 provider audit uses one immutable upstream revision:

- Game version: `7.0.0`
- GitLab project ID: `83871005`
- Project path: `Dimbreath/animegamedata2`
- Source revision: `26df1dfbdf05a82bbb1d97506859f3e1c40718d8`
- Version marker revision:
  `26df1dfbdf05a82bbb1d97506859f3e1c40718d8`
- Commit title:
  `CNRELWin7.0.0_R47482070_S47579390_D47579390`

The local research dataset is stored beneath:

`datasets/anime-game-data2-live`

Raw upstream files and extracted assets must not be committed or redistributed
without a separate repository and licensing decision.

## Audited Source Files

The current investigation uses:

- `TextMap/TextMapEN.json`
- `TextMap/TextMap_MediumEN.json`
- `ExcelBinOutput/AvatarExcelConfigData.json`
- `ExcelBinOutput/FetterInfoExcelConfigData.json`
- `ExcelBinOutput/AvatarTalentExcelConfigData.json`
- `ExcelBinOutput/AvatarSkillExcelConfigData.json`
- `ExcelBinOutput/DisplayItemExcelConfigData.json`
- `ExcelBinOutput/ReliquaryCodexExcelConfigData.json`
- `ExcelBinOutput/ReliquaryExcelConfigData.json`
- `ExcelBinOutput/WeaponExcelConfigData.json`
- `ExcelBinOutput/WeaponCodexExcelConfigData.json`
- `ExcelBinOutput/MaterialExcelConfigData.json`

## Localization Audit

The English localization sources are complementary:

- `TextMapEN.json`: 585,531 entries
- `TextMap_MediumEN.json`: 229,324 entries
- Overlapping hashes: 0
- Conflicting overlaps: 0

Both maps must be loaded when resolving English source names.

All formal avatar names examined during the character audit were found in
`TextMap_MediumEN.json`.

## Character Source Audit

`AvatarExcelConfigData.json` contains 165 rows.

Observed `useType` distribution:

- `AVATAR_FORMAL`: 130
- Missing: 31
- `AVATAR_ABANDON`: 3
- `AVATAR_SYNC_TEST`: 1

The audited relational membership rule is:

    Avatar.useType == "AVATAR_FORMAL"
        +
    matching FetterInfo.avatarId
        =
    canonical character source membership

This produces 122 canonical character source rows.

Exactly eight formal avatar rows do not have matching FetterInfo membership:

- `10000134`: Traveler PlayerBoy crossbow record
- `10000135`: Traveler PlayerGirl crossbow record
- `10000901`: Mavuika trial record
- `10000902`: Hu Tao trial record
- `10000903`: Ineffa duplicate
- `10000904`: Columbina duplicate
- `10000998`: UGC Official Male
- `10000999`: UGC Official Female

This relational boundary removes those records without depending on:

- Numeric ID cutoffs
- Trial-name matching
- UGC-name matching
- Duplicate-name heuristics
- Unsupported crossbow canonicalization

The following source records remain canonical members:

- `10000005`: Male Traveler
- `10000007`: Female Traveler
- `10000117`: Male Mannequin, `Manekin`
- `10000118`: Female Mannequin, `Manekina`

Teyvat Vision preserves their distinct raw identities. It does not inherit
Inventory Kamera's scanner-output decision to collapse or exclude them.

## Inventory Kamera Character Comparison

Inventory Kamera uses the same AnimeGameData2 avatar and FetterInfo tables, but
its generated character lookup is keyed by normalized GOOD-style names.

Its maintained updater applies several output-oriented filters, including:

- Excluding the Female Traveler source row
- Excluding IDs above a numeric threshold
- Excluding `Manekin` and `Manekina`
- Collapsing duplicate normalized names
- Depending on talent and skill heuristics for generated lookup metadata

Those choices are understandable for Inventory Kamera's lookup-file format but
are not appropriate as Teyvat Vision canonical-identity rules.

Teyvat Vision improves this boundary by:

- Using stable raw game IDs as canonical identity anchors
- Preserving distinct source identities
- Separating GOOD mappings from canonical identity
- Using FetterInfo as positive relational membership evidence
- Validating membership before canonicalizing other fields
- Preserving source order
- Rejecting malformed required fields explicitly

## Weapon Source Audit

`WeaponExcelConfigData.json` contains 281 unique weapon IDs.

Observed source weapon types:

- Sword: 69
- Catalyst: 59
- Bow: 54
- Claymore: 51
- Polearm: 47
- Crossbow: 1

Observed `rankLevel` distribution:

- 1-star: 15
- 2-star: 5
- 3-star: 28
- 4-star: 145
- 5-star: 88

Weapon rarity is represented by `rankLevel`. Weapon rows do not provide the
character-style `qualityType` field.

The five supported canonical weapon classes remain:

- Sword
- Claymore
- Polearm
- Bow
- Catalyst

The upstream crossbow row does not justify adding a canonical crossbow class.

## Inventory Kamera Weapon Baseline

Inventory Kamera's proven weapon membership behavior is:

    WeaponExcelConfigData row
        +
    nonempty name resolved through either English text map
        =
    generated weapon lookup membership

Applying that rule to the pinned 7.0.0 source produces:

- Raw weapon rows: 281
- Name-resolvable rows: 263
- Name-unmapped rows: 18

The 18 unresolved rows include:

- Ten template or internal records
- Seven non-template development or unreleased-looking records
- One fishing-rod record represented as a sword
- The only upstream crossbow record

Inventory Kamera logs unresolved names as likely unreleased and omits those
rows.

## Weapon Codex Comparison

`WeaponCodexExcelConfigData.json` was evaluated as a possible relational
membership source.

Audit results:

- Weapon codex rows: 249
- Unique codex weapon IDs: 249
- Duplicate codex weapon IDs: 0
- Codex IDs without weapon rows: 0
- Name-resolvable codex members: 249
- Codex members without resolvable names: 0
- Name-resolvable weapon rows absent from the codex: 14

The codex is therefore a strict subset of the 263-row Inventory Kamera
compatibility baseline.

The 14 localized rows omitted by the codex include:

- Three `Prized Isshin Blade` variants
- `Sword of Narzissenkreuz`
- `Primordial Jade Cutter`
- `One Side`
- `Quartz`
- `The Other Side`
- `The Flagstaff`
- `Deicide`
- `Amber Bead`
- `Lost Ballade`
- `Ebony Bow`
- `Mirror Breaker`

Some appear to be quest states, duplicates, legacy records, or unreleased
weapons. Those interpretations do not change the source fact that the codex
contains less localized information than Inventory Kamera's proven boundary.

## Weapon Membership Decision

Teyvat Vision will preserve the proven Inventory Kamera source boundary:

    WeaponExcelConfigData row
        +
    nonempty name resolved through TextMapEN or TextMap_MediumEN
        =
    canonical weapon source membership

`WeaponCodexExcelConfigData` will not be required for canonical weapon
membership.

This decision preserves all 263 localized source rows and prevents the provider
from silently discarding information that Inventory Kamera retained.

Membership filtering must occur before weapon-type and rarity canonicalization.
This naturally removes the unresolved crossbow record before the provider
encounters its unsupported source type.

Canonical weapon records will:

- Use the raw weapon ID as their canonical identity key
- Map source weapon classes into the five canonical classes
- Map `rankLevel` values 1 through 5 into canonical rarity
- Preserve source order
- Reject malformed required fields
- Keep localized names as presentation or mapping data rather than identity
- Keep GOOD keys behind the exporter boundary

## Reproducible Weapon Audit

The repository-owned audit utility is:

`scripts/audits/audit_anime_game_data_weapons.py`

Run it against the pinned local dataset with:

    uv run python scripts/audits/audit_anime_game_data_weapons.py \
        datasets/anime-game-data2-live

The audit compares:

- Raw weapon-table membership
- Inventory Kamera-compatible localization membership
- Weapon codex membership
- Unmapped internal and template rows

The script and this document preserve the evidence used to select the weapon
membership rule.

## Artifact Source Audit

The current artifact investigation observed:

- `DisplayItemExcelConfigData.json`: 334 rows
- Relic-icon display rows: 259
- Unique display-item suit IDs: 65
- `ReliquaryCodexExcelConfigData.json`: 129 rows
- Unique codex suit IDs: 63

Two display-item set IDs do not have codex entries:

- `15004`: Glacier and Snowfield
- `15012`: Prayers to the Firmament

Every nonzero artifact piece ID referenced by the codex was present in
`ReliquaryExcelConfigData.json`.

Observed raw artifact slots include:

- `EQUIP_DRESS`
- `EQUIP_SHOES`
- `EQUIP_RING`
- `EQUIP_NECKLACE`
- `EQUIP_BRACER`

Some prayer sets legitimately contain only a circlet-style slot. Teyvat Vision
must not assume that every artifact set has five slots.

No final artifact provider membership rule has yet been approved.

## Material Source Audit

`MaterialExcelConfigData.json` contains 10,404 rows.

Inventory Kamera selects six source categories:

- `MATERIAL_AVATAR_MATERIAL`: 474
- `MATERIAL_EXCHANGE`: 244
- `MATERIAL_EXP_FRUIT`: 3
- `MATERIAL_FISH_BAIT`: 13
- `MATERIAL_WEAPON_EXP_STONE`: 3
- `MATERIAL_WOOD`: 34

That produces 771 selected rows in the pinned dataset.

One selected wood row has no mapped name:

- ID: `101306`
- Name hash: `250702940`
- Icon: `UI_ItemIcon_101306`

Inventory Kamera's six material categories are a proven scanner baseline, but
they have not yet been adopted as the Teyvat Vision product rule.

## Strengths

- Very close to upstream game data
- Frequently updated around game releases
- Contains stable-looking raw machine identifiers
- Supports multiple localization maps
- Suitable for deriving canonical entity metadata
- Does not require a player account
- Can be cached locally for offline use
- Already proven by Inventory Kamera
- Supports reproducible revision-pinned audits

## Risks

AnimeGameData2 contains extracted game data rather than a stable application
API.

Its schemas and record relationships may change when the game changes.

Localized source membership may include legacy, quest-state, development, or
unreleased rows. Teyvat Vision currently preserves those rows when Inventory
Kamera also preserved them, favoring compatibility and information retention
over undocumented exclusion heuristics.

Teyvat Vision must not expose AnimeGameData2's raw structure directly to the
rest of the application.

A provider/parser boundary is required.

## Licensing

No explicit software or data license has been established for redistributing
the audited raw AnimeGameData2 dataset.

Attribution requests or community usage do not automatically grant
redistribution rights.

### Teyvat Vision Policy

Until licensing is clarified:

- Teyvat Vision may investigate and develop parsers against the repository.
- Teyvat Vision must record the exact upstream revision used.
- Raw AnimeGameData2 files must not automatically be redistributed inside
  Teyvat Vision releases.
- Extracted game assets must not automatically be committed.
- Any bundled derived dataset requires a separate licensing and redistribution
  review.

The provider design must allow the source to be replaced if needed.

## Architectural Classification

Candidate status:

**SELECTED PRIMARY STATIC DATA PROVIDER**

Technical confidence:

**High**

Redistribution confidence:

**Unresolved**

# 2. genshin.dev

Repository:

`genshindev/api`

## Intended Role

Secondary static-data source and optional fallback or cross-check provider.

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

- Straightforward HTTP API
- Human-friendly normalized records
- Supports entity listing
- Supports individual entity retrieval
- Provides images for some entities
- Supports localization
- Explicitly separates static game data from user-account data
- Easier to consume than raw extracted game files

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

- Invalid UID
- Missing player
- Game maintenance
- Rate limiting
- General server errors
- Service failures

Teyvat Vision must handle these explicitly if Enka support is implemented.

## Strengths

- Provides structured public showcase data
- Useful for independently validating showcased characters
- Useful for verifying showcased weapons and artifacts
- Can reduce redundant recognition where the data corresponds to visible
  showcased characters
- Can provide account or player metadata
- Does not require private HoYoLAB authentication cookies

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

- Provider
- Upstream version
- Upstream commit or source hash
- Fetch timestamp
- Local schema version
- Transformation version

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
        ├── display or localized name
        ├── visual asset name
        └── provider-specific key

Where a stable raw game ID exists, it should normally anchor the canonical
identity.

Localized display strings must never be primary identifiers.

Provider-specific slugs must not become primary identifiers unless evidence
shows they are the actual stable game identifier.

# 7. Source Disagreement Policy

If two providers disagree, Teyvat Vision must not silently choose whichever
response arrived last.

A disagreement should retain:

- Source A value
- Source B value
- Source versions
- Source timestamps
- Mapping decision
- Reason for the decision

Canonicalization rules must be deterministic and testable.

# 8. Recommended Provider Ranking

Current recommendation:

1. AnimeGameData2
   - Selected primary static provider
   - Closest to raw game data
   - Proven by Inventory Kamera
   - Isolated behind a parser and provenance boundary

2. Local Cache
   - Mandatory operational layer
   - Enables offline scanning
   - Retains provider provenance

3. genshin.dev
   - Secondary static provider
   - Useful cross-check and convenience source
   - Not canonical

4. Enka.Network
   - Optional public-account validation
   - Never required for complete scanning
   - Never proof of non-ownership

# 9. Dependencies We Explicitly Reject as Foundational

Teyvat Vision must not make the following foundational requirements:

- Private HoYoLAB session cookies
- Reverse-engineered authenticated account APIs
- Packet-capture-based account extraction
- Enka availability
- genshin.dev availability
- Any single community HTTP service
- Display-name-based canonical identities

# 10. Open Questions

Remaining research questions include:

- How artifact set and piece identities map to GOOD keys
- How weapon and character IDs map to current Genshin Optimizer keys
- Which material categories should exist in the Teyvat Vision native model
- Whether icon filenames provide a sufficiently stable bridge between
  screenshots and canonical records
- Whether Teyvat Vision may legally redistribute any derived static dataset
- Whether a build-time fetch or generation workflow is preferable to runtime
  static-data downloads
- How cache migrations should work when the local canonical schema changes
- Whether later game versions preserve the audited membership relationships
- How localization failures should be represented without corrupting an
  existing cache

# 11. Architectural Direction

The current evidence supports the following architecture:

    Upstream Static Sources
        ↓
    Provider-Specific Parsers
        ↓
    Canonicalization and Validation
        ↓
    Versioned Local Cache
        ↓
    Teyvat Vision Domain

Optional account providers operate beside this path:

    Enka
        ↓
    AccountDataProvider
        ↓
    Optional validation or enrichment

Neither path should write GOOD records directly.

GOOD serialization remains a downstream exporter concern.
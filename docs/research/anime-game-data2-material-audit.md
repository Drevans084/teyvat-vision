# AnimeGameData2 Material Source Audit

- Audit date: 2026-08-21
- Game version: `7.0.0`
- Source: `Dimbreath/AnimeGameData2`
- Source revision: `26df1dfbdf05a82bbb1d97506859f3e1c40718d8`
- Status: Phase 1 material membership boundary approved

## Purpose

This audit establishes the initial AnimeGameData2 material membership boundary
for Teyvat Vision.

The investigation compares the full material source table with Inventory
Kamera's proven six-category scanner scope.

The approved boundary must preserve known scanner behavior without treating
internal, virtual, temporary, or unrelated source rows as account inventory.

## Source Tables

The material investigation uses:

- `MaterialExcelConfigData.json`
- `TextMapEN.json`
- `TextMap_MediumEN.json`

## Source Summary

The pinned material table contains:

- Raw material rows: 10,404
- Unique material IDs: 10,404
- Duplicate material IDs: 0
- Observed material-category groups: 85

AnimeGameData2's material table is broader than the set of objects that can
appear as quantities in the inventory areas supported by Inventory Kamera.

The table includes:

- Inventory materials
- Virtual counters
- Character cards
- Stella Fortuna records
- Cosmetics
- Event objects
- Quest objects
- Food
- Gadgets
- Furniture-related records
- Energy particles
- Internal or test content
- Rows without a material category

The raw table must not be treated as canonical inventory membership without an
explicit product rule.

## Inventory Kamera Baseline

Inventory Kamera selects six material categories:

- `MATERIAL_AVATAR_MATERIAL`
- `MATERIAL_EXCHANGE`
- `MATERIAL_EXP_FRUIT`
- `MATERIAL_FISH_BAIT`
- `MATERIAL_WEAPON_EXP_STONE`
- `MATERIAL_WOOD`

Pinned-source results:

| Source category | Rows | Resolvable names | Unmapped names |
|---|---:|---:|---:|
| `MATERIAL_AVATAR_MATERIAL` | 474 | 474 | 0 |
| `MATERIAL_EXCHANGE` | 244 | 244 | 0 |
| `MATERIAL_EXP_FRUIT` | 3 | 3 | 0 |
| `MATERIAL_FISH_BAIT` | 13 | 13 | 0 |
| `MATERIAL_WEAPON_EXP_STONE` | 3 | 3 | 0 |
| `MATERIAL_WOOD` | 34 | 33 | 1 |
| **Total** | **771** | **770** | **1** |

The 770 resolved rows produce:

- 770 unique raw material IDs
- 770 unique normalized Inventory Kamera keys
- 0 normalized-name collisions

## Unmapped Baseline Row

One selected wood row has no English localization:

- ID: `101306`
- Category: `MATERIAL_WOOD`
- Name hash: `250702940`
- Icon: `UI_ItemIcon_101306`
- Rarity: 1

This row is not included in initial canonical membership because its source
name cannot be resolved through either audited English text map.

## Outside-Baseline Categories

Seventy-nine category groups fall outside the Inventory Kamera baseline.

Some contain legitimate inventory-visible objects, but many categories mix
valid, historical, invalidated, internal, virtual, temporary, or otherwise
unsupported records.

Examples include:

- Artifact enhancement materials
- Resin and consumable bundles
- Food
- Fishing rods
- Seeds
- Gadgets
- Currencies
- Character cards
- Stella Fortuna
- Cosmetics and poses
- Namecards and music
- Event materials
- Quest materials
- Energy particles
- Internal or test packages

Category-wide inclusion would therefore create false canonical membership.

Expanding material coverage requires an explicit canonical material
classification and scanner-scope model rather than an increasingly broad raw
source allowlist.

## Approved Phase 1 Membership Boundary

Canonical Phase 1 material membership is:

    MaterialExcelConfigData row
        +
    materialType in the six Inventory Kamera baseline categories
        +
    nonempty name resolved through TextMapEN or TextMap_MediumEN
        =
    canonical material source membership

This produces 770 canonical materials for the pinned 7.0.0 dataset.

## Canonicalization Requirements

The AnimeGameData2 provider will:

- Use the raw material ID as the canonical identity key.
- Resolve English names through both English text maps.
- Filter membership before canonicalization.
- Preserve source order.
- Exclude unresolved source rows.
- Reject malformed required fields explicitly.
- Keep GOOD keys behind the exporter boundary.

## Unknown Live-Item Policy

Restricting canonical membership must not make the scanner blind to new or
unsupported live inventory items.

Visual recognition must occur before canonical resolution can discard an
observation.

When a visible item cannot be resolved to an approved canonical material, the
scanner should retain an unresolved observation containing available evidence,
including:

- Raw OCR text
- Normalized OCR text
- Screenshot and crop references
- Inventory tab or category
- Visible quantity
- Recognition confidence
- Candidate source records
- Provider version and revision
- Capture timestamp
- Diagnostic context

An unresolved live item must not:

- Be silently discarded
- Be assigned an invented canonical identity
- Be exported as a different known material
- Automatically expand canonical membership

## Promotion Workflow

An unsupported item may enter canonical membership after:

1. It is observed in live inventory evidence.
2. Its existence and scannability are confirmed.
3. Its stable source identity is established.
4. Its material classification and scan scope are approved.
5. Deterministic provider and recognition fixtures are added.
6. The complete quality gate passes.

Previously retained unresolved observations may then be reprocessed against the
expanded canonical dataset.

## Reproducible Audit

The repository-owned audit utility is:

`scripts/audits/audit_anime_game_data_materials.py`

Run it with:

    uv run python scripts/audits/audit_anime_game_data_materials.py \
        datasets/anime-game-data2-live

The raw AnimeGameData2 dataset remains local and uncommitted pending a separate
licensing and redistribution decision.
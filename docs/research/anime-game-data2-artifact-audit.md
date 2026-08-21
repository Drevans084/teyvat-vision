# AnimeGameData2 Artifact Source Audit

- Audit date: 2026-08-21
- Game version: `7.0.0`
- Source: `Dimbreath/AnimeGameData2`
- Source revision: `26df1dfbdf05a82bbb1d97506859f3e1c40718d8`
- Status: Artifact-set membership boundary approved

## Purpose

This audit establishes the AnimeGameData2 artifact-set membership boundary for
Teyvat Vision.

The investigation compares the current source tables with Inventory Kamera's
proven artifact lookup-generation behavior.

The audit does not assume that every display label represents a scannable
artifact set.

## Source Tables

The artifact relationship uses:

- `DisplayItemExcelConfigData.json`
- `ReliquaryCodexExcelConfigData.json`
- `ReliquaryExcelConfigData.json`
- `TextMapEN.json`
- `TextMap_MediumEN.json`

## Inventory Kamera Baseline

Inventory Kamera:

1. Selects display rows whose icon contains `RelicIcon`.
2. Resolves their localized set names.
3. Matches the display `param` to a codex `suitId`.
4. Resolves the codex piece IDs through the reliquary table.
5. Generates a set only when at least one artifact piece is found.

Teyvat Vision retains this proven relational boundary while using raw suit IDs
instead of normalized display names as canonical identity.

## Audit Results

Observed source counts:

- Display-item rows: 334
- RelicIcon display rows: 259
- Unique RelicIcon display suit IDs: 65
- Reliquary-codex rows: 129
- Unique codex suit IDs: 63
- Reliquary rows: 4,352
- Inventory Kamera-compatible suit IDs: 63
- Missing referenced reliquary piece IDs: 0
- Duplicate localized artifact-set names: 0
- Codex-only suit IDs: 0

The codex-backed artifact sets are therefore a strict and internally complete
subset of the RelicIcon display suits.

## Display-Only Source Labels

Two RelicIcon display suit IDs do not have codex membership:

- `15004`: Glacier and Snowfield
- `15012`: Prayers to the Firmament

Each has five display rows, but neither has a matching codex relationship from
which usable artifact pieces can be constructed.

These labels remain documented source observations.

They are not canonical scannable artifact sets because the audited source
provides no corresponding inventory-piece relationship.

## Slot Availability

Of the 63 codex-backed sets:

- 59 reference all five artifact slots.
- 4 reference only the circlet-style `EQUIP_DRESS` slot.

The four one-slot sets are:

- `15009`: Prayers for Illumination
- `15010`: Prayers for Destiny
- `15011`: Prayers for Wisdom
- `15013`: Prayers to Springtime

These prayer sets are valid source members.

Teyvat Vision must not require every canonical artifact set to expose five
slots.

## Approved Membership Boundary

Canonical artifact-set source membership is:

    DisplayItem icon contains "RelicIcon"
        +
    DisplayItem.param matches ReliquaryCodex.suitId
        +
    at least one referenced piece exists in ReliquaryExcelConfigData
        =
    canonical artifact-set membership

This produces 63 canonical artifact-set source members for the pinned 7.0.0
dataset.

## Canonicalization Requirements

The AnimeGameData2 provider will:

- Use the raw suit ID as the canonical artifact-set identity key.
- Resolve English names through both English text maps.
- Preserve the first-occurrence order of qualifying display suits.
- Emit each suit ID once even when multiple display rows reference it.
- Derive available slots from codex piece relationships.
- Preserve legitimate one-slot prayer sets.
- Derive available rarities from referenced reliquary records.
- Reject malformed required fields explicitly.
- Keep GOOD keys behind the exporter boundary.

## Reproducible Audit

The repository-owned audit utility is:

`scripts/audits/audit_anime_game_data_artifacts.py`

Run it with:

    uv run python scripts/audits/audit_anime_game_data_artifacts.py \
        datasets/anime-game-data2-live

The raw AnimeGameData2 dataset remains local and uncommitted pending a separate
licensing and redistribution decision.
# AnimeGameData2 asset audit

## Status

Accepted research record.

## Date

2026-08-21

## Purpose

This audit establishes how Teyvat Vision should associate canonical game-data
entities with symbolic visual asset references.

The goals are to:

- identify the asset fields available in AnimeGameData2;
- verify coverage across canonical characters, weapons, artifact sets, and
  materials;
- compare the proposed design with Inventory Kamera;
- determine which symbolic references can currently be resolved through Enka;
- prevent external asset availability from changing canonical membership;
- define the boundary between static game data, asset resolution, caching, and
  recognition.

This audit does not add image files to the repository or introduce an OCR
dependency.

## Dataset provenance

The audit used the following AnimeGameData2 snapshot:

| Property | Value |
| --- | --- |
| Game version | `7.0.0` |
| Revision | `26df1dfbdf05a82bbb1d97506859f3e1c40718d8` |
| Provider | `Dimbreath/AnimeGameData2` |
| Local dataset role | External audit input |
| Repository status | Not committed |

The dataset contains symbolic asset names in its JSON records, but the audited
checkout contains no PNG, JPEG, WebP, DDS, or other image files.

## Source responsibilities

The proposed asset pipeline assigns separate responsibilities to each source.

| Source | Responsibility |
| --- | --- |
| AnimeGameData2 | Canonical membership, entity relationships, and symbolic asset references |
| Enka.Network | Optional resolution of supported symbolic references to image content |
| Local asset cache | Reproducible, resumable storage of resolved external images |
| Inventory Kamera test runs | Private recognition and regression evidence |
| Teyvat Vision recognition | Combine visual, structural, contextual, and canonical evidence |

AnimeGameData2 remains authoritative for which symbolic references belong to a
canonical entity. Enka availability is not a membership rule.

## Inventory Kamera comparison

The official Inventory Kamera implementation does not provide a static icon
database suitable for reuse as the Teyvat Vision asset catalog.

Its relevant behavior is:

- character `iconName` values help derive textual identifiers;
- artifact display icons containing `RelicIcon` help identify artifact-set
  membership;
- weapon and material lookup generation is primarily textual;
- live inventory recognition depends heavily on captured interface regions and
  Tesseract OCR;
- captured screenshots and OCR crops are observations, not canonical source
  assets.

A private Inventory Kamera test corpus is available outside the repository. It
contains approximately 13 GB and 43,943 PNG files collected from live personal
inventory runs. Those files may include account identifiers and other
user-specific interface content.

The corpus must therefore:

- remain outside Git;
- never be treated as the canonical static icon source;
- be handled as potentially sensitive test evidence;
- be used only through an explicit external regression-data configuration;
- support evaluation of recognition behavior rather than canonical membership.

Teyvat Vision will not adopt Inventory Kamera’s OCR-centered architecture.
Direct visual recognition, structural evidence, and canonical constraints are
the intended primary mechanisms.

## OCR policy

OCR is not part of the accepted asset-provider design and must not be added as
a default recognition dependency.

In particular:

- Tesseract will not be carried forward as a foundational recognition engine;
- this audit does not approve PaddleOCR or any other OCR implementation;
- icon and entity recognition should first use validated visual assets,
  region structure, visual classification, and canonical constraints;
- recognition should preserve uncertainty rather than forcing an OCR-derived
  answer;
- any future OCR use must be isolated behind a replaceable boundary;
- any future OCR dependency must be justified by representative benchmarks
  showing that visual and structural approaches cannot reliably recover the
  required field;
- adopting PaddleOCR or another engine requires a separate documented
  architectural decision.

Some variable textual or numeric fields may later require specialized text
recognition. That possibility does not justify introducing OCR into the static
asset contract or making it the default approach now.

## Symbolic asset roles

The audited source fields support the following proposed roles.

| Asset role | Entity kind | AnimeGameData2 source |
| --- | --- | --- |
| `character_icon` | Character | `AvatarExcelConfigData.iconName` |
| `character_side_icon` | Character | `AvatarExcelConfigData.sideIconName` |
| `weapon_icon` | Weapon | `WeaponExcelConfigData.icon` |
| `weapon_awakened_icon` | Weapon | `WeaponExcelConfigData.awakenIcon` |
| `material_icon` | Material | `MaterialExcelConfigData.icon` |
| `artifact_flower` | Artifact set | Codex `flowerId` to `ReliquaryExcelConfigData.icon` |
| `artifact_plume` | Artifact set | Codex `leatherId` to `ReliquaryExcelConfigData.icon` |
| `artifact_sands` | Artifact set | Codex `sandId` to `ReliquaryExcelConfigData.icon` |
| `artifact_goblet` | Artifact set | Codex `cupId` to `ReliquaryExcelConfigData.icon` |
| `artifact_circlet` | Artifact set | Codex `capId` to `ReliquaryExcelConfigData.icon` |

The asset role must be represented explicitly in the provider-independent
contract. A subject plus an untyped reference is insufficient because one
entity can have several assets with different meanings.

## Representative source references

The following records demonstrate the relationship between canonical subjects
and symbolic asset names.

| Subject | Source field | Symbolic reference |
| --- | --- | --- |
| Character `10000047` | `iconName` | `UI_AvatarIcon_Kazuha` |
| Character `10000047` | `sideIconName` | `UI_AvatarIcon_Side_Kazuha` |
| Weapon `11509` | `icon` | `UI_EquipIcon_Sword_Narukami` |
| Weapon `11509` | `awakenIcon` | `UI_EquipIcon_Sword_Narukami_Awaken` |
| Material `104003` | `icon` | `UI_ItemIcon_104003` |
| Artifact set `15001`, flower | Reliquary `icon` | `UI_RelicIcon_15001_4` |

These references identify external visual resources. They are not local file
paths and must not imply that the image has already been downloaded.

## Local relationship audit

The local audit applies the same canonical membership rules as the
AnimeGameData2 provider and then extracts every supported asset role.

### Canonical subjects

| Entity kind | Canonical subjects |
| --- | ---: |
| Characters | 122 |
| Weapons | 263 |
| Artifact sets | 63 |
| Materials | 770 |

### Role coverage

| Asset role | Expected subjects | Referenced subjects | Missing subjects |
| --- | ---: | ---: | ---: |
| `character_icon` | 122 | 122 | 0 |
| `character_side_icon` | 122 | 122 | 0 |
| `weapon_icon` | 263 | 263 | 0 |
| `weapon_awakened_icon` | 263 | 263 | 0 |
| `material_icon` | 770 | 770 | 0 |
| `artifact_flower` | 59 | 59 | 0 |
| `artifact_plume` | 59 | 59 | 0 |
| `artifact_sands` | 59 | 59 | 0 |
| `artifact_goblet` | 59 | 59 | 0 |
| `artifact_circlet` | 63 | 63 | 0 |

Four artifact sets are circlet-only sets. Their absence from the other four
artifact roles is expected and follows the slot availability established by
the artifact-set provider.

### Relationship totals

| Measurement | Result |
| --- | ---: |
| Candidate subject/reference relationships | 1,839 |
| Unique symbolic references | 1,811 |
| Invalid or blank references | 0 |
| Missing referenced reliquary piece IDs | 0 |
| Subject-role pairs with multiple references | 0 |
| References shared by multiple subjects | 14 |
| References shared across entity kinds | 0 |

The difference between 1,839 relationships and 1,811 unique references is
caused by legitimate reference reuse.

## Symbolic references are not identities

Fourteen symbolic references are shared by multiple canonical subjects.

Examples include:

- `UI_EquipIcon_Bow_Hunters`;
- `UI_EquipIcon_Catalyst_Apprentice`;
- `UI_EquipIcon_Claymore_Aniki`;
- `UI_EquipIcon_Pole_Gewalt`;
- `UI_EquipIcon_Sword_Blunt`;
- `UI_EquipIcon_Sword_Purewill`;
- `UI_EquipIcon_Sword_YoutouEnchanted`;
- `UI_ItemIcon_100061`;
- `UI_ItemIcon_100064`.

Several awakened weapon references are shared in the same way.

Consequences:

- an asset reference must never replace a canonical ID;
- a matching icon may produce multiple identity candidates;
- recognition must combine icon evidence with other visual, structural, and
  canonical observations;
- asset-reference uniqueness must not be enforced globally;
- duplicate image content may be stored once while retaining every
  subject-and-role relationship.

## Enka.Network boundary

Official Enka.Network documentation states that character, weapon, and
artifact icons can be requested using:

`https://enka.network/ui/[icon_name].png`

Official sources:

- <https://api.enka.network/>
- <https://github.com/EnkaNetwork/API-docs>
- <https://github.com/EnkaNetwork/API-docs/blob/master/docs/gi/api.md#icons-and-images>

Two distinct integrations may eventually use Enka:

1. An optional account-data provider can consume public account or showcase
   data.
2. An asset resolver can translate symbolic icon references into image
   responses.

These integrations must remain separate. The availability of an account API
does not make Enka the canonical static game-data provider.

No documented bulk icon archive or full-icon export endpoint was identified
during this audit. A future complete cache should therefore be based on the
audited symbolic-reference manifest unless Enka publishes an official bulk
mechanism.

## Enka resolution audit

The remote audit issued one sequential HTTP `HEAD` request for each unique
symbolic reference. It used a 0.25-second delay between requests and did not
download image bodies.

Because Enka is an external live service, these results describe availability
at the audit date rather than a permanent guarantee.

### Overall results

| Measurement | Result |
| --- | ---: |
| Unique references checked | 1,811 |
| HTTP 200 responses | 1,629 |
| HTTP 404 responses | 182 |
| Image responses | 1,629 |
| Overall resolution coverage | 89.95% |

### Coverage by entity group

| Entity group | Unique references | Resolved | Unresolved | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Characters | 244 | 244 | 0 | 100.00% |
| Artifact pieces | 299 | 299 | 0 | 100.00% |
| Weapons | 500 | 492 | 8 | 98.40% |
| Materials | 768 | 594 | 174 | 77.34% |

The official icon documentation explicitly describes characters, weapons, and
artifacts. It does not promise complete material-icon coverage. The observed
material results must therefore be treated as opportunistic resolver coverage,
not an Enka contract.

## Unresolved weapon references

The eight unresolved weapon references form four base-and-awakened pairs:

- `UI_EquipIcon_Bow_Hardwood`
- `UI_EquipIcon_Bow_Hardwood_Awaken`
- `UI_EquipIcon_Catalyst_Amber`
- `UI_EquipIcon_Catalyst_Amber_Awaken`
- `UI_EquipIcon_Claymore_Quartz`
- `UI_EquipIcon_Claymore_Quartz_Awaken`
- `UI_EquipIcon_Pole_Flagpole`
- `UI_EquipIcon_Pole_Flagpole_Awaken`

These are still valid AnimeGameData2 symbolic references. They must remain in
provider output even though Enka returned `404` during this audit.

The other 174 unresolved references are material references using the
`UI_ItemIcon_*` naming family.

## Accepted provider behavior

`AnimeGameDataProvider.assets()` should:

- derive assets only for canonical provider members;
- emit all 1,839 valid subject, role, and symbolic-reference relationships;
- preserve source order where that order is meaningful;
- use canonical IDs already produced by the provider;
- include typed asset roles;
- preserve symbolic reference spelling and case;
- reject malformed required asset fields;
- derive artifact roles through codex-to-reliquary relationships;
- avoid all network access;
- remain deterministic for a fixed dataset revision.

It must not:

- call Enka while loading static data;
- omit a symbolic reference because Enka currently returns `404`;
- use an asset reference as a canonical identity;
- infer canonical membership from asset availability;
- write downloaded images into the source repository.

## Accepted resolver behavior

A future Enka asset resolver should:

- accept a symbolic reference independently of the static provider;
- construct the supported Enka URL deterministically;
- distinguish resolved, unresolved, and transient-failure outcomes;
- validate successful content as an image;
- support timeouts, retries, and respectful rate limiting;
- expose provenance for the resolved content;
- allow another resolver or local cache to replace Enka;
- avoid silently converting a resolver failure into a membership decision.

A missing Enka image is an unresolved external asset, not invalid game data.

## Future external cache

A complete icon pull may be performed later, but the resulting images must
remain outside Git.

If no official bulk endpoint becomes available, the cache process should:

1. generate a manifest from the provider’s symbolic asset relationships;
2. deduplicate requests by symbolic reference;
3. download references sequentially or with conservative bounded concurrency;
4. resume without re-downloading verified content;
5. retain unresolved references for later retries;
6. validate status, content type, and nonzero content length;
7. hash downloaded bytes with SHA-256;
8. record source URL and retrieval time;
9. preserve every subject-and-role relationship even when content is
   deduplicated;
10. produce a machine-readable summary suitable for regression checks.

A cache manifest should record at least:

- canonical subject;
- asset role;
- symbolic reference;
- source URL;
- resolver name;
- HTTP status or failure category;
- content type;
- byte length;
- SHA-256 digest;
- retrieval timestamp;
- local cache key.

Licensing, redistribution, and upstream service terms must be reviewed before
any downloaded image set is distributed.

## Recognition implications

Resolved icons can support recognition, but no icon should be used as the sole
identity signal.

Teyvat Vision should prioritize evidence such as:

- direct visual similarity against validated static assets;
- region and interface-layout classification;
- visual item-category indicators;
- visual weapon-type indicators;
- visual rarity indicators;
- visual artifact-slot indicators;
- artifact-set compatibility;
- canonical entity compatibility;
- relationships between observations;
- confidence and ambiguity across candidate identities.

Shared references make this multi-evidence approach mandatory rather than
optional.

This recognition direction does not include OCR by default. If later
experiments demonstrate that a required variable field cannot be recovered
reliably through the accepted visual and structural pipeline, OCR can be
evaluated separately under the policy established above.

## Reproduction reference

The following commands are retained only to document how this audit can be
reproduced in the future. Do not run the remote commands as part of this
documentation change.

Run the local relationship audit without network access:

```powershell
uv run python scripts\audits\audit_anime_game_data_assets.py `
    datasets\anime-game-data2-live
```

Run a limited Enka connectivity sample when a future connectivity check is
required:

```powershell
uv run python scripts\audits\audit_anime_game_data_assets.py `
    datasets\anime-game-data2-live `
    --check-enka `
    --resolve-limit 10 `
    --delay 0.25 `
    --timeout 15
```

Run the complete sequential Enka availability audit only when a new dataset
snapshot requires a new recorded result:

```powershell
uv run python scripts\audits\audit_anime_game_data_assets.py `
    datasets\anime-game-data2-live `
    --check-enka `
    --delay 0.25 `
    --timeout 15
```

The complete command currently performs 1,811 remote requests and should not
be repeated unnecessarily.

## Conclusion

AnimeGameData2 provides complete symbolic asset-role coverage for all canonical
subjects in the audited 7.0.0 snapshot.

Enka resolves all audited character and artifact references, nearly all weapon
references, and most material references. Its incomplete material coverage and
the live nature of the service mean it must remain an optional resolver rather
than a membership authority.

The provider should preserve the full symbolic relationship set. Asset
resolution, caching, and recognition belong behind separate boundaries, and
all downloaded images and personal Inventory Kamera evidence must remain
outside the repository.

This audit does not approve or introduce an OCR dependency. Any future OCR
adoption requires separate evidence, benchmarking, and architectural review.
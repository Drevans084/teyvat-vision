import json
from pathlib import Path

from teyvat_vision.domain.artifact import ArtifactSlot
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import Rarity
from teyvat_vision.game_data.localization import LocalizedName
from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider
from teyvat_vision.game_data.records import ArtifactSetDefinition

type JsonValue = str | int | float | bool | list[JsonValue] | dict[str, JsonValue] | None


def write_json(
    root: Path,
    relative_path: str,
    data: JsonValue,
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def display(
    suit_id: int,
    *,
    name_hash: int = 100,
) -> dict[str, JsonValue]:
    return {
        "param": suit_id,
        "nameTextMapHash": name_hash,
        "icon": "UI_RelicIcon_Test",
    }


def codex(
    suit_id: int,
    *,
    flower_id: int = 0,
    plume_id: int = 0,
    sands_id: int = 0,
    goblet_id: int = 0,
    circlet_id: int = 0,
) -> dict[str, JsonValue]:
    return {
        "suitId": suit_id,
        "flowerId": flower_id,
        "leatherId": plume_id,
        "sandId": sands_id,
        "cupId": goblet_id,
        "capId": circlet_id,
    }


def reliquary(
    piece_id: int,
    *,
    equip_type: str,
    rank_level: int,
) -> dict[str, JsonValue]:
    return {
        "id": piece_id,
        "equipType": equip_type,
        "rankLevel": rank_level,
    }


def write_artifact_source(
    root: Path,
    *,
    displays: JsonValue,
    codex_rows: JsonValue,
    reliquaries: JsonValue,
    full_text_map: JsonValue,
    medium_text_map: JsonValue,
) -> None:
    write_json(
        root,
        "ExcelBinOutput/DisplayItemExcelConfigData.json",
        displays,
    )
    write_json(
        root,
        "ExcelBinOutput/ReliquaryCodexExcelConfigData.json",
        codex_rows,
    )
    write_json(
        root,
        "ExcelBinOutput/ReliquaryExcelConfigData.json",
        reliquaries,
    )
    write_json(
        root,
        "TextMap/TextMapEN.json",
        full_text_map,
    )
    write_json(
        root,
        "TextMap/TextMap_MediumEN.json",
        medium_text_map,
    )


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def load_artifact_set(
    root: Path,
    *,
    name_hash: int = 100,
    full_text_map: JsonValue = None,
    medium_text_map: JsonValue = None,
) -> ArtifactSetDefinition:
    write_artifact_source(
        root,
        displays=[
            display(
                15001,
                name_hash=name_hash,
            ),
        ],
        codex_rows=[
            codex(
                15001,
                flower_id=501,
            ),
        ],
        reliquaries=[
            reliquary(
                501,
                equip_type="EQUIP_BRACER",
                rank_level=5,
            ),
        ],
        full_text_map=({"100": "Gladiator's Finale"} if full_text_map is None else full_text_map),
        medium_text_map=({} if medium_text_map is None else medium_text_map),
    )

    return provider(root).artifact_sets()[0]


def test_anime_game_data_provider_loads_artifact_set_record(
    tmp_path: Path,
) -> None:
    definition = load_artifact_set(tmp_path)

    assert isinstance(definition, ArtifactSetDefinition)


def test_artifact_set_uses_raw_suit_id_as_canonical_key(
    tmp_path: Path,
) -> None:
    definition = load_artifact_set(tmp_path)

    assert definition.identity == CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key="15001",
    )


def test_artifact_set_preserves_resolved_english_name(
    tmp_path: Path,
) -> None:
    definition = load_artifact_set(tmp_path)

    assert definition.names == (
        LocalizedName(
            locale="en",
            value="Gladiator's Finale",
        ),
    )


def test_artifact_set_resolves_name_from_medium_english_text_map(
    tmp_path: Path,
) -> None:
    definition = load_artifact_set(
        tmp_path,
        name_hash=200,
        full_text_map={},
        medium_text_map={
            "200": "Wanderer's Troupe",
        },
    )

    assert definition.names == (
        LocalizedName(
            locale="en",
            value="Wanderer's Troupe",
        ),
    )


def test_artifact_set_derives_all_available_slots(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(15001),
        ],
        codex_rows=[
            codex(
                15001,
                flower_id=501,
                plume_id=502,
                sands_id=503,
                goblet_id=504,
                circlet_id=505,
            ),
        ],
        reliquaries=[
            reliquary(
                501,
                equip_type="EQUIP_BRACER",
                rank_level=5,
            ),
            reliquary(
                502,
                equip_type="EQUIP_NECKLACE",
                rank_level=5,
            ),
            reliquary(
                503,
                equip_type="EQUIP_SHOES",
                rank_level=5,
            ),
            reliquary(
                504,
                equip_type="EQUIP_RING",
                rank_level=5,
            ),
            reliquary(
                505,
                equip_type="EQUIP_DRESS",
                rank_level=5,
            ),
        ],
        full_text_map={
            "100": "Gladiator's Finale",
        },
        medium_text_map={},
    )

    definition = provider(tmp_path).artifact_sets()[0]

    assert definition.slots == (
        ArtifactSlot.FLOWER,
        ArtifactSlot.PLUME,
        ArtifactSlot.SANDS,
        ArtifactSlot.GOBLET,
        ArtifactSlot.CIRCLET,
    )


def test_artifact_set_preserves_circlet_only_slot_availability(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(15009),
        ],
        codex_rows=[
            codex(
                15009,
                circlet_id=509,
            ),
        ],
        reliquaries=[
            reliquary(
                509,
                equip_type="EQUIP_DRESS",
                rank_level=4,
            ),
        ],
        full_text_map={
            "100": "Prayers for Illumination",
        },
        medium_text_map={},
    )

    definition = provider(tmp_path).artifact_sets()[0]

    assert definition.slots == (ArtifactSlot.CIRCLET,)


def test_artifact_set_derives_unique_rarities_in_ascending_order(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(15001),
        ],
        codex_rows=[
            codex(
                15001,
                flower_id=501,
            ),
            codex(
                15001,
                flower_id=401,
            ),
        ],
        reliquaries=[
            reliquary(
                501,
                equip_type="EQUIP_BRACER",
                rank_level=5,
            ),
            reliquary(
                401,
                equip_type="EQUIP_BRACER",
                rank_level=4,
            ),
        ],
        full_text_map={
            "100": "Gladiator's Finale",
        },
        medium_text_map={},
    )

    definition = provider(tmp_path).artifact_sets()[0]

    assert definition.rarities == (
        Rarity.FOUR_STAR,
        Rarity.FIVE_STAR,
    )

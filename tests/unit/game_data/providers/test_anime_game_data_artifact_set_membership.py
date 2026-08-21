import json
from pathlib import Path

from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider

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
    icon: str = "UI_RelicIcon_Test",
) -> dict[str, JsonValue]:
    return {
        "param": suit_id,
        "nameTextMapHash": name_hash,
        "icon": icon,
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
    equip_type: str = "EQUIP_BRACER",
    rank_level: int = 5,
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
        {
            "100": "Test Set",
            "200": "Other Set",
        },
    )
    write_json(
        root,
        "TextMap/TextMap_MediumEN.json",
        {},
    )


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def artifact_set_keys(
    root: Path,
) -> tuple[str, ...]:
    return tuple(definition.identity.key for definition in provider(root).artifact_sets())


def test_artifact_set_membership_requires_display_codex_and_piece_relationship(
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
        ],
        reliquaries=[
            reliquary(501),
        ],
    )

    assert artifact_set_keys(tmp_path) == ("15001",)


def test_artifact_set_membership_requires_relic_icon_display(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(
                15001,
                icon="UI_ItemIcon_Test",
            ),
        ],
        codex_rows=[
            codex(
                15001,
                flower_id=501,
            ),
        ],
        reliquaries=[
            reliquary(501),
        ],
    )

    assert artifact_set_keys(tmp_path) == ()


def test_artifact_set_membership_requires_matching_codex_suit(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(15001),
        ],
        codex_rows=[
            codex(
                15002,
                flower_id=502,
            ),
        ],
        reliquaries=[
            reliquary(502),
        ],
    )

    assert artifact_set_keys(tmp_path) == ()


def test_artifact_set_membership_requires_referenced_reliquary_piece(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(15001),
        ],
        codex_rows=[
            codex(15001),
        ],
        reliquaries=[
            reliquary(999),
        ],
    )

    assert artifact_set_keys(tmp_path) == ()


def test_circlet_only_prayer_set_remains_canonical_member(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(
                15009,
                name_hash=200,
            ),
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
    )

    assert artifact_set_keys(tmp_path) == ("15009",)


def test_artifact_set_membership_emits_each_suit_once_in_display_order(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(
                15002,
                name_hash=200,
                icon="UI_RelicIcon_15002_4",
            ),
            display(
                15001,
                icon="UI_RelicIcon_15001_4",
            ),
            display(
                15002,
                name_hash=200,
                icon="UI_RelicIcon_15002_5",
            ),
        ],
        codex_rows=[
            codex(
                15001,
                flower_id=501,
            ),
            codex(
                15002,
                flower_id=502,
            ),
        ],
        reliquaries=[
            reliquary(501),
            reliquary(502),
        ],
    )

    assert artifact_set_keys(tmp_path) == (
        "15002",
        "15001",
    )


def test_codex_suit_without_relic_icon_display_is_not_canonical_member(
    tmp_path: Path,
) -> None:
    write_artifact_source(
        tmp_path,
        displays=[
            display(
                15002,
                icon="UI_ItemIcon_Test",
            ),
        ],
        codex_rows=[
            codex(
                15001,
                flower_id=501,
            ),
        ],
        reliquaries=[
            reliquary(501),
        ],
    )

    assert artifact_set_keys(tmp_path) == ()

import json
from pathlib import Path

import pytest

from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider

type JsonValue = str | int | float | bool | list[JsonValue] | dict[str, JsonValue] | None

_TABLE_PATHS = (
    "ExcelBinOutput/AvatarExcelConfigData.json",
    "ExcelBinOutput/WeaponExcelConfigData.json",
    "ExcelBinOutput/DisplayItemExcelConfigData.json",
    "ExcelBinOutput/ReliquaryCodexExcelConfigData.json",
    "ExcelBinOutput/ReliquaryExcelConfigData.json",
    "ExcelBinOutput/MaterialExcelConfigData.json",
)

_ASSET_FIELDS = (
    (
        "ExcelBinOutput/AvatarExcelConfigData.json",
        "iconName",
    ),
    (
        "ExcelBinOutput/AvatarExcelConfigData.json",
        "sideIconName",
    ),
    (
        "ExcelBinOutput/WeaponExcelConfigData.json",
        "icon",
    ),
    (
        "ExcelBinOutput/WeaponExcelConfigData.json",
        "awakenIcon",
    ),
    (
        "ExcelBinOutput/ReliquaryExcelConfigData.json",
        "icon",
    ),
    (
        "ExcelBinOutput/MaterialExcelConfigData.json",
        "icon",
    ),
)


def write_json(
    root: Path,
    relative_path: str,
    data: object,
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def valid_records() -> dict[str, list[dict[str, JsonValue]]]:
    return {
        "ExcelBinOutput/AvatarExcelConfigData.json": [
            {
                "id": 10000047,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
                "iconName": "UI_AvatarIcon_Kazuha",
                "sideIconName": "UI_AvatarIcon_Side_Kazuha",
            },
        ],
        "ExcelBinOutput/FetterInfoExcelConfigData.json": [
            {
                "avatarId": 10000047,
            },
        ],
        "ExcelBinOutput/WeaponExcelConfigData.json": [
            {
                "id": 11509,
                "nameTextMapHash": 200,
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "rankLevel": 5,
                "icon": "UI_EquipIcon_Sword_Narukami",
                "awakenIcon": "UI_EquipIcon_Sword_Narukami_Awaken",
            },
        ],
        "ExcelBinOutput/DisplayItemExcelConfigData.json": [
            {
                "param": 15001,
                "nameTextMapHash": 300,
                "icon": "UI_RelicIcon_15001_4",
            },
        ],
        "ExcelBinOutput/ReliquaryCodexExcelConfigData.json": [
            {
                "suitId": 15001,
                "flowerId": 501,
                "leatherId": 0,
                "sandId": 0,
                "cupId": 0,
                "capId": 0,
            },
        ],
        "ExcelBinOutput/ReliquaryExcelConfigData.json": [
            {
                "id": 501,
                "equipType": "EQUIP_BRACER",
                "rankLevel": 5,
                "icon": "UI_RelicIcon_15001_4",
            },
        ],
        "ExcelBinOutput/MaterialExcelConfigData.json": [
            {
                "id": 104003,
                "nameTextMapHash": 400,
                "materialType": "MATERIAL_AVATAR_MATERIAL",
                "itemType": "ITEM_MATERIAL",
                "icon": "UI_ItemIcon_104003",
            },
        ],
    }


def write_valid_source(root: Path) -> None:
    for relative_path, records in valid_records().items():
        write_json(
            root,
            relative_path,
            records,
        )

    write_json(
        root,
        "TextMap/TextMapEN.json",
        {
            "200": "Mistsplitter Reforged",
            "300": "Gladiator's Finale",
            "400": "Teachings of Freedom",
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


@pytest.mark.parametrize(
    "relative_path",
    _TABLE_PATHS,
)
def test_assets_validate_required_source_tables_are_not_empty(
    tmp_path: Path,
    relative_path: str,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        relative_path,
        [],
    )

    with pytest.raises(ValueError, match="must not be empty"):
        provider(tmp_path).assets()


@pytest.mark.parametrize(
    ("relative_path", "field"),
    _ASSET_FIELDS,
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        123,
        "",
    ],
)
def test_canonical_asset_reference_must_be_non_empty_string(
    tmp_path: Path,
    relative_path: str,
    field: str,
    invalid_value: JsonValue,
) -> None:
    write_valid_source(tmp_path)
    records = valid_records()[relative_path]
    records[0][field] = invalid_value
    write_json(
        tmp_path,
        relative_path,
        records,
    )

    with pytest.raises(
        ValueError,
        match=rf"{field!r}.*non-empty string",
    ):
        provider(tmp_path).assets()


@pytest.mark.parametrize(
    "invalid_reference",
    [
        "   ",
        " UI_AvatarIcon_Kazuha ",
    ],
)
def test_canonical_asset_reference_rejects_invalid_whitespace(
    tmp_path: Path,
    invalid_reference: str,
) -> None:
    write_valid_source(tmp_path)
    records = valid_records()["ExcelBinOutput/AvatarExcelConfigData.json"]
    records[0]["iconName"] = invalid_reference
    write_json(
        tmp_path,
        "ExcelBinOutput/AvatarExcelConfigData.json",
        records,
    )

    with pytest.raises(ValueError, match="reference"):
        provider(tmp_path).assets()

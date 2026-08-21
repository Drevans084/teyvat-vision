import json
from pathlib import Path

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import AssetRole, GameDataAsset
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


def write_source(root: Path) -> None:
    write_json(
        root,
        "ExcelBinOutput/AvatarExcelConfigData.json",
        [
            {
                "id": 10000047,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
                "iconName": "UI_AvatarIcon_Kazuha",
                "sideIconName": "UI_AvatarIcon_Side_Kazuha",
            },
        ],
    )
    write_json(
        root,
        "ExcelBinOutput/FetterInfoExcelConfigData.json",
        [
            {
                "avatarId": 10000047,
            },
        ],
    )
    write_json(
        root,
        "ExcelBinOutput/WeaponExcelConfigData.json",
        [
            {
                "id": 11509,
                "nameTextMapHash": 200,
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "rankLevel": 5,
                "icon": "UI_EquipIcon_Sword_Narukami",
                "awakenIcon": "UI_EquipIcon_Sword_Narukami_Awaken",
            },
        ],
    )
    write_json(
        root,
        "ExcelBinOutput/DisplayItemExcelConfigData.json",
        [
            {
                "param": 15001,
                "nameTextMapHash": 300,
                "icon": "UI_RelicIcon_15001_4",
            },
        ],
    )
    write_json(
        root,
        "ExcelBinOutput/ReliquaryCodexExcelConfigData.json",
        [
            {
                "suitId": 15001,
                "flowerId": 501,
                "leatherId": 502,
                "sandId": 503,
                "cupId": 504,
                "capId": 505,
            },
        ],
    )
    write_json(
        root,
        "ExcelBinOutput/ReliquaryExcelConfigData.json",
        [
            {
                "id": 501,
                "equipType": "EQUIP_BRACER",
                "rankLevel": 5,
                "icon": "UI_RelicIcon_15001_4",
            },
            {
                "id": 502,
                "equipType": "EQUIP_NECKLACE",
                "rankLevel": 5,
                "icon": "UI_RelicIcon_15001_2",
            },
            {
                "id": 503,
                "equipType": "EQUIP_SHOES",
                "rankLevel": 5,
                "icon": "UI_RelicIcon_15001_5",
            },
            {
                "id": 504,
                "equipType": "EQUIP_RING",
                "rankLevel": 5,
                "icon": "UI_RelicIcon_15001_1",
            },
            {
                "id": 505,
                "equipType": "EQUIP_DRESS",
                "rankLevel": 5,
                "icon": "UI_RelicIcon_15001_3",
            },
        ],
    )
    write_json(
        root,
        "ExcelBinOutput/MaterialExcelConfigData.json",
        [
            {
                "id": 104003,
                "nameTextMapHash": 400,
                "materialType": "MATERIAL_AVATAR_MATERIAL",
                "itemType": "ITEM_MATERIAL",
                "icon": "UI_ItemIcon_104003",
            },
        ],
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


def test_assets_preserve_subject_role_reference_and_deterministic_order(
    tmp_path: Path,
) -> None:
    write_source(tmp_path)

    assert provider(tmp_path).assets() == (
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000047",
            ),
            role=AssetRole.CHARACTER_ICON,
            reference="UI_AvatarIcon_Kazuha",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000047",
            ),
            role=AssetRole.CHARACTER_SIDE_ICON,
            reference="UI_AvatarIcon_Side_Kazuha",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            role=AssetRole.WEAPON_ICON,
            reference="UI_EquipIcon_Sword_Narukami",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            role=AssetRole.WEAPON_AWAKENED_ICON,
            reference="UI_EquipIcon_Sword_Narukami_Awaken",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            role=AssetRole.ARTIFACT_FLOWER,
            reference="UI_RelicIcon_15001_4",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            role=AssetRole.ARTIFACT_PLUME,
            reference="UI_RelicIcon_15001_2",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            role=AssetRole.ARTIFACT_SANDS,
            reference="UI_RelicIcon_15001_5",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            role=AssetRole.ARTIFACT_GOBLET,
            reference="UI_RelicIcon_15001_1",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            role=AssetRole.ARTIFACT_CIRCLET,
            reference="UI_RelicIcon_15001_3",
        ),
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.MATERIAL,
                key="104003",
            ),
            role=AssetRole.MATERIAL_ICON,
            reference="UI_ItemIcon_104003",
        ),
    )

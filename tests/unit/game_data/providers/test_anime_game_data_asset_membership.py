import json
from pathlib import Path

from teyvat_vision.game_data.assets import AssetRole
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


def character(
    character_id: int,
    *,
    use_type: str = "AVATAR_FORMAL",
    icon: JsonValue = "UI_AvatarIcon_Test",
    side_icon: JsonValue = "UI_AvatarIcon_Side_Test",
) -> dict[str, JsonValue]:
    return {
        "id": character_id,
        "useType": use_type,
        "weaponType": "WEAPON_SWORD_ONE_HAND",
        "qualityType": "QUALITY_ORANGE",
        "iconName": icon,
        "sideIconName": side_icon,
    }


def weapon(
    weapon_id: int,
    name_hash: int,
    *,
    icon: JsonValue = "UI_EquipIcon_Test",
    awakened_icon: JsonValue = "UI_EquipIcon_Test_Awaken",
) -> dict[str, JsonValue]:
    return {
        "id": weapon_id,
        "nameTextMapHash": name_hash,
        "weaponType": "WEAPON_SWORD_ONE_HAND",
        "rankLevel": 5,
        "icon": icon,
        "awakenIcon": awakened_icon,
    }


def display(
    suit_id: int,
    name_hash: int,
    *,
    icon: JsonValue = "UI_RelicIcon_Test",
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
    circlet_id: int = 0,
) -> dict[str, JsonValue]:
    return {
        "suitId": suit_id,
        "flowerId": flower_id,
        "leatherId": 0,
        "sandId": 0,
        "cupId": 0,
        "capId": circlet_id,
    }


def reliquary(
    piece_id: int,
    *,
    equip_type: str,
    icon: JsonValue,
) -> dict[str, JsonValue]:
    return {
        "id": piece_id,
        "equipType": equip_type,
        "rankLevel": 5,
        "icon": icon,
    }


def material(
    material_id: int,
    name_hash: int,
    *,
    material_type: str = "MATERIAL_AVATAR_MATERIAL",
    icon: JsonValue = "UI_ItemIcon_Test",
) -> dict[str, JsonValue]:
    return {
        "id": material_id,
        "nameTextMapHash": name_hash,
        "materialType": material_type,
        "itemType": "ITEM_MATERIAL",
        "icon": icon,
    }


def write_source(
    root: Path,
    *,
    avatars: JsonValue,
    fetters: JsonValue,
    weapons: JsonValue,
    displays: JsonValue,
    codex_rows: JsonValue,
    reliquaries: JsonValue,
    materials: JsonValue,
    full_text_map: JsonValue,
) -> None:
    write_json(root, "ExcelBinOutput/AvatarExcelConfigData.json", avatars)
    write_json(root, "ExcelBinOutput/FetterInfoExcelConfigData.json", fetters)
    write_json(root, "ExcelBinOutput/WeaponExcelConfigData.json", weapons)
    write_json(root, "ExcelBinOutput/DisplayItemExcelConfigData.json", displays)
    write_json(root, "ExcelBinOutput/ReliquaryCodexExcelConfigData.json", codex_rows)
    write_json(root, "ExcelBinOutput/ReliquaryExcelConfigData.json", reliquaries)
    write_json(root, "ExcelBinOutput/MaterialExcelConfigData.json", materials)
    write_json(root, "TextMap/TextMapEN.json", full_text_map)
    write_json(root, "TextMap/TextMap_MediumEN.json", {})


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def asset_keys(
    root: Path,
) -> tuple[tuple[str, AssetRole], ...]:
    return tuple((asset.subject.key, asset.role) for asset in provider(root).assets())


def test_assets_are_emitted_only_for_canonical_provider_members(
    tmp_path: Path,
) -> None:
    write_source(
        tmp_path,
        avatars=[
            character(10000047),
            character(
                10000048,
                use_type="AVATAR_ABANDON",
            ),
        ],
        fetters=[
            {"avatarId": 10000047},
            {"avatarId": 10000048},
        ],
        weapons=[
            weapon(11509, 200),
            weapon(11510, 999),
        ],
        displays=[
            display(15001, 300),
            display(15002, 301),
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
                icon="UI_RelicIcon_15001_4",
            ),
        ],
        materials=[
            material(104003, 400),
            material(
                105001,
                401,
                material_type="MATERIAL_RELIQUARY_MATERIAL",
            ),
        ],
        full_text_map={
            "200": "Mistsplitter Reforged",
            "300": "Gladiator's Finale",
            "301": "Display Only Set",
            "400": "Teachings of Freedom",
            "401": "Sanctifying Droplet",
        },
    )

    assert asset_keys(tmp_path) == (
        (
            "10000047",
            AssetRole.CHARACTER_ICON,
        ),
        (
            "10000047",
            AssetRole.CHARACTER_SIDE_ICON,
        ),
        (
            "11509",
            AssetRole.WEAPON_ICON,
        ),
        (
            "11509",
            AssetRole.WEAPON_AWAKENED_ICON,
        ),
        (
            "15001",
            AssetRole.ARTIFACT_FLOWER,
        ),
        (
            "104003",
            AssetRole.MATERIAL_ICON,
        ),
    )


def test_circlet_only_artifact_set_emits_only_circlet_asset(
    tmp_path: Path,
) -> None:
    write_source(
        tmp_path,
        avatars=[character(10000047)],
        fetters=[{"avatarId": 10000047}],
        weapons=[weapon(11509, 200)],
        displays=[display(15009, 300)],
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
                icon="UI_RelicIcon_15009_3",
            ),
        ],
        materials=[material(104003, 400)],
        full_text_map={
            "200": "Mistsplitter Reforged",
            "300": "Prayers for Illumination",
            "400": "Teachings of Freedom",
        },
    )

    artifact_assets = tuple(
        asset for asset in provider(tmp_path).assets() if asset.subject.key == "15009"
    )

    assert tuple(asset.role for asset in artifact_assets) == (AssetRole.ARTIFACT_CIRCLET,)
    assert artifact_assets[0].reference == "UI_RelicIcon_15009_3"


def test_shared_reference_is_preserved_for_each_canonical_subject(
    tmp_path: Path,
) -> None:
    write_source(
        tmp_path,
        avatars=[character(10000047)],
        fetters=[{"avatarId": 10000047}],
        weapons=[
            weapon(
                11101,
                200,
                icon="UI_EquipIcon_Sword_Blunt",
                awakened_icon="UI_EquipIcon_Sword_Blunt_Awaken",
            ),
            weapon(
                11506,
                201,
                icon="UI_EquipIcon_Sword_Blunt",
                awakened_icon="UI_EquipIcon_Sword_Blunt_Awaken",
            ),
        ],
        displays=[display(15001, 300)],
        codex_rows=[codex(15001, flower_id=501)],
        reliquaries=[
            reliquary(
                501,
                equip_type="EQUIP_BRACER",
                icon="UI_RelicIcon_15001_4",
            ),
        ],
        materials=[material(104003, 400)],
        full_text_map={
            "200": "Dull Blade",
            "201": "Primordial Jade Cutter",
            "300": "Gladiator's Finale",
            "400": "Teachings of Freedom",
        },
    )

    shared_assets = tuple(
        asset
        for asset in provider(tmp_path).assets()
        if asset.reference == "UI_EquipIcon_Sword_Blunt"
    )

    assert tuple(asset.subject.key for asset in shared_assets) == (
        "11101",
        "11506",
    )


def test_membership_filter_runs_before_asset_reference_validation(
    tmp_path: Path,
) -> None:
    write_source(
        tmp_path,
        avatars=[
            character(10000047),
            character(
                10000048,
                use_type="AVATAR_ABANDON",
                icon=None,
                side_icon=None,
            ),
        ],
        fetters=[
            {"avatarId": 10000047},
            {"avatarId": 10000048},
        ],
        weapons=[
            weapon(11509, 200),
            weapon(
                11510,
                999,
                icon=None,
                awakened_icon=None,
            ),
        ],
        displays=[display(15001, 300)],
        codex_rows=[codex(15001, flower_id=501)],
        reliquaries=[
            reliquary(
                501,
                equip_type="EQUIP_BRACER",
                icon="UI_RelicIcon_15001_4",
            ),
            reliquary(
                999,
                equip_type="EQUIP_BRACER",
                icon=None,
            ),
        ],
        materials=[
            material(104003, 400),
            material(
                105001,
                401,
                material_type="MATERIAL_RELIQUARY_MATERIAL",
                icon=None,
            ),
        ],
        full_text_map={
            "200": "Mistsplitter Reforged",
            "300": "Gladiator's Finale",
            "400": "Teachings of Freedom",
            "401": "Sanctifying Droplet",
        },
    )

    assert len(provider(tmp_path).assets()) == 6

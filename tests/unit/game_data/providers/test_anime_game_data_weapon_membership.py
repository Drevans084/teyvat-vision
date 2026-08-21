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


def write_weapon_data(
    root: Path,
    data: JsonValue,
) -> None:
    write_json(
        root,
        "ExcelBinOutput/WeaponExcelConfigData.json",
        data,
    )


def write_text_maps(
    root: Path,
    *,
    full: JsonValue,
    medium: JsonValue,
) -> None:
    write_json(
        root,
        "TextMap/TextMapEN.json",
        full,
    )
    write_json(
        root,
        "TextMap/TextMap_MediumEN.json",
        medium,
    )


def weapon(
    weapon_id: int,
    name_hash: int,
    *,
    weapon_type: str = "WEAPON_SWORD_ONE_HAND",
    rank_level: int = 3,
    icon: str = "UI_EquipIcon_Test",
) -> dict[str, JsonValue]:
    return {
        "id": weapon_id,
        "nameTextMapHash": name_hash,
        "weaponType": weapon_type,
        "rankLevel": rank_level,
        "icon": icon,
    }


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def weapon_keys(
    root: Path,
) -> tuple[str, ...]:
    return tuple(definition.identity.key for definition in provider(root).weapons())


def test_weapon_membership_requires_resolvable_english_name(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(11101, 100),
            weapon(11102, 999),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Dull Blade",
        },
        medium={},
    )

    assert weapon_keys(tmp_path) == ("11101",)


def test_weapon_membership_combines_full_and_medium_english_text_maps(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(11101, 100),
            weapon(11201, 200),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Dull Blade",
        },
        medium={
            "200": "Silver Sword",
        },
    )

    assert weapon_keys(tmp_path) == (
        "11101",
        "11201",
    )


def test_unmapped_crossbow_is_not_canonical_member(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(
                10011,
                999,
                weapon_type="WEAPON_CROSSBOW",
                rank_level=1,
                icon="UI_EquipIcon_Sword_Template",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={},
        medium={},
    )

    assert weapon_keys(tmp_path) == ()


def test_membership_filter_runs_before_weapon_type_canonicalization(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(11101, 100),
            weapon(
                10011,
                999,
                weapon_type="WEAPON_CROSSBOW",
                rank_level=1,
                icon="UI_EquipIcon_Sword_Template",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Dull Blade",
        },
        medium={},
    )

    assert weapon_keys(tmp_path) == ("11101",)


def test_weapon_membership_preserves_weapon_source_order(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(11301, 300),
            weapon(11102, 999),
            weapon(11101, 100),
            weapon(11201, 200),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Dull Blade",
            "300": "Beginner's Protector",
        },
        medium={
            "200": "Silver Sword",
        },
    )

    assert weapon_keys(tmp_path) == (
        "11301",
        "11101",
        "11201",
    )

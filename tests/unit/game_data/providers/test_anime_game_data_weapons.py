import json
from pathlib import Path

import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import Rarity, WeaponType
from teyvat_vision.game_data.localization import LocalizedName
from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider
from teyvat_vision.game_data.records import WeaponDefinition

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
    *,
    weapon_id: int = 11101,
    name_hash: int = 100,
    weapon_type: str = "WEAPON_SWORD_ONE_HAND",
    rank_level: int = 3,
) -> dict[str, JsonValue]:
    return {
        "id": weapon_id,
        "nameTextMapHash": name_hash,
        "weaponType": weapon_type,
        "rankLevel": rank_level,
        "icon": "UI_EquipIcon_Test",
    }


def load_weapon(
    root: Path,
    record: dict[str, JsonValue],
    *,
    name: str = "Dull Blade",
) -> WeaponDefinition:
    write_weapon_data(
        root,
        [record],
    )
    write_text_maps(
        root,
        full={
            str(record["nameTextMapHash"]): name,
        },
        medium={},
    )

    provider = AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )

    return provider.weapons()[0]


def test_anime_game_data_provider_loads_weapon_record(
    tmp_path: Path,
) -> None:
    definition = load_weapon(
        tmp_path,
        weapon(),
    )

    assert isinstance(definition, WeaponDefinition)


def test_weapon_uses_raw_game_id_as_canonical_key(
    tmp_path: Path,
) -> None:
    definition = load_weapon(
        tmp_path,
        weapon(weapon_id=11101),
    )

    assert definition.identity == CanonicalId(
        kind=EntityKind.WEAPON,
        key="11101",
    )


def test_weapon_preserves_resolved_english_name(
    tmp_path: Path,
) -> None:
    definition = load_weapon(
        tmp_path,
        weapon(),
        name="Dull Blade",
    )

    assert definition.names == (
        LocalizedName(
            locale="en",
            value="Dull Blade",
        ),
    )


@pytest.mark.parametrize(
    ("raw_weapon_type", "expected"),
    [
        ("WEAPON_SWORD_ONE_HAND", WeaponType.SWORD),
        ("WEAPON_CLAYMORE", WeaponType.CLAYMORE),
        ("WEAPON_POLE", WeaponType.POLEARM),
        ("WEAPON_BOW", WeaponType.BOW),
        ("WEAPON_CATALYST", WeaponType.CATALYST),
    ],
)
def test_weapon_canonicalizes_weapon_type(
    tmp_path: Path,
    raw_weapon_type: str,
    expected: WeaponType,
) -> None:
    definition = load_weapon(
        tmp_path,
        weapon(weapon_type=raw_weapon_type),
    )

    assert definition.weapon_type is expected


@pytest.mark.parametrize(
    ("rank_level", "expected"),
    [
        (1, Rarity.ONE_STAR),
        (2, Rarity.TWO_STAR),
        (3, Rarity.THREE_STAR),
        (4, Rarity.FOUR_STAR),
        (5, Rarity.FIVE_STAR),
    ],
)
def test_weapon_canonicalizes_rank_level_as_rarity(
    tmp_path: Path,
    rank_level: int,
    expected: Rarity,
) -> None:
    definition = load_weapon(
        tmp_path,
        weapon(rank_level=rank_level),
    )

    assert definition.rarity is expected

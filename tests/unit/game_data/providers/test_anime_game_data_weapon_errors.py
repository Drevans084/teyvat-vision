import json
from pathlib import Path

import pytest

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
    *,
    weapon_id: JsonValue = 11101,
    name_hash: JsonValue = 100,
    weapon_type: JsonValue = "WEAPON_SWORD_ONE_HAND",
    rank_level: JsonValue = 3,
) -> dict[str, JsonValue]:
    return {
        "id": weapon_id,
        "nameTextMapHash": name_hash,
        "weaponType": weapon_type,
        "rankLevel": rank_level,
        "icon": "UI_EquipIcon_Test",
    }


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def write_valid_text_maps(root: Path) -> None:
    write_text_maps(
        root,
        full={
            "100": "Dull Blade",
        },
        medium={},
    )


def test_weapon_table_must_be_json_array(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        {
            "id": 11101,
        },
    )

    with pytest.raises(ValueError, match="JSON array"):
        provider(tmp_path).weapons()


def test_weapon_table_must_contain_json_objects(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            "not-an-object",
        ],
    )

    with pytest.raises(ValueError, match="JSON objects"):
        provider(tmp_path).weapons()


def test_weapon_table_must_not_be_empty(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match="must not be empty"):
        provider(tmp_path).weapons()


@pytest.mark.parametrize(
    "filename",
    [
        "TextMapEN.json",
        "TextMap_MediumEN.json",
    ],
)
def test_english_text_map_must_be_json_object(
    tmp_path: Path,
    filename: str,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(),
        ],
    )
    write_valid_text_maps(tmp_path)
    write_json(
        tmp_path,
        f"TextMap/{filename}",
        [
            "not-an-object",
        ],
    )

    with pytest.raises(ValueError, match=r"TextMap.*JSON object"):
        provider(tmp_path).weapons()


def test_english_text_map_values_must_be_strings(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": 123,
        },
        medium={},
    )

    with pytest.raises(ValueError, match=r"TextMap.*values.*strings"):
        provider(tmp_path).weapons()


def test_weapon_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(weapon_id="11101"),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).weapons()


def test_weapon_boolean_id_is_not_accepted_as_integer(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(weapon_id=True),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).weapons()


def test_weapon_requires_weapon_type(
    tmp_path: Path,
) -> None:
    record = weapon()
    del record["weaponType"]

    write_weapon_data(
        tmp_path,
        [
            record,
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(
        ValueError,
        match=r"'weaponType'.*non-empty string",
    ):
        provider(tmp_path).weapons()


def test_weapon_rejects_unknown_weapon_type(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(weapon_type="WEAPON_UNKNOWN"),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(
        ValueError,
        match="unsupported AnimeGameData weapon type",
    ):
        provider(tmp_path).weapons()


def test_weapon_rank_level_must_be_integer(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(rank_level="3"),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match=r"'rankLevel'.*integer"):
        provider(tmp_path).weapons()


def test_weapon_boolean_rank_level_is_not_accepted_as_integer(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(rank_level=True),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match=r"'rankLevel'.*integer"):
        provider(tmp_path).weapons()


def test_weapon_rejects_unsupported_rank_level(
    tmp_path: Path,
) -> None:
    write_weapon_data(
        tmp_path,
        [
            weapon(rank_level=6),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(
        ValueError,
        match="unsupported AnimeGameData weapon rankLevel",
    ):
        provider(tmp_path).weapons()

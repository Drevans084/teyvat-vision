import json
from pathlib import Path

import pytest

from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider

type JsonValue = str | int | float | bool | list[JsonValue] | dict[str, JsonValue] | None


def write_avatar_data(
    root: Path,
    data: JsonValue,
) -> None:
    excel_bin = root / "ExcelBinOutput"
    excel_bin.mkdir(parents=True, exist_ok=True)

    (excel_bin / "AvatarExcelConfigData.json").write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def write_fetter_data(
    root: Path,
    avatar_ids: list[int],
) -> None:
    excel_bin = root / "ExcelBinOutput"
    excel_bin.mkdir(parents=True, exist_ok=True)

    (excel_bin / "FetterInfoExcelConfigData.json").write_text(
        json.dumps(
            [
                {
                    "avatarId": avatar_id,
                }
                for avatar_id in avatar_ids
            ]
        ),
        encoding="utf-8",
    )


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0",
    )


def test_character_table_must_be_json_array(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        {
            "id": 10000002,
        },
    )

    with pytest.raises(ValueError, match="JSON array"):
        provider(tmp_path).characters()


def test_character_table_must_contain_json_objects(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            "not-an-object",
        ],
    )

    with pytest.raises(ValueError, match="JSON objects"):
        provider(tmp_path).characters()


def test_character_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": "10000002",
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [10000002],
    )

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).characters()


def test_character_boolean_id_is_not_accepted_as_integer(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": True,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [10000002],
    )

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).characters()


def test_character_requires_weapon_type(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
                "useType": "AVATAR_FORMAL",
                "qualityType": "QUALITY_ORANGE",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [10000002],
    )

    with pytest.raises(
        ValueError,
        match=r"'weaponType'.*non-empty string",
    ):
        provider(tmp_path).characters()


def test_character_rejects_unknown_weapon_type(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_UNKNOWN",
                "qualityType": "QUALITY_ORANGE",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [10000002],
    )

    with pytest.raises(
        ValueError,
        match="unsupported AnimeGameData weapon type",
    ):
        provider(tmp_path).characters()


def test_character_rejects_unknown_rarity(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_UNKNOWN",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [10000002],
    )

    with pytest.raises(
        ValueError,
        match="unsupported AnimeGameData rarity",
    ):
        provider(tmp_path).characters()


def test_character_table_must_not_be_empty(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [],
    )

    with pytest.raises(ValueError, match="must not be empty"):
        provider(tmp_path).characters()

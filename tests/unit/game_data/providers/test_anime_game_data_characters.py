import json
from pathlib import Path

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import Rarity, WeaponType
from teyvat_vision.game_data.providers.anime_game_data import (
    AnimeGameDataProvider,
)


def write_avatar_data(
    root: Path,
    records: list[dict[str, object]],
) -> None:
    excel_bin = root / "ExcelBinOutput"
    excel_bin.mkdir(parents=True, exist_ok=True)

    (excel_bin / "AvatarExcelConfigData.json").write_text(
        json.dumps(records),
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


def test_anime_game_data_provider_loads_character_records(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
                "iconName": "UI_AvatarIcon_Ayaka",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [10000002],
    )

    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0",
    )

    characters = provider.characters()

    assert len(characters) == 1


def test_anime_game_data_character_uses_raw_game_id_as_canonical_key(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
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

    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0",
    )

    character = provider.characters()[0]

    assert character.identity == CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )


def test_anime_game_data_character_canonicalizes_weapon_type(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
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

    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0",
    )

    character = provider.characters()[0]

    assert character.weapon_type is WeaponType.SWORD


def test_anime_game_data_character_canonicalizes_rarity(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
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

    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0",
    )

    character = provider.characters()[0]

    assert character.rarity is Rarity.FIVE_STAR


def test_anime_game_data_character_preserves_source_order(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            {
                "id": 10000002,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
            },
            {
                "id": 10000003,
                "useType": "AVATAR_FORMAL",
                "weaponType": "WEAPON_SWORD_ONE_HAND",
                "qualityType": "QUALITY_ORANGE",
            },
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            10000002,
            10000003,
        ],
    )

    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0",
    )

    characters = provider.characters()

    assert tuple(character.identity.key for character in characters) == (
        "10000002",
        "10000003",
    )

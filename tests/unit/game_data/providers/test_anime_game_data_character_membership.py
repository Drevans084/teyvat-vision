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


def write_avatar_data(
    root: Path,
    data: JsonValue,
) -> None:
    write_json(
        root,
        "ExcelBinOutput/AvatarExcelConfigData.json",
        data,
    )


def write_fetter_data(
    root: Path,
    data: JsonValue,
) -> None:
    write_json(
        root,
        "ExcelBinOutput/FetterInfoExcelConfigData.json",
        data,
    )


def character(
    character_id: int,
    *,
    use_type: str = "AVATAR_FORMAL",
    weapon_type: str = "WEAPON_SWORD_ONE_HAND",
    quality_type: str = "QUALITY_ORANGE",
    icon_name: str = "UI_AvatarIcon_Test",
) -> dict[str, JsonValue]:
    return {
        "id": character_id,
        "useType": use_type,
        "weaponType": weapon_type,
        "qualityType": quality_type,
        "iconName": icon_name,
    }


def fetter(
    character_id: int,
) -> dict[str, JsonValue]:
    return {
        "avatarId": character_id,
    }


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def character_keys(
    root: Path,
) -> tuple[str, ...]:
    return tuple(definition.identity.key for definition in provider(root).characters())


def test_character_membership_requires_formal_avatar_with_matching_fetter_info(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            character(10000002),
            character(
                10000003,
                use_type="AVATAR_ABANDON",
            ),
            character(10000004),
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            fetter(10000002),
            fetter(10000003),
        ],
    )

    assert character_keys(tmp_path) == ("10000002",)


def test_membership_filter_runs_before_weapon_type_canonicalization(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            character(10000002),
            character(
                10000134,
                weapon_type="WEAPON_CROSSBOW",
                icon_name="UI_AvatarIcon_PlayerBoy",
            ),
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            fetter(10000002),
        ],
    )

    assert character_keys(tmp_path) == ("10000002",)


def test_both_travelers_remain_in_canonical_membership(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            character(
                10000005,
                icon_name="UI_AvatarIcon_PlayerBoy",
            ),
            character(
                10000007,
                icon_name="UI_AvatarIcon_PlayerGirl",
            ),
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            fetter(10000005),
            fetter(10000007),
        ],
    )

    assert character_keys(tmp_path) == (
        "10000005",
        "10000007",
    )


def test_both_mannequins_remain_in_canonical_membership(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            character(
                10000117,
                icon_name="UI_AvatarIcon_MannequinBoy",
            ),
            character(
                10000118,
                icon_name="UI_AvatarIcon_MannequinGirl",
            ),
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            fetter(10000117),
            fetter(10000118),
        ],
    )

    assert character_keys(tmp_path) == (
        "10000117",
        "10000118",
    )


def test_source_duplicate_without_fetter_is_not_canonical_member(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            character(
                10000116,
                weapon_type="WEAPON_POLE",
                icon_name="UI_AvatarIcon_Ineffa",
            ),
            character(
                10000903,
                weapon_type="WEAPON_POLE",
                icon_name="UI_AvatarIcon_Ineffa",
            ),
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            fetter(10000116),
        ],
    )

    assert character_keys(tmp_path) == ("10000116",)


def test_character_membership_preserves_avatar_source_order(
    tmp_path: Path,
) -> None:
    write_avatar_data(
        tmp_path,
        [
            character(10000003),
            character(
                10000901,
                use_type="AVATAR_FORMAL",
            ),
            character(
                10000004,
                use_type="AVATAR_ABANDON",
            ),
            character(10000002),
        ],
    )
    write_fetter_data(
        tmp_path,
        [
            fetter(10000003),
            fetter(10000004),
            fetter(10000002),
        ],
    )

    assert character_keys(tmp_path) == (
        "10000003",
        "10000002",
    )

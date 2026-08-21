import json
from pathlib import Path

import pytest

from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider

type JsonValue = str | int | float | bool | list[JsonValue] | dict[str, JsonValue] | None

_APPROVED_CATEGORIES = (
    "MATERIAL_AVATAR_MATERIAL",
    "MATERIAL_EXCHANGE",
    "MATERIAL_EXP_FRUIT",
    "MATERIAL_FISH_BAIT",
    "MATERIAL_WEAPON_EXP_STONE",
    "MATERIAL_WOOD",
)


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


def write_material_data(
    root: Path,
    data: JsonValue,
) -> None:
    write_json(
        root,
        "ExcelBinOutput/MaterialExcelConfigData.json",
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


def material(
    material_id: JsonValue,
    name_hash: JsonValue,
    *,
    material_type: JsonValue,
    icon: str = "UI_ItemIcon_Test",
) -> dict[str, JsonValue]:
    return {
        "id": material_id,
        "nameTextMapHash": name_hash,
        "materialType": material_type,
        "itemType": "ITEM_MATERIAL",
        "icon": icon,
    }


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def material_keys(
    root: Path,
) -> tuple[str, ...]:
    return tuple(definition.identity.key for definition in provider(root).materials())


@pytest.mark.parametrize(
    "material_type",
    _APPROVED_CATEGORIES,
)
def test_each_inventory_kamera_material_category_is_canonical_member(
    tmp_path: Path,
    material_type: str,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                104001,
                100,
                material_type=material_type,
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Test Material",
        },
        medium={},
    )

    assert material_keys(tmp_path) == ("104001",)


def test_material_membership_requires_resolvable_english_name(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                104001,
                100,
                material_type="MATERIAL_AVATAR_MATERIAL",
            ),
            material(
                101306,
                999,
                material_type="MATERIAL_WOOD",
                icon="UI_ItemIcon_101306",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Test Material",
        },
        medium={},
    )

    assert material_keys(tmp_path) == ("104001",)


def test_material_membership_combines_full_and_medium_english_text_maps(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                104001,
                100,
                material_type="MATERIAL_AVATAR_MATERIAL",
            ),
            material(
                104002,
                200,
                material_type="MATERIAL_EXCHANGE",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "First Material",
        },
        medium={
            "200": "Second Material",
        },
    )

    assert material_keys(tmp_path) == (
        "104001",
        "104002",
    )


def test_material_outside_approved_categories_is_not_canonical_member(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                105001,
                100,
                material_type="MATERIAL_RELIQUARY_MATERIAL",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Sanctifying Droplet",
        },
        medium={},
    )

    assert material_keys(tmp_path) == ()


def test_unmapped_approved_material_is_not_canonical_member(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                101306,
                999,
                material_type="MATERIAL_WOOD",
                icon="UI_ItemIcon_101306",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={},
        medium={},
    )

    assert material_keys(tmp_path) == ()


def test_membership_filter_runs_before_material_id_canonicalization(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                104001,
                100,
                material_type="MATERIAL_AVATAR_MATERIAL",
            ),
            material(
                "not-an-integer",
                200,
                material_type="MATERIAL_QUEST",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "Test Material",
            "200": "Quest Material",
        },
        medium={},
    )

    assert material_keys(tmp_path) == ("104001",)


def test_material_membership_preserves_material_source_order(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                104003,
                300,
                material_type="MATERIAL_EXP_FRUIT",
            ),
            material(
                105001,
                400,
                material_type="MATERIAL_RELIQUARY_MATERIAL",
            ),
            material(
                104001,
                100,
                material_type="MATERIAL_AVATAR_MATERIAL",
            ),
            material(
                104002,
                200,
                material_type="MATERIAL_EXCHANGE",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "100": "First Material",
            "300": "Third Material",
            "400": "Outside Scope",
        },
        medium={
            "200": "Second Material",
        },
    )

    assert material_keys(tmp_path) == (
        "104003",
        "104001",
        "104002",
    )

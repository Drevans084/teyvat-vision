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
    *,
    material_id: JsonValue = 104003,
    name_hash: JsonValue = 100,
    material_type: JsonValue = "MATERIAL_AVATAR_MATERIAL",
) -> dict[str, JsonValue]:
    return {
        "id": material_id,
        "nameTextMapHash": name_hash,
        "materialType": material_type,
        "icon": "UI_ItemIcon_Test",
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
            "100": "Guide to Freedom",
        },
        medium={},
    )


def test_material_table_must_be_json_array(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        {
            "id": 104003,
        },
    )

    with pytest.raises(ValueError, match="JSON array"):
        provider(tmp_path).materials()


def test_material_table_must_contain_json_objects(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            "not-an-object",
        ],
    )

    with pytest.raises(ValueError, match="JSON objects"):
        provider(tmp_path).materials()


def test_material_table_must_not_be_empty(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match="must not be empty"):
        provider(tmp_path).materials()


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
    write_material_data(
        tmp_path,
        [
            material(),
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
        provider(tmp_path).materials()


def test_english_text_map_values_must_be_strings(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(),
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
        provider(tmp_path).materials()


def test_material_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(material_id="104003"),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).materials()


def test_material_boolean_id_is_not_accepted_as_integer(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(material_id=True),
        ],
    )
    write_valid_text_maps(tmp_path)

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).materials()

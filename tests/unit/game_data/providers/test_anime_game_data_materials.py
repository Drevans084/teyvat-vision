import json
from pathlib import Path

from teyvat_vision.game_data.localization import LocalizedName
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
    full: JsonValue | None = None,
    medium: JsonValue | None = None,
) -> None:
    write_json(
        root,
        "TextMap/TextMapEN.json",
        {} if full is None else full,
    )
    write_json(
        root,
        "TextMap/TextMap_MediumEN.json",
        {} if medium is None else medium,
    )


def material(
    material_id: int,
    *,
    name_hash: int,
    material_type: str = "MATERIAL_AVATAR_MATERIAL",
) -> dict[str, JsonValue]:
    return {
        "id": material_id,
        "materialType": material_type,
        "nameTextMapHash": name_hash,
    }


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


def test_material_preserves_resolved_english_name(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                104003,
                name_hash=111111111,
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        full={
            "111111111": "Guide to Freedom",
        },
    )

    definition = provider(tmp_path).materials()[0]

    assert definition.names == (
        LocalizedName(
            locale="en",
            value="Guide to Freedom",
        ),
    )


def test_material_resolves_name_from_medium_english_text_map(
    tmp_path: Path,
) -> None:
    write_material_data(
        tmp_path,
        [
            material(
                101001,
                name_hash=222222222,
                material_type="MATERIAL_EXCHANGE",
            ),
        ],
    )
    write_text_maps(
        tmp_path,
        medium={
            "222222222": "Iron Chunk",
        },
    )

    definition = provider(tmp_path).materials()[0]

    assert definition.names == (
        LocalizedName(
            locale="en",
            value="Iron Chunk",
        ),
    )

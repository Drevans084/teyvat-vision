import json
from pathlib import Path

import pytest

from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider

type JsonValue = str | int | float | bool | list[JsonValue] | dict[str, JsonValue] | None

_TABLE_PATHS = (
    "ExcelBinOutput/DisplayItemExcelConfigData.json",
    "ExcelBinOutput/ReliquaryCodexExcelConfigData.json",
    "ExcelBinOutput/ReliquaryExcelConfigData.json",
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


def display(
    *,
    suit_id: JsonValue = 15001,
) -> dict[str, JsonValue]:
    return {
        "param": suit_id,
        "nameTextMapHash": 100,
        "icon": "UI_RelicIcon_Test",
    }


def codex(
    *,
    suit_id: JsonValue = 15001,
    flower_id: JsonValue = 501,
) -> dict[str, JsonValue]:
    return {
        "suitId": suit_id,
        "flowerId": flower_id,
        "leatherId": 0,
        "sandId": 0,
        "cupId": 0,
        "capId": 0,
    }


def reliquary(
    *,
    piece_id: JsonValue = 501,
    rank_level: JsonValue = 5,
) -> dict[str, JsonValue]:
    return {
        "id": piece_id,
        "equipType": "EQUIP_BRACER",
        "rankLevel": rank_level,
    }


def write_valid_source(root: Path) -> None:
    write_json(
        root,
        _TABLE_PATHS[0],
        [
            display(),
        ],
    )
    write_json(
        root,
        _TABLE_PATHS[1],
        [
            codex(),
        ],
    )
    write_json(
        root,
        _TABLE_PATHS[2],
        [
            reliquary(),
        ],
    )
    write_json(
        root,
        "TextMap/TextMapEN.json",
        {
            "100": "Gladiator's Finale",
        },
    )
    write_json(
        root,
        "TextMap/TextMap_MediumEN.json",
        {},
    )


def provider(root: Path) -> AnimeGameDataProvider:
    return AnimeGameDataProvider(
        root=root,
        game_version="7.0.0",
    )


@pytest.mark.parametrize(
    "relative_path",
    _TABLE_PATHS,
)
def test_artifact_source_table_must_be_json_array(
    tmp_path: Path,
    relative_path: str,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        relative_path,
        {
            "not": "an array",
        },
    )

    with pytest.raises(ValueError, match="JSON array"):
        provider(tmp_path).artifact_sets()


@pytest.mark.parametrize(
    "relative_path",
    _TABLE_PATHS,
)
def test_artifact_source_table_must_contain_json_objects(
    tmp_path: Path,
    relative_path: str,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        relative_path,
        [
            "not-an-object",
        ],
    )

    with pytest.raises(ValueError, match="JSON objects"):
        provider(tmp_path).artifact_sets()


@pytest.mark.parametrize(
    "relative_path",
    _TABLE_PATHS,
)
def test_artifact_source_table_must_not_be_empty(
    tmp_path: Path,
    relative_path: str,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        relative_path,
        [],
    )

    with pytest.raises(ValueError, match="must not be empty"):
        provider(tmp_path).artifact_sets()


def test_relic_display_suit_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[0],
        [
            display(suit_id="15001"),
        ],
    )

    with pytest.raises(ValueError, match=r"'param'.*integer"):
        provider(tmp_path).artifact_sets()


def test_relic_display_boolean_suit_id_is_not_accepted_as_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[0],
        [
            display(suit_id=True),
        ],
    )

    with pytest.raises(ValueError, match=r"'param'.*integer"):
        provider(tmp_path).artifact_sets()


def test_codex_suit_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[1],
        [
            codex(suit_id="15001"),
        ],
    )

    with pytest.raises(ValueError, match=r"'suitId'.*integer"):
        provider(tmp_path).artifact_sets()


def test_codex_piece_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[1],
        [
            codex(flower_id="501"),
        ],
    )

    with pytest.raises(ValueError, match=r"'flowerId'.*integer"):
        provider(tmp_path).artifact_sets()


def test_reliquary_piece_id_must_be_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[2],
        [
            reliquary(piece_id="501"),
        ],
    )

    with pytest.raises(ValueError, match=r"'id'.*integer"):
        provider(tmp_path).artifact_sets()


def test_reliquary_rank_level_must_be_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[2],
        [
            reliquary(rank_level="5"),
        ],
    )

    with pytest.raises(ValueError, match=r"'rankLevel'.*integer"):
        provider(tmp_path).artifact_sets()


def test_reliquary_boolean_rank_level_is_not_accepted_as_integer(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[2],
        [
            reliquary(rank_level=True),
        ],
    )

    with pytest.raises(ValueError, match=r"'rankLevel'.*integer"):
        provider(tmp_path).artifact_sets()


def test_reliquary_rejects_unsupported_rank_level(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[2],
        [
            reliquary(rank_level=6),
        ],
    )

    with pytest.raises(
        ValueError,
        match="unsupported AnimeGameData artifact rankLevel",
    ):
        provider(tmp_path).artifact_sets()


def test_codex_reference_to_missing_reliquary_piece_is_rejected(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[2],
        [
            reliquary(piece_id=999),
        ],
    )

    with pytest.raises(
        ValueError,
        match="missing reliquary piece",
    ):
        provider(tmp_path).artifact_sets()


def test_duplicate_reliquary_piece_id_is_rejected(
    tmp_path: Path,
) -> None:
    write_valid_source(tmp_path)
    write_json(
        tmp_path,
        _TABLE_PATHS[2],
        [
            reliquary(piece_id=501),
            reliquary(piece_id=501),
        ],
    )

    with pytest.raises(
        ValueError,
        match="duplicate reliquary id",
    ):
        provider(tmp_path).artifact_sets()

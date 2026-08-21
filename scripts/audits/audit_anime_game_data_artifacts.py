from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import cast

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]

_CODEX_SLOT_FIELDS = {
    "flowerId": "EQUIP_BRACER",
    "leatherId": "EQUIP_NECKLACE",
    "sandId": "EQUIP_SHOES",
    "cupId": "EQUIP_RING",
    "capId": "EQUIP_DRESS",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit AnimeGameData2 artifact-set relationships against "
            "Inventory Kamera-compatible membership."
        ),
    )
    parser.add_argument(
        "dataset_root",
        type=Path,
        help="Path to the root of an AnimeGameData2 dataset checkout.",
    )
    return parser.parse_args()


def load_json(path: Path) -> JsonValue:
    with path.open(encoding="utf-8") as file:
        return cast(JsonValue, json.load(file))


def require_array(
    value: JsonValue,
    *,
    path: Path,
) -> list[JsonValue]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must contain a JSON array")

    return value


def require_object(
    value: JsonValue,
    *,
    context: str,
) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise TypeError(f"{context} must be a JSON object")

    return value


def require_integer(
    value: JsonValue | None,
    *,
    context: str,
) -> int:
    if type(value) is not int:
        raise TypeError(f"{context} must be an integer")

    return value


def load_records(path: Path) -> list[dict[str, JsonValue]]:
    return [
        require_object(value, context=f"{path.name} row")
        for value in require_array(load_json(path), path=path)
    ]


def load_text_map(dataset_root: Path) -> dict[str, str]:
    text_map: dict[str, str] = {}

    for filename in (
        "TextMapEN.json",
        "TextMap_MediumEN.json",
    ):
        path = dataset_root / "TextMap" / filename
        raw = require_object(
            load_json(path),
            context=str(path),
        )

        for key, value in raw.items():
            if isinstance(value, str) and value.strip():
                text_map[key] = value

    return text_map


def resolve_hash(
    value: JsonValue | None,
    text_map: dict[str, str],
) -> str | None:
    return text_map.get(str(value))


def main() -> None:
    arguments = parse_arguments()
    dataset_root = arguments.dataset_root.resolve()
    excel_root = dataset_root / "ExcelBinOutput"

    display_path = excel_root / "DisplayItemExcelConfigData.json"
    codex_path = excel_root / "ReliquaryCodexExcelConfigData.json"
    reliquary_path = excel_root / "ReliquaryExcelConfigData.json"

    display_rows = load_records(display_path)
    codex_rows = load_records(codex_path)
    reliquary_rows = load_records(reliquary_path)
    text_map = load_text_map(dataset_root)

    relic_display_rows = [
        row
        for row in display_rows
        if isinstance(row.get("icon"), str) and "RelicIcon" in cast(str, row["icon"])
    ]

    display_rows_by_suit: dict[
        int,
        list[dict[str, JsonValue]],
    ] = defaultdict(list)

    for row in relic_display_rows:
        suit_id = require_integer(
            row.get("param"),
            context="RelicIcon display param",
        )
        display_rows_by_suit[suit_id].append(row)

    codex_rows_by_suit: dict[
        int,
        list[dict[str, JsonValue]],
    ] = defaultdict(list)

    for row in codex_rows:
        suit_id = require_integer(
            row.get("suitId"),
            context="reliquary codex suitId",
        )
        codex_rows_by_suit[suit_id].append(row)

    reliquary_rows_by_id: dict[int, dict[str, JsonValue]] = {}

    for row in reliquary_rows:
        reliquary_id = require_integer(
            row.get("id"),
            context="reliquary id",
        )

        if reliquary_id in reliquary_rows_by_id:
            raise ValueError(f"duplicate reliquary id: {reliquary_id}")

        reliquary_rows_by_id[reliquary_id] = row

    display_suit_ids = set(display_rows_by_suit)
    codex_suit_ids = set(codex_rows_by_suit)

    display_only_suit_ids = sorted(display_suit_ids - codex_suit_ids)
    codex_only_suit_ids = sorted(codex_suit_ids - display_suit_ids)
    shared_suit_ids = sorted(display_suit_ids & codex_suit_ids)

    missing_piece_ids: set[int] = set()
    slot_profiles: Counter[tuple[str, ...]] = Counter()
    incomplete_sets: list[dict[str, JsonValue]] = []
    suit_names: dict[int, tuple[str, ...]] = {}

    for suit_id in sorted(display_suit_ids):
        names = {
            name
            for row in display_rows_by_suit[suit_id]
            if (
                name := resolve_hash(
                    row.get("nameTextMapHash"),
                    text_map,
                )
            )
            is not None
        }
        suit_names[suit_id] = tuple(sorted(names))

    for suit_id in shared_suit_ids:
        piece_ids_by_slot: dict[str, set[int]] = defaultdict(set)

        for codex_row in codex_rows_by_suit[suit_id]:
            for field, expected_slot in _CODEX_SLOT_FIELDS.items():
                raw_piece_id = codex_row.get(field)

                if raw_piece_id in (None, 0):
                    continue

                piece_id = require_integer(
                    raw_piece_id,
                    context=f"codex {field}",
                )
                piece_ids_by_slot[expected_slot].add(piece_id)

                if piece_id not in reliquary_rows_by_id:
                    missing_piece_ids.add(piece_id)

        present_slots = tuple(
            slot for slot in _CODEX_SLOT_FIELDS.values() if piece_ids_by_slot.get(slot)
        )
        slot_profiles[present_slots] += 1

        if len(present_slots) < len(_CODEX_SLOT_FIELDS):
            incomplete_sets.append(
                {
                    "suitId": suit_id,
                    "names": list(suit_names[suit_id]),
                    "slots": list(present_slots),
                    "codexRowCount": len(codex_rows_by_suit[suit_id]),
                }
            )

    name_to_suit_ids: dict[str, set[int]] = defaultdict(set)

    for suit_id, names in suit_names.items():
        for name in names:
            name_to_suit_ids[name].add(suit_id)

    duplicate_names = {
        name: sorted(suit_ids) for name, suit_ids in name_to_suit_ids.items() if len(suit_ids) > 1
    }

    inventory_kamera_suit_ids = [
        suit_id
        for suit_id in shared_suit_ids
        if any(
            codex_row.get(field) not in (None, 0)
            for codex_row in codex_rows_by_suit[suit_id]
            for field in _CODEX_SLOT_FIELDS
        )
    ]

    print(f"DisplayItem rows: {len(display_rows)}")
    print(f"RelicIcon display rows: {len(relic_display_rows)}")
    print(f"Unique RelicIcon display suit IDs: {len(display_suit_ids)}")
    print(f"ReliquaryCodex rows: {len(codex_rows)}")
    print(f"Unique codex suit IDs: {len(codex_suit_ids)}")
    print(f"Reliquary rows: {len(reliquary_rows)}")
    print(f"Inventory Kamera-compatible suit IDs: {len(inventory_kamera_suit_ids)}")
    print(f"Missing codex piece IDs: {sorted(missing_piece_ids)}")
    print(f"Duplicate localized set names: {duplicate_names}")
    print()

    print(f"Display-only suit IDs: {len(display_only_suit_ids)}")

    for suit_id in display_only_suit_ids:
        print(
            json.dumps(
                {
                    "suitId": suit_id,
                    "names": list(suit_names[suit_id]),
                    "displayRowCount": len(display_rows_by_suit[suit_id]),
                    "icons": sorted(
                        {
                            cast(str, row["icon"])
                            for row in display_rows_by_suit[suit_id]
                            if isinstance(row.get("icon"), str)
                        }
                    ),
                },
                sort_keys=True,
            )
        )

    print()
    print(f"Codex-only suit IDs: {codex_only_suit_ids}")
    print()

    print("Artifact slot profiles:")

    for slots, count in sorted(slot_profiles.items()):
        print(
            json.dumps(
                {
                    "slots": list(slots),
                    "setCount": count,
                },
                sort_keys=True,
            )
        )

    print()
    print(f"Incomplete artifact sets: {len(incomplete_sets)}")

    for result in incomplete_sets:
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

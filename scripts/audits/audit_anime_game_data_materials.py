from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import cast

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]

_INVENTORY_KAMERA_CATEGORIES = {
    "MATERIAL_AVATAR_MATERIAL",
    "MATERIAL_EXCHANGE",
    "MATERIAL_EXP_FRUIT",
    "MATERIAL_FISH_BAIT",
    "MATERIAL_WEAPON_EXP_STONE",
    "MATERIAL_WOOD",
}

_MISSING_CATEGORY = "<missing>"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare AnimeGameData2 material coverage with Inventory "
            "Kamera's proven six-category scope."
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


def material_category(row: dict[str, JsonValue]) -> str:
    value = row.get("materialType")

    if not isinstance(value, str) or not value:
        return _MISSING_CATEGORY

    return value


def resolved_name(
    row: dict[str, JsonValue],
    text_map: dict[str, str],
) -> str | None:
    return text_map.get(str(row.get("nameTextMapHash")))


def inventory_kamera_key(name: str) -> str:
    return re.sub(r"\W", "", name.title()).lower()


def summarize_row(
    row: dict[str, JsonValue],
    *,
    name: str | None,
) -> dict[str, JsonValue]:
    return {
        "id": row.get("id"),
        "name": name,
        "materialType": row.get("materialType"),
        "itemType": row.get("itemType"),
        "icon": row.get("icon"),
        "rankLevel": row.get("rankLevel"),
        "nameTextMapHash": row.get("nameTextMapHash"),
    }


def main() -> None:
    arguments = parse_arguments()
    dataset_root = arguments.dataset_root.resolve()
    material_path = dataset_root / "ExcelBinOutput" / "MaterialExcelConfigData.json"

    material_rows = load_records(material_path)
    text_map = load_text_map(dataset_root)

    material_ids = [require_integer(row.get("id"), context="material id") for row in material_rows]
    duplicate_ids = sorted(
        material_id for material_id in set(material_ids) if material_ids.count(material_id) > 1
    )

    rows_by_category: dict[
        str,
        list[dict[str, JsonValue]],
    ] = defaultdict(list)

    for row in material_rows:
        rows_by_category[material_category(row)].append(row)

    inventory_kamera_rows = [
        row for row in material_rows if material_category(row) in _INVENTORY_KAMERA_CATEGORIES
    ]
    inventory_kamera_mapped_rows = [
        row for row in inventory_kamera_rows if resolved_name(row, text_map) is not None
    ]
    inventory_kamera_unmapped_rows = [
        row for row in inventory_kamera_rows if resolved_name(row, text_map) is None
    ]

    inventory_kamera_keys: dict[
        str,
        list[dict[str, JsonValue]],
    ] = defaultdict(list)

    for row in inventory_kamera_mapped_rows:
        name = resolved_name(row, text_map)

        if name is None:
            raise AssertionError("mapped material row must have a name")

        inventory_kamera_keys[inventory_kamera_key(name)].append(row)

    duplicate_inventory_kamera_keys = {
        key: rows for key, rows in inventory_kamera_keys.items() if len(rows) > 1
    }

    print(f"Raw material rows: {len(material_rows)}")
    print(f"Unique material IDs: {len(set(material_ids))}")
    print(f"Duplicate material IDs: {duplicate_ids}")
    print(f"Material category count: {len(rows_by_category)}")
    print(f"Inventory Kamera category rows: {len(inventory_kamera_rows)}")
    print(f"Inventory Kamera name-resolvable rows: {len(inventory_kamera_mapped_rows)}")
    print(f"Inventory Kamera name-unmapped rows: {len(inventory_kamera_unmapped_rows)}")
    print(f"Inventory Kamera unique normalized keys: {len(inventory_kamera_keys)}")
    print(f"Inventory Kamera duplicate normalized keys: {len(duplicate_inventory_kamera_keys)}")
    print()

    print("Inventory Kamera category summary:")

    for category in sorted(_INVENTORY_KAMERA_CATEGORIES):
        rows = rows_by_category.get(category, [])
        mapped_count = sum(resolved_name(row, text_map) is not None for row in rows)

        print(
            json.dumps(
                {
                    "materialType": category,
                    "rows": len(rows),
                    "nameResolvable": mapped_count,
                    "nameUnmapped": len(rows) - mapped_count,
                    "itemTypes": dict(
                        sorted(Counter(str(row.get("itemType")) for row in rows).items())
                    ),
                },
                sort_keys=True,
            )
        )

    print()
    print(f"Inventory Kamera unmapped rows: {len(inventory_kamera_unmapped_rows)}")

    for row in inventory_kamera_unmapped_rows:
        print(
            json.dumps(
                summarize_row(
                    row,
                    name=None,
                ),
                sort_keys=True,
            )
        )

    print()
    print(
        f"Inventory Kamera duplicate normalized-key groups: {len(duplicate_inventory_kamera_keys)}"
    )

    for key, rows in sorted(duplicate_inventory_kamera_keys.items()):
        print(f"{key}:")

        for row in rows:
            print(
                json.dumps(
                    summarize_row(
                        row,
                        name=resolved_name(row, text_map),
                    ),
                    sort_keys=True,
                )
            )

    outside_categories = sorted(
        category for category in rows_by_category if category not in _INVENTORY_KAMERA_CATEGORIES
    )

    print()
    print(f"Outside-baseline categories: {len(outside_categories)}")

    for category in outside_categories:
        rows = rows_by_category[category]
        mapped_rows = [row for row in rows if resolved_name(row, text_map) is not None]
        samples = [
            summarize_row(
                row,
                name=resolved_name(row, text_map),
            )
            for row in mapped_rows[:5]
        ]

        print(
            json.dumps(
                {
                    "materialType": category,
                    "rows": len(rows),
                    "nameResolvable": len(mapped_rows),
                    "nameUnmapped": len(rows) - len(mapped_rows),
                    "itemTypes": dict(
                        sorted(Counter(str(row.get("itemType")) for row in rows).items())
                    ),
                    "samples": samples,
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()

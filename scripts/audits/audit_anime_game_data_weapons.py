from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Inventory Kamera-compatible AnimeGameData2 weapon "
            "membership with weapon codex membership."
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


def require_object(
    value: JsonValue,
    *,
    context: str,
) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise TypeError(f"{context} must be a JSON object")

    return value


def require_array(
    value: JsonValue,
    *,
    path: Path,
) -> list[JsonValue]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must contain a JSON array")

    return value


def require_integer(
    value: JsonValue | None,
    *,
    context: str,
) -> int:
    if type(value) is not int:
        raise TypeError(f"{context} must be an integer")

    return value


def resolve_name(
    row: dict[str, JsonValue],
    text_map: dict[str, JsonValue],
) -> str | None:
    name_hash = row.get("nameTextMapHash")
    value = text_map.get(str(name_hash))

    if not isinstance(value, str) or not value.strip():
        return None

    return value


def summarize_weapon(
    row: dict[str, JsonValue],
    *,
    name: str | None,
) -> dict[str, JsonValue]:
    return {
        "id": row.get("id"),
        "name": name,
        "weaponType": row.get("weaponType"),
        "rankLevel": row.get("rankLevel"),
        "icon": row.get("icon"),
        "skillAffix": row.get("skillAffix"),
        "storyId": row.get("storyId"),
    }


def print_group(
    title: str,
    rows: list[dict[str, JsonValue]],
    *,
    text_map: dict[str, JsonValue],
) -> None:
    print(f"{title}: {len(rows)}")

    for row in rows:
        print(
            json.dumps(
                summarize_weapon(
                    row,
                    name=resolve_name(row, text_map),
                ),
                sort_keys=True,
            )
        )

    print()


def main() -> None:
    arguments = parse_arguments()
    dataset_root = arguments.dataset_root.resolve()
    excel_root = dataset_root / "ExcelBinOutput"

    weapon_path = excel_root / "WeaponExcelConfigData.json"
    codex_path = excel_root / "WeaponCodexExcelConfigData.json"
    text_map_paths = (
        dataset_root / "TextMap" / "TextMapEN.json",
        dataset_root / "TextMap" / "TextMap_MediumEN.json",
    )

    text_map: dict[str, JsonValue] = {}

    for path in text_map_paths:
        text_map.update(
            require_object(
                load_json(path),
                context=str(path),
            )
        )

    weapon_values = require_array(
        load_json(weapon_path),
        path=weapon_path,
    )
    codex_values = require_array(
        load_json(codex_path),
        path=codex_path,
    )

    weapon_rows = [require_object(value, context="weapon row") for value in weapon_values]
    codex_rows = [require_object(value, context="weapon codex row") for value in codex_values]

    weapon_ids = [require_integer(row.get("id"), context="weapon id") for row in weapon_rows]
    codex_weapon_ids = [
        require_integer(
            row.get("weaponId"),
            context="weapon codex weaponId",
        )
        for row in codex_rows
    ]

    duplicate_weapon_ids = sorted(
        weapon_id for weapon_id in set(weapon_ids) if weapon_ids.count(weapon_id) > 1
    )
    duplicate_codex_weapon_ids = sorted(
        weapon_id for weapon_id in set(codex_weapon_ids) if codex_weapon_ids.count(weapon_id) > 1
    )

    weapon_id_set = set(weapon_ids)
    codex_weapon_id_set = set(codex_weapon_ids)
    codex_without_weapon = sorted(codex_weapon_id_set - weapon_id_set)

    baseline_and_codex: list[dict[str, JsonValue]] = []
    baseline_only: list[dict[str, JsonValue]] = []
    codex_without_name: list[dict[str, JsonValue]] = []
    neither_baseline_nor_codex: list[dict[str, JsonValue]] = []

    for weapon_id, row in zip(weapon_ids, weapon_rows, strict=True):
        in_inventory_kamera_baseline = resolve_name(row, text_map) is not None
        in_codex = weapon_id in codex_weapon_id_set

        if in_inventory_kamera_baseline and in_codex:
            baseline_and_codex.append(row)
        elif in_inventory_kamera_baseline:
            baseline_only.append(row)
        elif in_codex:
            codex_without_name.append(row)
        else:
            neither_baseline_nor_codex.append(row)

    baseline_count = len(baseline_and_codex) + len(baseline_only)
    unmapped_count = len(codex_without_name) + len(neither_baseline_nor_codex)

    print(f"Raw weapon rows: {len(weapon_rows)}")
    print(f"Inventory Kamera baseline rows: {baseline_count}")
    print(f"Name-unmapped rows: {unmapped_count}")
    print(f"Weapon codex rows: {len(codex_rows)}")
    print(f"Unique weapon IDs: {len(weapon_id_set)}")
    print(f"Unique codex weapon IDs: {len(codex_weapon_id_set)}")
    print(f"Duplicate weapon IDs: {duplicate_weapon_ids}")
    print(f"Duplicate codex weapon IDs: {duplicate_codex_weapon_ids}")
    print(f"Codex IDs without weapon rows: {codex_without_weapon}")
    print()

    print(f"Inventory Kamera baseline + codex: {len(baseline_and_codex)}")
    print()

    print_group(
        "Inventory Kamera baseline only",
        baseline_only,
        text_map=text_map,
    )
    print_group(
        "Codex only, without resolvable name",
        codex_without_name,
        text_map=text_map,
    )
    print_group(
        "Neither baseline nor codex",
        neither_baseline_nor_codex,
        text_map=text_map,
    )


if __name__ == "__main__":
    main()

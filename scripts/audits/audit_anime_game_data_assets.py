from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import cast

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type Subject = tuple[str, int]

_MATERIAL_TYPES = frozenset(
    {
        "MATERIAL_AVATAR_MATERIAL",
        "MATERIAL_EXCHANGE",
        "MATERIAL_EXP_FRUIT",
        "MATERIAL_FISH_BAIT",
        "MATERIAL_WEAPON_EXP_STONE",
        "MATERIAL_WOOD",
    }
)

_CODEX_ASSET_ROLES = {
    "flowerId": "artifact_flower",
    "leatherId": "artifact_plume",
    "sandId": "artifact_sands",
    "cupId": "artifact_goblet",
    "capId": "artifact_circlet",
}

_KIND_ORDER = (
    "character",
    "weapon",
    "artifact_set",
    "material",
)


@dataclass(frozen=True, slots=True)
class AssetCandidate:
    """One symbolic asset reference associated with a canonical subject."""

    subject_kind: str
    subject_id: int
    role: str
    reference: str

    @property
    def subject(self) -> Subject:
        return (
            self.subject_kind,
            self.subject_id,
        )


@dataclass(frozen=True, slots=True)
class InvalidReference:
    """One expected asset field whose value cannot become a reference."""

    subject_kind: str
    subject_id: int
    role: str
    value: JsonValue | None


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    """Result of resolving one symbolic reference through an asset origin."""

    reference: str
    url: str
    status: int | None
    content_type: str | None
    content_length: str | None
    error: str | None

    @property
    def is_image(self) -> bool:
        return (
            self.status == 200
            and self.content_type is not None
            and self.content_type.startswith("image/")
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit AnimeGameData2 symbolic asset references for canonical Teyvat Vision entities."
        ),
    )
    parser.add_argument(
        "dataset_root",
        type=Path,
        help="Path to the root of an AnimeGameData2 dataset checkout.",
    )
    parser.add_argument(
        "--check-enka",
        action="store_true",
        help=(
            "Resolve unique references through Enka sequentially. "
            "Omit this flag for a local-only audit."
        ),
    )
    parser.add_argument(
        "--resolve-limit",
        type=int,
        default=None,
        help="Maximum number of unique references to resolve.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay in seconds between remote requests. Default: 0.1.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Timeout in seconds for each remote request. Default: 15.",
    )
    parser.add_argument(
        "--origin-template",
        default="https://enka.network/ui/{reference}.png",
        help=(
            "Asset-origin URL template. It must contain {reference}. "
            "Default: Enka's public Genshin icon endpoint."
        ),
    )

    arguments = parser.parse_args()

    if arguments.resolve_limit is not None and arguments.resolve_limit <= 0:
        parser.error("--resolve-limit must be greater than zero")

    if arguments.delay < 0:
        parser.error("--delay must not be negative")

    if arguments.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    if "{reference}" not in arguments.origin_template:
        parser.error("--origin-template must contain {reference}")

    return arguments


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
        require_object(
            value,
            context=f"{path.name} row",
        )
        for value in require_array(
            load_json(path),
            path=path,
        )
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


def resolved_name(
    record: dict[str, JsonValue],
    text_map: dict[str, str],
) -> str | None:
    return text_map.get(str(record.get("nameTextMapHash")))


def add_reference(
    *,
    candidates: set[AssetCandidate],
    invalid_references: list[InvalidReference],
    expected_subjects_by_role: dict[str, set[Subject]],
    subject_kind: str,
    subject_id: int,
    role: str,
    value: JsonValue | None,
) -> None:
    subject = (
        subject_kind,
        subject_id,
    )
    expected_subjects_by_role[role].add(subject)

    if not isinstance(value, str) or not value.strip():
        invalid_references.append(
            InvalidReference(
                subject_kind=subject_kind,
                subject_id=subject_id,
                role=role,
                value=value,
            )
        )
        return

    if value != value.strip():
        invalid_references.append(
            InvalidReference(
                subject_kind=subject_kind,
                subject_id=subject_id,
                role=role,
                value=value,
            )
        )
        return

    candidates.add(
        AssetCandidate(
            subject_kind=subject_kind,
            subject_id=subject_id,
            role=role,
            reference=value,
        )
    )


def collect_asset_candidates(
    dataset_root: Path,
) -> tuple[
    set[AssetCandidate],
    dict[str, set[Subject]],
    dict[str, set[int]],
    list[InvalidReference],
    set[int],
]:
    excel_root = dataset_root / "ExcelBinOutput"

    avatar_rows = load_records(excel_root / "AvatarExcelConfigData.json")
    fetter_rows = load_records(excel_root / "FetterInfoExcelConfigData.json")
    weapon_rows = load_records(excel_root / "WeaponExcelConfigData.json")
    material_rows = load_records(excel_root / "MaterialExcelConfigData.json")
    display_rows = load_records(excel_root / "DisplayItemExcelConfigData.json")
    codex_rows = load_records(excel_root / "ReliquaryCodexExcelConfigData.json")
    reliquary_rows = load_records(excel_root / "ReliquaryExcelConfigData.json")
    text_map = load_text_map(dataset_root)

    candidates: set[AssetCandidate] = set()
    invalid_references: list[InvalidReference] = []
    expected_subjects_by_role: dict[str, set[Subject]] = defaultdict(set)
    canonical_ids_by_kind: dict[str, set[int]] = defaultdict(set)

    fetter_avatar_ids = {
        require_integer(
            row.get("avatarId"),
            context="fetter avatarId",
        )
        for row in fetter_rows
    }

    for row in avatar_rows:
        if row.get("useType") != "AVATAR_FORMAL":
            continue

        avatar_id = require_integer(
            row.get("id"),
            context="formal avatar id",
        )

        if avatar_id not in fetter_avatar_ids:
            continue

        canonical_ids_by_kind["character"].add(avatar_id)

        add_reference(
            candidates=candidates,
            invalid_references=invalid_references,
            expected_subjects_by_role=expected_subjects_by_role,
            subject_kind="character",
            subject_id=avatar_id,
            role="character_icon",
            value=row.get("iconName"),
        )
        add_reference(
            candidates=candidates,
            invalid_references=invalid_references,
            expected_subjects_by_role=expected_subjects_by_role,
            subject_kind="character",
            subject_id=avatar_id,
            role="character_side_icon",
            value=row.get("sideIconName"),
        )

    for row in weapon_rows:
        if resolved_name(row, text_map) is None:
            continue

        weapon_id = require_integer(
            row.get("id"),
            context="resolvable weapon id",
        )
        canonical_ids_by_kind["weapon"].add(weapon_id)

        add_reference(
            candidates=candidates,
            invalid_references=invalid_references,
            expected_subjects_by_role=expected_subjects_by_role,
            subject_kind="weapon",
            subject_id=weapon_id,
            role="weapon_icon",
            value=row.get("icon"),
        )
        add_reference(
            candidates=candidates,
            invalid_references=invalid_references,
            expected_subjects_by_role=expected_subjects_by_role,
            subject_kind="weapon",
            subject_id=weapon_id,
            role="weapon_awakened_icon",
            value=row.get("awakenIcon"),
        )

    for row in material_rows:
        if row.get("materialType") not in _MATERIAL_TYPES:
            continue

        if resolved_name(row, text_map) is None:
            continue

        material_id = require_integer(
            row.get("id"),
            context="canonical material id",
        )
        canonical_ids_by_kind["material"].add(material_id)

        add_reference(
            candidates=candidates,
            invalid_references=invalid_references,
            expected_subjects_by_role=expected_subjects_by_role,
            subject_kind="material",
            subject_id=material_id,
            role="material_icon",
            value=row.get("icon"),
        )

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

    emitted_suit_ids: set[int] = set()
    missing_piece_ids: set[int] = set()

    for display_row in display_rows:
        display_icon = display_row.get("icon")

        if not isinstance(display_icon, str) or "RelicIcon" not in display_icon:
            continue

        suit_id = require_integer(
            display_row.get("param"),
            context="RelicIcon display param",
        )

        if suit_id in emitted_suit_ids:
            continue

        piece_rows_by_role: dict[
            str,
            dict[int, dict[str, JsonValue]],
        ] = defaultdict(dict)

        for codex_row in codex_rows_by_suit.get(suit_id, []):
            for field, role in _CODEX_ASSET_ROLES.items():
                raw_piece_id = codex_row.get(field)

                if raw_piece_id in (None, 0):
                    continue

                piece_id = require_integer(
                    raw_piece_id,
                    context=f"codex {field}",
                )
                piece_row = reliquary_rows_by_id.get(piece_id)

                if piece_row is None:
                    missing_piece_ids.add(piece_id)
                    continue

                piece_rows_by_role[role][piece_id] = piece_row

        if not piece_rows_by_role:
            continue

        if resolved_name(display_row, text_map) is None:
            continue

        canonical_ids_by_kind["artifact_set"].add(suit_id)

        for role, piece_rows in piece_rows_by_role.items():
            for piece_row in piece_rows.values():
                add_reference(
                    candidates=candidates,
                    invalid_references=invalid_references,
                    expected_subjects_by_role=expected_subjects_by_role,
                    subject_kind="artifact_set",
                    subject_id=suit_id,
                    role=role,
                    value=piece_row.get("icon"),
                )

        emitted_suit_ids.add(suit_id)

    return (
        candidates,
        expected_subjects_by_role,
        canonical_ids_by_kind,
        invalid_references,
        missing_piece_ids,
    )


def resolve_reference(
    reference: str,
    *,
    origin_template: str,
    timeout: float,
) -> ResolutionResult:
    encoded_reference = urllib.parse.quote(
        reference,
        safe="",
    )
    url = origin_template.format(reference=encoded_reference)
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={
            "User-Agent": "Teyvat-Vision-Asset-Audit/0.1",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            return ResolutionResult(
                reference=reference,
                url=url,
                status=response.status,
                content_type=response.headers.get("Content-Type"),
                content_length=response.headers.get("Content-Length"),
                error=None,
            )
    except urllib.error.HTTPError as error:
        return ResolutionResult(
            reference=reference,
            url=url,
            status=error.code,
            content_type=error.headers.get("Content-Type"),
            content_length=error.headers.get("Content-Length"),
            error=str(error),
        )
    except urllib.error.URLError as error:
        return ResolutionResult(
            reference=reference,
            url=url,
            status=None,
            content_type=None,
            content_length=None,
            error=str(error.reason),
        )


def print_local_audit(
    *,
    candidates: set[AssetCandidate],
    expected_subjects_by_role: dict[str, set[Subject]],
    canonical_ids_by_kind: dict[str, set[int]],
    invalid_references: list[InvalidReference],
    missing_piece_ids: set[int],
) -> None:
    candidates_by_role: dict[str, list[AssetCandidate]] = defaultdict(list)
    references_to_candidates: dict[str, set[AssetCandidate]] = defaultdict(set)
    references_by_subject_role: dict[
        tuple[Subject, str],
        set[str],
    ] = defaultdict(set)

    for candidate in candidates:
        candidates_by_role[candidate.role].append(candidate)
        references_to_candidates[candidate.reference].add(candidate)
        references_by_subject_role[
            (
                candidate.subject,
                candidate.role,
            )
        ].add(candidate.reference)

    print("Canonical subjects:")

    for kind in _KIND_ORDER:
        print(
            json.dumps(
                {
                    "kind": kind,
                    "subjectCount": len(canonical_ids_by_kind[kind]),
                },
                sort_keys=True,
            )
        )

    print()
    print("Asset-role coverage:")

    for role in sorted(expected_subjects_by_role):
        expected_subjects = expected_subjects_by_role[role]
        referenced_subjects = {candidate.subject for candidate in candidates_by_role.get(role, [])}
        missing_subjects = sorted(
            expected_subjects - referenced_subjects,
            key=lambda subject: (
                subject[0],
                subject[1],
            ),
        )

        print(
            json.dumps(
                {
                    "role": role,
                    "expectedSubjectCount": len(expected_subjects),
                    "referencedSubjectCount": len(referenced_subjects),
                    "candidateRelationshipCount": len(
                        candidates_by_role.get(
                            role,
                            [],
                        )
                    ),
                    "missingSubjectCount": len(missing_subjects),
                    "missingSubjects": [
                        {
                            "kind": kind,
                            "id": subject_id,
                        }
                        for kind, subject_id in missing_subjects
                    ],
                },
                sort_keys=True,
            )
        )

    print()
    print(f"Candidate relationships: {len(candidates)}")
    print(f"Unique symbolic references: {len(references_to_candidates)}")
    print(f"Invalid or blank references: {len(invalid_references)}")
    print(f"Missing referenced reliquary piece IDs: {sorted(missing_piece_ids)}")

    for invalid in sorted(
        invalid_references,
        key=lambda result: (
            result.subject_kind,
            result.subject_id,
            result.role,
        ),
    ):
        print(
            json.dumps(
                {
                    "kind": invalid.subject_kind,
                    "id": invalid.subject_id,
                    "role": invalid.role,
                    "value": invalid.value,
                },
                sort_keys=True,
            )
        )

    multiple_references: list[tuple[str, int, str, list[str]]] = [
        (
            subject[0],
            subject[1],
            role,
            sorted(references),
        )
        for (subject, role), references in references_by_subject_role.items()
        if len(references) > 1
    ]

    print()
    print(f"Subject-role pairs with multiple references: {len(multiple_references)}")

    for subject_kind, subject_id, role, references in sorted(
        multiple_references,
        key=lambda value: (
            value[0],
            value[1],
            value[2],
        ),
    ):
        print(
            json.dumps(
                {
                    "kind": subject_kind,
                    "id": subject_id,
                    "role": role,
                    "references": references,
                },
                sort_keys=True,
            )
        )

    shared_references = {
        reference: sorted(
            {
                (
                    candidate.subject_kind,
                    candidate.subject_id,
                )
                for candidate in matching_candidates
            },
            key=lambda subject: (
                subject[0],
                subject[1],
            ),
        )
        for reference, matching_candidates in references_to_candidates.items()
        if len({candidate.subject for candidate in matching_candidates}) > 1
    }

    print()
    print(f"References shared by multiple subjects: {len(shared_references)}")

    for reference, subjects in sorted(shared_references.items()):
        print(
            json.dumps(
                {
                    "reference": reference,
                    "subjects": [
                        {
                            "kind": kind,
                            "id": subject_id,
                        }
                        for kind, subject_id in subjects
                    ],
                },
                sort_keys=True,
            )
        )

    cross_kind_references = {
        reference: sorted({candidate.subject_kind for candidate in matching_candidates})
        for reference, matching_candidates in references_to_candidates.items()
        if len({candidate.subject_kind for candidate in matching_candidates}) > 1
    }

    print()
    print(f"References shared across entity kinds: {len(cross_kind_references)}")

    for reference, kinds in sorted(cross_kind_references.items()):
        print(
            json.dumps(
                {
                    "reference": reference,
                    "kinds": kinds,
                },
                sort_keys=True,
            )
        )


def print_remote_audit(
    candidates: set[AssetCandidate],
    *,
    origin_template: str,
    resolve_limit: int | None,
    delay: float,
    timeout: float,
) -> None:
    references = sorted({candidate.reference for candidate in candidates})

    if resolve_limit is not None:
        references = references[:resolve_limit]

    print()
    print(f"Resolving symbolic references: {len(references)}")
    print(f"Origin template: {origin_template}")
    print(f"Delay between requests: {delay}")
    print()

    results: list[ResolutionResult] = []

    for index, reference in enumerate(references):
        result = resolve_reference(
            reference,
            origin_template=origin_template,
            timeout=timeout,
        )
        results.append(result)

        if index + 1 < len(references) and delay:
            time.sleep(delay)

    status_counts = Counter(
        result.status if result.status is not None else "ERROR" for result in results
    )
    image_count = sum(result.is_image for result in results)
    failed_results = [result for result in results if not result.is_image]

    print(f"Resolution statuses: {dict(status_counts)}")
    print(f"Successful image responses: {image_count}")
    print(f"Unresolved or non-image responses: {len(failed_results)}")

    for result in failed_results:
        print(
            json.dumps(
                {
                    "reference": result.reference,
                    "url": result.url,
                    "status": result.status,
                    "contentType": result.content_type,
                    "contentLength": result.content_length,
                    "error": result.error,
                },
                sort_keys=True,
            )
        )


def main() -> None:
    arguments = parse_arguments()
    dataset_root = arguments.dataset_root.resolve()

    (
        candidates,
        expected_subjects_by_role,
        canonical_ids_by_kind,
        invalid_references,
        missing_piece_ids,
    ) = collect_asset_candidates(dataset_root)

    print_local_audit(
        candidates=candidates,
        expected_subjects_by_role=expected_subjects_by_role,
        canonical_ids_by_kind=canonical_ids_by_kind,
        invalid_references=invalid_references,
        missing_piece_ids=missing_piece_ids,
    )

    if arguments.check_enka:
        print_remote_audit(
            candidates,
            origin_template=arguments.origin_template,
            resolve_limit=arguments.resolve_limit,
            delay=arguments.delay,
            timeout=arguments.timeout,
        )


if __name__ == "__main__":
    main()

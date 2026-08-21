"""AnimeGameData static provider for Teyvat Vision."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import GameDataAsset
from teyvat_vision.game_data.classification import Rarity, WeaponType
from teyvat_vision.game_data.localization import LocalizedName
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)
from teyvat_vision.game_data.source import GameDataSource

_WEAPON_TYPES = {
    "WEAPON_SWORD_ONE_HAND": WeaponType.SWORD,
    "WEAPON_CLAYMORE": WeaponType.CLAYMORE,
    "WEAPON_POLE": WeaponType.POLEARM,
    "WEAPON_BOW": WeaponType.BOW,
    "WEAPON_CATALYST": WeaponType.CATALYST,
}

_RARITIES = {
    "QUALITY_WHITE": Rarity.ONE_STAR,
    "QUALITY_GREEN": Rarity.TWO_STAR,
    "QUALITY_BLUE": Rarity.THREE_STAR,
    "QUALITY_PURPLE": Rarity.FOUR_STAR,
    "QUALITY_ORANGE": Rarity.FIVE_STAR,
    "QUALITY_ORANGE_SP": Rarity.FIVE_STAR,
}


@dataclass(frozen=True, slots=True)
class AnimeGameDataProvider:
    """Load canonical static game data from a local AnimeGameData2 checkout."""

    root: Path
    game_version: str
    revision: str | None = None

    def __post_init__(self) -> None:
        if not self.game_version:
            raise ValueError("game_version must be non-empty")

        if self.game_version != self.game_version.strip():
            raise ValueError("game_version must not contain surrounding whitespace")

        if self.revision is not None:
            if not self.revision:
                raise ValueError("revision must be non-empty when provided")

            if self.revision != self.revision.strip():
                raise ValueError("revision must not contain surrounding whitespace")

    def version(self) -> str:
        """Return the Genshin game-data version exposed by this provider."""

        return self.game_version

    def source(self) -> GameDataSource:
        """Return provenance for the AnimeGameData2 source dataset."""

        return GameDataSource(
            provider="Dimbreath/AnimeGameData2",
            version=self.game_version,
            revision=self.revision,
        )

    def characters(self) -> tuple[CharacterDefinition, ...]:
        """Load canonical character definitions."""

        avatar_records = self._load_records(
            self.root / "ExcelBinOutput" / "AvatarExcelConfigData.json"
        )

        if not avatar_records:
            raise ValueError("AvatarExcelConfigData.json must not be empty")

        fetter_records = self._load_records(
            self.root / "ExcelBinOutput" / "FetterInfoExcelConfigData.json"
        )

        fetter_avatar_ids = {self._required_int(record, "avatarId") for record in fetter_records}

        member_records = tuple(
            record
            for record in avatar_records
            if record.get("useType") == "AVATAR_FORMAL"
            and self._required_int(record, "id") in fetter_avatar_ids
        )

        return tuple(self._character_definition(record) for record in member_records)

    def weapons(self) -> tuple[WeaponDefinition, ...]:
        """Load canonical weapon definitions."""

        weapon_records = self._load_records(
            self.root / "ExcelBinOutput" / "WeaponExcelConfigData.json"
        )

        if not weapon_records:
            raise ValueError("WeaponExcelConfigData.json must not be empty")

        text_map = self._load_english_text_map()
        member_records: list[tuple[dict[str, object], str]] = []

        for record in weapon_records:
            name = self._resolved_name(record, text_map)

            if name is not None:
                member_records.append((record, name))

        return tuple(self._weapon_definition(record, name) for record, name in member_records)

    def artifact_sets(self) -> tuple[ArtifactSetDefinition, ...]:
        """Load canonical artifact-set definitions."""

        return ()

    def materials(self) -> tuple[MaterialDefinition, ...]:
        """Load canonical material definitions."""

        return ()

    def assets(self) -> tuple[GameDataAsset, ...]:
        """Load canonical static asset references."""

        return ()

    @staticmethod
    def _load_records(path: Path) -> tuple[dict[str, object], ...]:
        raw: object = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(raw, list):
            raise ValueError(f"{path.name} must contain a JSON array")

        raw_records = cast(list[object], raw)
        records: list[dict[str, object]] = []

        for raw_record in raw_records:
            if not isinstance(raw_record, dict):
                raise ValueError(f"{path.name} must contain only JSON objects")

            raw_mapping = cast(dict[object, object], raw_record)
            record: dict[str, object] = {}

            for key, value in raw_mapping.items():
                if not isinstance(key, str):
                    raise ValueError(f"{path.name} JSON object keys must be strings")

                record[key] = value

            records.append(record)

        return tuple(records)

    def _load_english_text_map(self) -> dict[str, str]:
        text_map: dict[str, str] = {}

        for filename in (
            "TextMapEN.json",
            "TextMap_MediumEN.json",
        ):
            path = self.root / "TextMap" / filename
            raw: object = json.loads(path.read_text(encoding="utf-8"))

            if not isinstance(raw, dict):
                raise ValueError(f"{path.name} must contain a JSON object")

            raw_mapping = cast(dict[object, object], raw)

            for key, value in raw_mapping.items():
                if not isinstance(key, str):
                    raise ValueError(f"{path.name} JSON object keys must be strings")

                if not isinstance(value, str):
                    raise ValueError(f"{path.name} JSON object values must be strings")

                if value.strip():
                    text_map[key] = value

        return text_map

    @staticmethod
    def _resolved_name(
        record: dict[str, object],
        text_map: dict[str, str],
    ) -> str | None:
        name_hash = record.get("nameTextMapHash")
        name = text_map.get(str(name_hash))

        if name is None or not name.strip():
            return None

        return name

    @staticmethod
    def _character_definition(
        record: dict[str, object],
    ) -> CharacterDefinition:
        raw_id = AnimeGameDataProvider._required_int(
            record,
            "id",
        )
        raw_weapon_type = AnimeGameDataProvider._required_str(
            record,
            "weaponType",
        )
        raw_rarity = AnimeGameDataProvider._required_str(
            record,
            "qualityType",
        )

        return CharacterDefinition(
            identity=CanonicalId(
                kind=EntityKind.CHARACTER,
                key=str(raw_id),
            ),
            weapon_type=AnimeGameDataProvider._weapon_type(raw_weapon_type),
            rarity=AnimeGameDataProvider._rarity(raw_rarity),
        )

    @staticmethod
    def _weapon_definition(
        record: dict[str, object],
        name: str,
    ) -> WeaponDefinition:
        raw_id = AnimeGameDataProvider._required_int(
            record,
            "id",
        )
        raw_weapon_type = AnimeGameDataProvider._required_str(
            record,
            "weaponType",
        )
        raw_rank_level = AnimeGameDataProvider._required_int(
            record,
            "rankLevel",
        )

        return WeaponDefinition(
            identity=CanonicalId(
                kind=EntityKind.WEAPON,
                key=str(raw_id),
            ),
            names=(
                LocalizedName(
                    locale="en",
                    value=name,
                ),
            ),
            weapon_type=AnimeGameDataProvider._weapon_type(raw_weapon_type),
            rarity=AnimeGameDataProvider._weapon_rarity(raw_rank_level),
        )

    @staticmethod
    def _required_int(
        record: dict[str, object],
        field: str,
    ) -> int:
        value = record.get(field)

        if type(value) is not int:
            raise ValueError(f"AnimeGameData field {field!r} must be an integer")

        return value

    @staticmethod
    def _required_str(
        record: dict[str, object],
        field: str,
    ) -> str:
        value = record.get(field)

        if not isinstance(value, str) or not value:
            raise ValueError(f"AnimeGameData field {field!r} must be a non-empty string")

        return value

    @staticmethod
    def _weapon_type(raw: str) -> WeaponType:
        try:
            return _WEAPON_TYPES[raw]
        except KeyError as exc:
            raise ValueError(f"unsupported AnimeGameData weapon type: {raw}") from exc

    @staticmethod
    def _rarity(raw: str) -> Rarity:
        try:
            return _RARITIES[raw]
        except KeyError as exc:
            raise ValueError(f"unsupported AnimeGameData rarity: {raw}") from exc

    @staticmethod
    def _weapon_rarity(raw: int) -> Rarity:
        try:
            return Rarity(raw)
        except ValueError as exc:
            raise ValueError(f"unsupported AnimeGameData weapon rankLevel: {raw}") from exc

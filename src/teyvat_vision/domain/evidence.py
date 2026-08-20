"""Association between canonical account state and supporting observation evidence."""

from dataclasses import dataclass
from typing import Any

from teyvat_vision.domain.account import AccountSnapshot
from teyvat_vision.domain.artifact import Artifact
from teyvat_vision.domain.identity import CanonicalId
from teyvat_vision.domain.observation import Observation

_CHARACTER_FIELDS = frozenset(
    {
        "level",
        "ascension",
        "constellation",
        "custom_name",
        "talents.normal",
        "talents.skill",
        "talents.burst",
    }
)

_WEAPON_FIELDS = frozenset(
    {
        "level",
        "ascension",
        "refinement",
        "locked",
        "equipped_to",
    }
)

_MATERIAL_FIELDS = frozenset(
    {
        "quantity",
    }
)

_ARTIFACT_FIELDS = frozenset(
    {
        "slot",
        "rarity",
        "level",
        "main_stat.key",
        "main_stat.value",
        "locked",
        "equipped_to",
    }
)


@dataclass(frozen=True, slots=True)
class SnapshotEvidence:
    """An account snapshot together with the observations supporting it.

    Every associated observation must address a subject actually represented by
    the canonical snapshot and a semantic field supported by that subject.
    Evidence for unresolved or otherwise unrepresented subjects remains outside
    this association until that subject enters accepted snapshot state.
    """

    snapshot: AccountSnapshot
    observations: tuple[Observation[Any], ...]

    def __post_init__(self) -> None:
        characters_by_identity = {
            character.identity: character for character in self.snapshot.characters.items
        }
        materials_by_identity = {
            material.identity: material for material in self.snapshot.materials.items
        }
        weapons_by_identity = {weapon.identity: weapon for weapon in self.snapshot.weapons.items}
        artifacts_by_identity = {
            artifact.identity: artifact for artifact in self.snapshot.artifacts.items
        }

        for observation in self.observations:
            subject = observation.target.subject
            field = observation.target.field

            if isinstance(subject, CanonicalId):
                if subject in characters_by_identity:
                    self._validate_field(
                        field=field,
                        supported_fields=_CHARACTER_FIELDS,
                    )
                    continue

                if subject in materials_by_identity:
                    self._validate_field(
                        field=field,
                        supported_fields=_MATERIAL_FIELDS,
                    )
                    continue

                raise ValueError("observation subject is absent from the associated snapshot")

            if subject in weapons_by_identity:
                self._validate_field(
                    field=field,
                    supported_fields=_WEAPON_FIELDS,
                )
                continue

            artifact = artifacts_by_identity.get(subject)

            if artifact is not None:
                self._validate_artifact_field(
                    artifact=artifact,
                    field=field,
                )
                continue

            raise ValueError("observation subject is absent from the associated snapshot")

    @staticmethod
    def _validate_field(
        *,
        field: str,
        supported_fields: frozenset[str],
    ) -> None:
        if field not in supported_fields:
            raise ValueError(f"observation field {field!r} is not supported by the subject")

    @staticmethod
    def _validate_artifact_field(
        *,
        artifact: Artifact,
        field: str,
    ) -> None:
        if field in _ARTIFACT_FIELDS:
            return

        prefix = "substats."

        if field.startswith(prefix):
            substat_key = field.removeprefix(prefix)

            if substat_key and any(substat.key == substat_key for substat in artifact.substats):
                return

        raise ValueError(f"observation field {field!r} is not supported by the subject")

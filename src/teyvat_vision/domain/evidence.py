"""Association between canonical account state and supporting observation evidence."""

from dataclasses import dataclass
from typing import Any

from teyvat_vision.domain.account import AccountSnapshot
from teyvat_vision.domain.identity import CanonicalId
from teyvat_vision.domain.observation import Observation


@dataclass(frozen=True, slots=True)
class SnapshotEvidence:
    """An account snapshot together with the observations supporting it.

    Every associated observation must address a subject actually represented by
    the canonical snapshot. Evidence for unresolved or otherwise unrepresented
    subjects remains outside this association until that subject enters accepted
    snapshot state.
    """

    snapshot: AccountSnapshot
    observations: tuple[Observation[Any], ...]

    def __post_init__(self) -> None:
        canonical_subjects = {
            character.identity for character in self.snapshot.characters.items
        } | {material.identity for material in self.snapshot.materials.items}

        owned_item_subjects = {
            weapon.identity for weapon in self.snapshot.weapons.items
        } | {artifact.identity for artifact in self.snapshot.artifacts.items}

        for observation in self.observations:
            subject = observation.target.subject

            if isinstance(subject, CanonicalId):
                if subject not in canonical_subjects:
                    raise ValueError(
                        "observation subject is absent from the associated snapshot"
                    )
                continue

            if subject not in owned_item_subjects:
                raise ValueError(
                    "observation subject is absent from the associated snapshot"
                )
            
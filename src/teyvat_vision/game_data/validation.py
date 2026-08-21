"""Structured static game-data validation for canonical account state."""

from dataclasses import dataclass
from enum import StrEnum

from teyvat_vision.domain.account import AccountSnapshot
from teyvat_vision.domain.identity import CanonicalId
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.game_data.dataset import StaticGameData


class ValidationSeverity(StrEnum):
    """Severity of one domain-validation issue."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One structured issue discovered during domain validation."""

    code: str
    severity: ValidationSeverity
    message: str
    subject: CanonicalId | OwnedItemId | None = None
    field: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Collection of issues produced by one validation operation."""

    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        """Return whether the result contains no validation errors."""

        return not self.errors

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        """Return only error-severity issues."""

        return tuple(issue for issue in self.issues if issue.severity is ValidationSeverity.ERROR)

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        """Return only warning-severity issues."""

        return tuple(issue for issue in self.issues if issue.severity is ValidationSeverity.WARNING)


def validate_snapshot_against_game_data(
    snapshot: AccountSnapshot,
    game_data: StaticGameData,
) -> ValidationResult:
    """Validate canonical account state against normalized static game data."""

    character_definitions = {definition.identity: definition for definition in game_data.characters}
    weapon_definitions = {definition.identity: definition for definition in game_data.weapons}
    artifact_set_definitions = {
        definition.identity: definition for definition in game_data.artifact_sets
    }
    material_identities = {definition.identity for definition in game_data.materials}

    issues: list[ValidationIssue] = []

    for character in snapshot.characters.items:
        if character.identity not in character_definitions:
            issues.append(
                ValidationIssue(
                    code="unknown_character",
                    severity=ValidationSeverity.ERROR,
                    message=("character identity is absent from static game data"),
                    subject=character.identity,
                    field="identity",
                )
            )

    for weapon in snapshot.weapons.items:
        weapon_definition = weapon_definitions.get(weapon.identity.definition)

        if weapon_definition is None:
            issues.append(
                ValidationIssue(
                    code="unknown_weapon",
                    severity=ValidationSeverity.ERROR,
                    message=("weapon definition identity is absent from static game data"),
                    subject=weapon.identity,
                    field="identity.definition",
                )
            )
            continue

        if weapon.equipped_to is None:
            continue

        character_definition = character_definitions.get(weapon.equipped_to)

        if character_definition is None:
            continue

        if (
            weapon_definition.weapon_type is not None
            and character_definition.weapon_type is not None
            and weapon_definition.weapon_type is not character_definition.weapon_type
        ):
            issues.append(
                ValidationIssue(
                    code="weapon_type_mismatch",
                    severity=ValidationSeverity.ERROR,
                    message=("equipped weapon type does not match character weapon type"),
                    subject=weapon.identity,
                    field="equipped_to",
                )
            )

    for artifact in snapshot.artifacts.items:
        artifact_set_definition = artifact_set_definitions.get(artifact.identity.definition)

        if artifact_set_definition is None:
            issues.append(
                ValidationIssue(
                    code="unknown_artifact_set",
                    severity=ValidationSeverity.ERROR,
                    message=("artifact set definition identity is absent from static game data"),
                    subject=artifact.identity,
                    field="identity.definition",
                )
            )
            continue

        if artifact_set_definition.rarities and artifact.rarity not in {
            rarity.value for rarity in artifact_set_definition.rarities
        }:
            issues.append(
                ValidationIssue(
                    code="artifact_rarity_mismatch",
                    severity=ValidationSeverity.ERROR,
                    message=("artifact rarity is not available for its artifact set"),
                    subject=artifact.identity,
                    field="rarity",
                )
            )

        if artifact_set_definition.slots and artifact.slot not in artifact_set_definition.slots:
            issues.append(
                ValidationIssue(
                    code="artifact_slot_mismatch",
                    severity=ValidationSeverity.ERROR,
                    message=("artifact slot is not available for its artifact set"),
                    subject=artifact.identity,
                    field="slot",
                )
            )

    for material in snapshot.materials.items:
        if material.identity not in material_identities:
            issues.append(
                ValidationIssue(
                    code="unknown_material",
                    severity=ValidationSeverity.ERROR,
                    message=("material identity is absent from static game data"),
                    subject=material.identity,
                    field="identity",
                )
            )

    return ValidationResult(
        issues=tuple(issues),
    )

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
    """Validate account entity identities against normalized static game data."""

    character_identities = {definition.identity for definition in game_data.characters}
    weapon_identities = {definition.identity for definition in game_data.weapons}
    artifact_set_identities = {definition.identity for definition in game_data.artifact_sets}
    material_identities = {definition.identity for definition in game_data.materials}

    issues: list[ValidationIssue] = []

    for character in snapshot.characters.items:
        if character.identity not in character_identities:
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
        if weapon.identity.definition not in weapon_identities:
            issues.append(
                ValidationIssue(
                    code="unknown_weapon",
                    severity=ValidationSeverity.ERROR,
                    message=("weapon definition identity is absent from static game data"),
                    subject=weapon.identity,
                    field="identity.definition",
                )
            )

    for artifact in snapshot.artifacts.items:
        if artifact.identity.definition not in artifact_set_identities:
            issues.append(
                ValidationIssue(
                    code="unknown_artifact_set",
                    severity=ValidationSeverity.ERROR,
                    message=("artifact set definition identity is absent from static game data"),
                    subject=artifact.identity,
                    field="identity.definition",
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

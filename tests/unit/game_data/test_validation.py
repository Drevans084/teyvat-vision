from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


def test_validation_severity_has_stable_values() -> None:
    assert ValidationSeverity.ERROR.value == "error"
    assert ValidationSeverity.WARNING.value == "warning"


def test_validation_issue_preserves_details() -> None:
    subject = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000047",
    )

    issue = ValidationIssue(
        code="unknown_character",
        severity=ValidationSeverity.ERROR,
        message="character identity is absent from static game data",
        subject=subject,
        field="identity",
    )

    assert issue.code == "unknown_character"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.message == ("character identity is absent from static game data")
    assert issue.subject == subject
    assert issue.field == "identity"


def test_validation_issue_allows_no_subject() -> None:
    issue = ValidationIssue(
        code="dataset_problem",
        severity=ValidationSeverity.WARNING,
        message="static game data is incomplete",
    )

    assert issue.subject is None
    assert issue.field is None


def test_validation_result_with_no_issues_is_valid() -> None:
    result = ValidationResult()

    assert result.is_valid
    assert result.issues == ()
    assert result.errors == ()
    assert result.warnings == ()


def test_validation_result_with_warning_remains_valid() -> None:
    warning = ValidationIssue(
        code="incomplete_static_data",
        severity=ValidationSeverity.WARNING,
        message="static game data coverage is incomplete",
    )

    result = ValidationResult(
        issues=(warning,),
    )

    assert result.is_valid
    assert result.errors == ()
    assert result.warnings == (warning,)


def test_validation_result_with_error_is_invalid() -> None:
    error = ValidationIssue(
        code="unknown_character",
        severity=ValidationSeverity.ERROR,
        message="character identity is absent from static game data",
    )

    result = ValidationResult(
        issues=(error,),
    )

    assert not result.is_valid
    assert result.errors == (error,)
    assert result.warnings == ()


def test_validation_result_separates_errors_and_warnings() -> None:
    error = ValidationIssue(
        code="unknown_weapon",
        severity=ValidationSeverity.ERROR,
        message="weapon identity is absent from static game data",
    )
    warning = ValidationIssue(
        code="incomplete_static_data",
        severity=ValidationSeverity.WARNING,
        message="static game data coverage is incomplete",
    )

    result = ValidationResult(
        issues=(
            warning,
            error,
        ),
    )

    assert result.errors == (error,)
    assert result.warnings == (warning,)

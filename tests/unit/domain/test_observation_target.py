import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.observation import ObservationTarget


def character_id(key: str = "10000002") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def material_id(key: str = "104003") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.MATERIAL,
        key=key,
    )


def weapon_id(
    key: str = "11509",
    *,
    instance_key: str = "weapon-000001",
) -> OwnedItemId:
    return OwnedItemId(
        definition=CanonicalId(
            kind=EntityKind.WEAPON,
            key=key,
        ),
        instance_key=instance_key,
    )


def artifact_id(
    key: str = "15001",
    *,
    instance_key: str = "artifact-000001",
) -> OwnedItemId:
    return OwnedItemId(
        definition=CanonicalId(
            kind=EntityKind.ARTIFACT_SET,
            key=key,
        ),
        instance_key=instance_key,
    )


def test_character_can_be_observation_subject() -> None:
    target = ObservationTarget(
        subject=character_id(),
        field="level",
    )

    assert target.subject == character_id()
    assert target.field == "level"


def test_material_can_be_observation_subject() -> None:
    target = ObservationTarget(
        subject=material_id(),
        field="quantity",
    )

    assert target.subject == material_id()
    assert target.field == "quantity"


def test_owned_weapon_can_be_observation_subject() -> None:
    subject = weapon_id()

    target = ObservationTarget(
        subject=subject,
        field="refinement",
    )

    assert target.subject == subject
    assert target.field == "refinement"


def test_owned_artifact_can_be_observation_subject() -> None:
    subject = artifact_id()

    target = ObservationTarget(
        subject=subject,
        field="main_stat.value",
    )

    assert target.subject == subject
    assert target.field == "main_stat.value"


@pytest.mark.parametrize(
    "kind",
    [
        EntityKind.WEAPON,
        EntityKind.ARTIFACT_SET,
    ],
)
def test_definition_only_identity_cannot_address_duplicate_capable_item(
    kind: EntityKind,
) -> None:
    with pytest.raises(ValueError, match="owned item"):
        ObservationTarget(
            subject=CanonicalId(
                kind=kind,
                key="15001",
            ),
            field="level",
        )


@pytest.mark.parametrize(
    "field",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_observation_target_rejects_blank_field(field: str) -> None:
    with pytest.raises(ValueError, match="field"):
        ObservationTarget(
            subject=character_id(),
            field=field,
        )


@pytest.mark.parametrize(
    "field",
    [
        " level",
        "level ",
        " level ",
    ],
)
def test_observation_target_rejects_surrounding_whitespace_in_field(
    field: str,
) -> None:
    with pytest.raises(ValueError, match="field"):
        ObservationTarget(
            subject=character_id(),
            field=field,
        )


def test_field_path_is_case_preserving() -> None:
    upper = ObservationTarget(
        subject=character_id(),
        field="CustomName",
    )
    lower = ObservationTarget(
        subject=character_id(),
        field="customname",
    )

    assert upper.field == "CustomName"
    assert lower.field == "customname"
    assert upper != lower


def test_targets_for_two_owned_copies_are_distinct() -> None:
    first = ObservationTarget(
        subject=weapon_id(instance_key="weapon-000001"),
        field="level",
    )
    second = ObservationTarget(
        subject=weapon_id(instance_key="weapon-000002"),
        field="level",
    )

    assert first != second


def test_observation_target_is_hashable() -> None:
    target = ObservationTarget(
        subject=character_id(),
        field="level",
    )

    targets = {target}

    assert target in targets


def test_observation_target_has_stable_string_representation() -> None:
    target = ObservationTarget(
        subject=weapon_id(),
        field="refinement",
    )

    assert str(target) == "weapon:11509#weapon-000001.refinement"

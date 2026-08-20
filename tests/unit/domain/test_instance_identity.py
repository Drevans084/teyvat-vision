import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId


def weapon_id(key: str = "11509") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.WEAPON,
        key=key,
    )


def artifact_set_id(key: str = "15001") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key=key,
    )


def test_owned_item_id_preserves_definition_identity_and_instance_key() -> None:
    identity = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-000001",
    )

    assert identity.definition == weapon_id()
    assert identity.instance_key == "scan-000001"


def test_owned_item_id_has_stable_string_representation() -> None:
    identity = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-000001",
    )

    assert str(identity) == "weapon:11509#scan-000001"


def test_two_copies_of_same_definition_are_distinct() -> None:
    first = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-000001",
    )
    second = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-000002",
    )

    assert first != second


def test_same_instance_key_on_different_definitions_is_distinct() -> None:
    weapon = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-000001",
    )
    artifact = OwnedItemId(
        definition=artifact_set_id(),
        instance_key="scan-000001",
    )

    assert weapon != artifact


@pytest.mark.parametrize(
    "instance_key",
    [
        "",
        "   ",
        " scan-000001",
        "scan-000001 ",
    ],
)
def test_owned_item_id_rejects_invalid_instance_key(instance_key: str) -> None:
    with pytest.raises(ValueError, match="instance"):
        OwnedItemId(
            definition=weapon_id(),
            instance_key=instance_key,
        )


def test_owned_item_id_preserves_case() -> None:
    upper = OwnedItemId(
        definition=weapon_id(),
        instance_key="Scan-A",
    )
    lower = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-a",
    )

    assert upper.instance_key == "Scan-A"
    assert lower.instance_key == "scan-a"
    assert upper != lower


def test_owned_item_id_is_hashable() -> None:
    identity = OwnedItemId(
        definition=weapon_id(),
        instance_key="scan-000001",
    )

    identities = {identity}

    assert identity in identities


@pytest.mark.parametrize(
    "kind",
    [
        EntityKind.CHARACTER,
        EntityKind.MATERIAL,
    ],
)
def test_owned_item_id_rejects_non_instance_entity_kinds(kind: EntityKind) -> None:
    with pytest.raises(ValueError, match="weapon or artifact"):
        OwnedItemId(
            definition=CanonicalId(
                kind=kind,
                key="10000002",
            ),
            instance_key="scan-000001",
        )

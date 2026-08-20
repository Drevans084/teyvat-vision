import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind


def test_canonical_id_preserves_kind_and_key() -> None:
    identity = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )

    assert identity.kind is EntityKind.CHARACTER
    assert identity.key == "10000002"


def test_canonical_id_has_stable_string_representation() -> None:
    identity = CanonicalId(
        kind=EntityKind.WEAPON,
        key="11509",
    )

    assert str(identity) == "weapon:11509"


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        " 10000002",
        "10000002 ",
    ],
)
def test_canonical_id_rejects_invalid_keys(key: str) -> None:
    with pytest.raises(ValueError, match="key"):
        CanonicalId(
            kind=EntityKind.CHARACTER,
            key=key,
        )


def test_canonical_id_treats_key_as_opaque_machine_identity() -> None:
    identity = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="Some_Upstream-ID_123",
    )

    assert identity.key == "Some_Upstream-ID_123"


def test_canonical_id_preserves_case() -> None:
    upper = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="TravelerVariant",
    )
    lower = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="travelervariant",
    )

    assert upper.key == "TravelerVariant"
    assert lower.key == "travelervariant"
    assert upper != lower


def test_canonical_id_is_hashable() -> None:
    identity = CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key="15001",
    )

    identities = {identity}

    assert identity in identities


def test_same_key_in_different_entity_kinds_is_not_equal() -> None:
    character = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )
    weapon = CanonicalId(
        kind=EntityKind.WEAPON,
        key="10000002",
    )

    assert character != weapon

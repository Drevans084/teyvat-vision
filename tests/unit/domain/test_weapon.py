import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.weapon import Weapon


def weapon_definition(key: str = "11509") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.WEAPON,
        key=key,
    )


def weapon_id(
    key: str = "11509",
    *,
    instance_key: str = "weapon-000001",
) -> OwnedItemId:
    return OwnedItemId(
        definition=weapon_definition(key),
        instance_key=instance_key,
    )


def character_id(key: str = "10000002") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def test_weapon_preserves_valid_account_state() -> None:
    identity = weapon_id()

    weapon = Weapon(
        identity=identity,
        level=90,
        ascension=6,
        refinement=5,
        locked=True,
    )

    assert weapon.identity == identity
    assert weapon.identity.definition == weapon_definition()
    assert weapon.level == 90
    assert weapon.ascension == 6
    assert weapon.refinement == 5
    assert weapon.locked is True


def test_two_owned_copies_of_same_weapon_have_distinct_identity() -> None:
    first = Weapon(
        identity=weapon_id(instance_key="weapon-000001"),
        level=90,
        ascension=6,
        refinement=1,
        locked=True,
    )
    second = Weapon(
        identity=weapon_id(instance_key="weapon-000002"),
        level=90,
        ascension=6,
        refinement=1,
        locked=True,
    )

    assert first.identity.definition == second.identity.definition
    assert first.identity != second.identity


def test_weapon_can_be_equipped_to_character() -> None:
    owner = character_id()

    weapon = Weapon(
        identity=weapon_id(),
        level=90,
        ascension=6,
        refinement=1,
        locked=True,
        equipped_to=owner,
    )

    assert weapon.equipped_to == owner


def test_weapon_can_be_unequipped() -> None:
    weapon = Weapon(
        identity=weapon_id(),
        level=1,
        ascension=0,
        refinement=1,
        locked=False,
    )

    assert weapon.equipped_to is None


def test_weapon_rejects_non_weapon_owned_item_identity() -> None:
    with pytest.raises(ValueError, match="weapon"):
        Weapon(
            identity=OwnedItemId(
                definition=CanonicalId(
                    kind=EntityKind.ARTIFACT_SET,
                    key="15001",
                ),
                instance_key="artifact-000001",
            ),
            level=90,
            ascension=6,
            refinement=1,
            locked=True,
        )


def test_weapon_rejects_non_character_equipment_owner() -> None:
    with pytest.raises(ValueError, match="equipped"):
        Weapon(
            identity=weapon_id(),
            level=90,
            ascension=6,
            refinement=1,
            locked=True,
            equipped_to=CanonicalId(
                kind=EntityKind.WEAPON,
                key="12501",
            ),
        )


@pytest.mark.parametrize("level", [0, 91])
def test_weapon_rejects_invalid_level(level: int) -> None:
    with pytest.raises(ValueError, match="level"):
        Weapon(
            identity=weapon_id(),
            level=level,
            ascension=0,
            refinement=1,
            locked=False,
        )


@pytest.mark.parametrize("ascension", [-1, 7])
def test_weapon_rejects_invalid_ascension(ascension: int) -> None:
    with pytest.raises(ValueError, match="ascension"):
        Weapon(
            identity=weapon_id(),
            level=1,
            ascension=ascension,
            refinement=1,
            locked=False,
        )


@pytest.mark.parametrize("refinement", [0, 6])
def test_weapon_rejects_invalid_refinement(refinement: int) -> None:
    with pytest.raises(ValueError, match="refinement"):
        Weapon(
            identity=weapon_id(),
            level=1,
            ascension=0,
            refinement=refinement,
            locked=False,
        )


@pytest.mark.parametrize("locked", [0, 1, "true", None])
def test_weapon_rejects_non_boolean_locked_value(locked: object) -> None:
    with pytest.raises(ValueError, match="locked"):
        Weapon(
            identity=weapon_id(),
            level=1,
            ascension=0,
            refinement=1,
            locked=locked,  # type: ignore[arg-type]
        )

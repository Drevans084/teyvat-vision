import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.weapon import Weapon


def weapon_id(key: str = "11509") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.WEAPON,
        key=key,
    )


def character_id(key: str = "10000002") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def test_weapon_preserves_valid_account_state() -> None:
    weapon = Weapon(
        identity=weapon_id(),
        level=90,
        ascension=6,
        refinement=5,
        locked=True,
    )

    assert weapon.identity == weapon_id()
    assert weapon.level == 90
    assert weapon.ascension == 6
    assert weapon.refinement == 5
    assert weapon.locked is True


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


def test_weapon_rejects_non_weapon_identity() -> None:
    with pytest.raises(ValueError, match="weapon"):
        Weapon(
            identity=character_id(),
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

import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import WeaponType
from teyvat_vision.game_data.records import CharacterDefinition, WeaponDefinition


def test_character_definition_preserves_weapon_type() -> None:
    definition = CharacterDefinition(
        identity=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
        weapon_type=WeaponType.SWORD,
    )

    assert definition.weapon_type is WeaponType.SWORD


def test_weapon_definition_preserves_weapon_type() -> None:
    definition = WeaponDefinition(
        identity=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
        weapon_type=WeaponType.SWORD,
    )

    assert definition.weapon_type is WeaponType.SWORD


def test_character_definition_allows_unknown_weapon_type() -> None:
    definition = CharacterDefinition(
        identity=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
    )

    assert definition.weapon_type is None


def test_weapon_definition_allows_unknown_weapon_type() -> None:
    definition = WeaponDefinition(
        identity=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
    )

    assert definition.weapon_type is None


def test_character_definition_rejects_noncanonical_weapon_type() -> None:
    with pytest.raises(ValueError, match="weapon type"):
        CharacterDefinition(
            identity=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000047",
            ),
            weapon_type="sword",  # type: ignore[arg-type]
        )


def test_weapon_definition_rejects_noncanonical_weapon_type() -> None:
    with pytest.raises(ValueError, match="weapon type"):
        WeaponDefinition(
            identity=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            weapon_type="sword",  # type: ignore[arg-type]
        )

import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import Rarity
from teyvat_vision.game_data.records import CharacterDefinition, WeaponDefinition


def test_character_definition_preserves_rarity() -> None:
    definition = CharacterDefinition(
        identity=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
        rarity=Rarity.FIVE_STAR,
    )

    assert definition.rarity is Rarity.FIVE_STAR


def test_weapon_definition_preserves_rarity() -> None:
    definition = WeaponDefinition(
        identity=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
        rarity=Rarity.FIVE_STAR,
    )

    assert definition.rarity is Rarity.FIVE_STAR


def test_character_definition_allows_unknown_rarity() -> None:
    definition = CharacterDefinition(
        identity=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
    )

    assert definition.rarity is None


def test_weapon_definition_allows_unknown_rarity() -> None:
    definition = WeaponDefinition(
        identity=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
    )

    assert definition.rarity is None


def test_character_definition_rejects_raw_integer_rarity() -> None:
    with pytest.raises(ValueError, match="rarity"):
        CharacterDefinition(
            identity=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000047",
            ),
            rarity=5,  # type: ignore[arg-type]
        )


def test_weapon_definition_rejects_raw_integer_rarity() -> None:
    with pytest.raises(ValueError, match="rarity"):
        WeaponDefinition(
            identity=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            rarity=5,  # type: ignore[arg-type]
        )

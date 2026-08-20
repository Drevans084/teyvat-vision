from teyvat_vision.game_data.classification import Rarity, WeaponType


def test_weapon_type_sword_has_stable_value() -> None:
    assert WeaponType.SWORD.value == "sword"


def test_weapon_type_claymore_has_stable_value() -> None:
    assert WeaponType.CLAYMORE.value == "claymore"


def test_weapon_type_polearm_has_stable_value() -> None:
    assert WeaponType.POLEARM.value == "polearm"


def test_weapon_type_bow_has_stable_value() -> None:
    assert WeaponType.BOW.value == "bow"


def test_weapon_type_catalyst_has_stable_value() -> None:
    assert WeaponType.CATALYST.value == "catalyst"


def test_weapon_type_contains_only_supported_canonical_types() -> None:
    assert set(WeaponType) == {
        WeaponType.SWORD,
        WeaponType.CLAYMORE,
        WeaponType.POLEARM,
        WeaponType.BOW,
        WeaponType.CATALYST,
    }


def test_rarity_one_star_has_stable_value() -> None:
    assert Rarity.ONE_STAR.value == 1


def test_rarity_two_star_has_stable_value() -> None:
    assert Rarity.TWO_STAR.value == 2


def test_rarity_three_star_has_stable_value() -> None:
    assert Rarity.THREE_STAR.value == 3


def test_rarity_four_star_has_stable_value() -> None:
    assert Rarity.FOUR_STAR.value == 4


def test_rarity_five_star_has_stable_value() -> None:
    assert Rarity.FIVE_STAR.value == 5


def test_rarity_contains_only_supported_canonical_values() -> None:
    assert set(Rarity) == {
        Rarity.ONE_STAR,
        Rarity.TWO_STAR,
        Rarity.THREE_STAR,
        Rarity.FOUR_STAR,
        Rarity.FIVE_STAR,
    }


def test_rarity_is_not_interchangeable_with_raw_integer() -> None:
    assert Rarity.FIVE_STAR != 5

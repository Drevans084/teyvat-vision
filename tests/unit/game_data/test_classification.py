from teyvat_vision.game_data.classification import WeaponType


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

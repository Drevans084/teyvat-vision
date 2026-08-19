import pytest

from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.names import CustomName


def character_id(key: str = "10000002") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def test_character_preserves_valid_account_state() -> None:
    character = Character(
        identity=character_id(),
        level=90,
        ascension=6,
        constellation=2,
        talents=TalentLevels(
            normal=9,
            skill=10,
            burst=10,
        ),
    )

    assert character.identity == character_id()
    assert character.level == 90
    assert character.ascension == 6
    assert character.constellation == 2
    assert character.talents.normal == 9
    assert character.talents.skill == 10
    assert character.talents.burst == 10


def test_character_can_preserve_case_sensitive_custom_name() -> None:
    character = Character(
        identity=character_id(),
        level=90,
        ascension=6,
        constellation=6,
        talents=TalentLevels(
            normal=10,
            skill=10,
            burst=10,
        ),
        custom_name=CustomName("Traveler"),
    )

    assert character.custom_name == CustomName("Traveler")
    assert character.custom_name != CustomName("traveler")


def test_character_custom_name_is_optional() -> None:
    character = Character(
        identity=character_id(),
        level=1,
        ascension=0,
        constellation=0,
        talents=TalentLevels(
            normal=1,
            skill=1,
            burst=1,
        ),
    )

    assert character.custom_name is None


def test_character_rejects_non_character_identity() -> None:
    with pytest.raises(ValueError, match="character"):
        Character(
            identity=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            level=90,
            ascension=6,
            constellation=0,
            talents=TalentLevels(
                normal=1,
                skill=1,
                burst=1,
            ),
        )


@pytest.mark.parametrize("level", [0, 101])
def test_character_rejects_invalid_level(level: int) -> None:
    with pytest.raises(ValueError, match="level"):
        Character(
            identity=character_id(),
            level=level,
            ascension=0,
            constellation=0,
            talents=TalentLevels(
                normal=1,
                skill=1,
                burst=1,
            ),
        )


@pytest.mark.parametrize("ascension", [-1, 7])
def test_character_rejects_invalid_ascension(ascension: int) -> None:
    with pytest.raises(ValueError, match="ascension"):
        Character(
            identity=character_id(),
            level=1,
            ascension=ascension,
            constellation=0,
            talents=TalentLevels(
                normal=1,
                skill=1,
                burst=1,
            ),
        )


@pytest.mark.parametrize("constellation", [-1, 7])
def test_character_rejects_invalid_constellation(constellation: int) -> None:
    with pytest.raises(ValueError, match="constellation"):
        Character(
            identity=character_id(),
            level=1,
            ascension=0,
            constellation=constellation,
            talents=TalentLevels(
                normal=1,
                skill=1,
                burst=1,
            ),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("normal", 0),
        ("normal", 16),
        ("skill", 0),
        ("skill", 16),
        ("burst", 0),
        ("burst", 16),
    ],
)
def test_talent_levels_reject_invalid_values(field: str, value: int) -> None:
    values = {
        "normal": 1,
        "skill": 1,
        "burst": 1,
    }
    values[field] = value

    with pytest.raises(ValueError, match=field):
        TalentLevels(**values)

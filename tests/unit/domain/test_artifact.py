import pytest

from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId


def artifact_set_definition(key: str = "15001") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key=key,
    )


def artifact_id(
    key: str = "15001",
    *,
    instance_key: str = "artifact-000001",
) -> OwnedItemId:
    return OwnedItemId(
        definition=artifact_set_definition(key),
        instance_key=instance_key,
    )


def character_id(key: str = "10000002") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def test_stat_value_preserves_stat_key_and_value() -> None:
    stat = StatValue(
        key="critRate_",
        value=3.9,
    )

    assert stat.key == "critRate_"
    assert stat.value == 3.9


def test_stat_value_rejects_blank_key() -> None:
    with pytest.raises(ValueError, match="key"):
        StatValue(
            key="   ",
            value=3.9,
        )


def test_stat_value_rejects_surrounding_whitespace_in_key() -> None:
    with pytest.raises(ValueError, match="key"):
        StatValue(
            key=" critRate_ ",
            value=3.9,
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_stat_value_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        StatValue(
            key="critRate_",
            value=value,
        )


def test_artifact_preserves_valid_account_state() -> None:
    identity = artifact_id()

    artifact = Artifact(
        identity=identity,
        slot=ArtifactSlot.FLOWER,
        rarity=5,
        level=20,
        main_stat=StatValue(
            key="hp",
            value=4780.0,
        ),
        substats=(
            StatValue(key="critRate_", value=10.5),
            StatValue(key="critDMG_", value=21.8),
            StatValue(key="atk_", value=5.8),
            StatValue(key="enerRech_", value=11.0),
        ),
        locked=True,
    )

    assert artifact.identity == identity
    assert artifact.identity.definition == artifact_set_definition()
    assert artifact.slot is ArtifactSlot.FLOWER
    assert artifact.rarity == 5
    assert artifact.level == 20
    assert artifact.main_stat.key == "hp"
    assert len(artifact.substats) == 4
    assert artifact.locked is True


def test_two_artifacts_from_same_set_have_distinct_identity() -> None:
    first = Artifact(
        identity=artifact_id(instance_key="artifact-000001"),
        slot=ArtifactSlot.FLOWER,
        rarity=5,
        level=20,
        main_stat=StatValue(key="hp", value=4780.0),
        substats=(),
        locked=True,
    )
    second = Artifact(
        identity=artifact_id(instance_key="artifact-000002"),
        slot=ArtifactSlot.FLOWER,
        rarity=5,
        level=20,
        main_stat=StatValue(key="hp", value=4780.0),
        substats=(),
        locked=True,
    )

    assert first.identity.definition == second.identity.definition
    assert first.identity != second.identity


def test_artifact_can_be_equipped_to_character() -> None:
    owner = character_id()

    artifact = Artifact(
        identity=artifact_id(),
        slot=ArtifactSlot.PLUME,
        rarity=5,
        level=20,
        main_stat=StatValue(
            key="atk",
            value=311.0,
        ),
        substats=(),
        locked=False,
        equipped_to=owner,
    )

    assert artifact.equipped_to == owner


def test_artifact_can_be_unequipped() -> None:
    artifact = Artifact(
        identity=artifact_id(),
        slot=ArtifactSlot.SANDS,
        rarity=5,
        level=0,
        main_stat=StatValue(
            key="atk_",
            value=7.0,
        ),
        substats=(),
        locked=False,
    )

    assert artifact.equipped_to is None


def test_artifact_rejects_non_artifact_owned_item_identity() -> None:
    with pytest.raises(ValueError, match="artifact"):
        Artifact(
            identity=OwnedItemId(
                definition=CanonicalId(
                    kind=EntityKind.WEAPON,
                    key="11509",
                ),
                instance_key="weapon-000001",
            ),
            slot=ArtifactSlot.FLOWER,
            rarity=5,
            level=20,
            main_stat=StatValue(
                key="hp",
                value=4780.0,
            ),
            substats=(),
            locked=True,
        )


def test_artifact_rejects_non_character_equipment_owner() -> None:
    with pytest.raises(ValueError, match="equipped"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.FLOWER,
            rarity=5,
            level=20,
            main_stat=StatValue(
                key="hp",
                value=4780.0,
            ),
            substats=(),
            locked=True,
            equipped_to=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
        )


@pytest.mark.parametrize("rarity", [0, 6])
def test_artifact_rejects_invalid_rarity(rarity: int) -> None:
    with pytest.raises(ValueError, match="rarity"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.FLOWER,
            rarity=rarity,
            level=0,
            main_stat=StatValue(
                key="hp",
                value=717.0,
            ),
            substats=(),
            locked=False,
        )


@pytest.mark.parametrize("level", [-1, 21])
def test_artifact_rejects_invalid_level(level: int) -> None:
    with pytest.raises(ValueError, match="level"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.FLOWER,
            rarity=5,
            level=level,
            main_stat=StatValue(
                key="hp",
                value=717.0,
            ),
            substats=(),
            locked=False,
        )


@pytest.mark.parametrize("locked", [0, 1, "true", None])
def test_artifact_rejects_non_boolean_locked_value(locked: object) -> None:
    with pytest.raises(ValueError, match="locked"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.FLOWER,
            rarity=5,
            level=0,
            main_stat=StatValue(
                key="hp",
                value=717.0,
            ),
            substats=(),
            locked=locked,  # type: ignore[arg-type]
        )


def test_artifact_rejects_more_than_four_substats() -> None:
    with pytest.raises(ValueError, match="substats"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.FLOWER,
            rarity=5,
            level=20,
            main_stat=StatValue(
                key="hp",
                value=4780.0,
            ),
            substats=(
                StatValue(key="critRate_", value=3.9),
                StatValue(key="critDMG_", value=7.8),
                StatValue(key="atk_", value=5.8),
                StatValue(key="enerRech_", value=5.2),
                StatValue(key="def_", value=7.3),
            ),
            locked=False,
        )


def test_artifact_rejects_duplicate_substat_keys() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.FLOWER,
            rarity=5,
            level=20,
            main_stat=StatValue(
                key="hp",
                value=4780.0,
            ),
            substats=(
                StatValue(key="critRate_", value=3.9),
                StatValue(key="critRate_", value=7.8),
            ),
            locked=False,
        )


def test_artifact_rejects_main_stat_repeated_as_substat() -> None:
    with pytest.raises(ValueError, match="main stat"):
        Artifact(
            identity=artifact_id(),
            slot=ArtifactSlot.SANDS,
            rarity=5,
            level=20,
            main_stat=StatValue(
                key="atk_",
                value=46.6,
            ),
            substats=(StatValue(key="atk_", value=5.8),),
            locked=False,
        )

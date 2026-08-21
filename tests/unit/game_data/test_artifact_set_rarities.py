import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import Rarity
from teyvat_vision.game_data.records import ArtifactSetDefinition

ARTIFACT_SET_ID = CanonicalId(
    kind=EntityKind.ARTIFACT_SET,
    key="15001",
)


def test_artifact_set_defaults_to_unknown_rarities() -> None:
    definition = ArtifactSetDefinition(
        identity=ARTIFACT_SET_ID,
    )

    assert definition.rarities == ()


def test_artifact_set_preserves_single_rarity() -> None:
    definition = ArtifactSetDefinition(
        identity=ARTIFACT_SET_ID,
        rarities=(Rarity.FIVE_STAR,),
    )

    assert definition.rarities == (Rarity.FIVE_STAR,)


def test_artifact_set_preserves_multiple_rarities() -> None:
    definition = ArtifactSetDefinition(
        identity=ARTIFACT_SET_ID,
        rarities=(
            Rarity.FOUR_STAR,
            Rarity.FIVE_STAR,
        ),
    )

    assert definition.rarities == (
        Rarity.FOUR_STAR,
        Rarity.FIVE_STAR,
    )


def test_artifact_set_rejects_duplicate_rarity() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        ArtifactSetDefinition(
            identity=ARTIFACT_SET_ID,
            rarities=(
                Rarity.FIVE_STAR,
                Rarity.FIVE_STAR,
            ),
        )


def test_artifact_set_rejects_raw_integer_rarity() -> None:
    with pytest.raises(ValueError, match="canonical Rarity"):
        ArtifactSetDefinition(
            identity=ARTIFACT_SET_ID,
            rarities=(5,),  # type: ignore[arg-type]
        )

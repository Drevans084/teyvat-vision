import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.localization import LocalizedName
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)


def names() -> tuple[LocalizedName, ...]:
    return (
        LocalizedName(
            locale="en-US",
            value="English Name",
        ),
        LocalizedName(
            locale="ja-JP",
            value="日本語名",
        ),
    )


def test_character_definition_preserves_localized_names() -> None:
    localized_names = names()

    definition = CharacterDefinition(
        identity=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000002",
        ),
        names=localized_names,
    )

    assert definition.names == localized_names


def test_weapon_definition_preserves_localized_names() -> None:
    localized_names = names()

    definition = WeaponDefinition(
        identity=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
        names=localized_names,
    )

    assert definition.names == localized_names


def test_artifact_set_definition_preserves_localized_names() -> None:
    localized_names = names()

    definition = ArtifactSetDefinition(
        identity=CanonicalId(
            kind=EntityKind.ARTIFACT_SET,
            key="15001",
        ),
        names=localized_names,
    )

    assert definition.names == localized_names


def test_material_definition_preserves_localized_names() -> None:
    localized_names = names()

    definition = MaterialDefinition(
        identity=CanonicalId(
            kind=EntityKind.MATERIAL,
            key="104003",
        ),
        names=localized_names,
    )

    assert definition.names == localized_names


def test_character_definition_rejects_duplicate_name_locale() -> None:
    with pytest.raises(ValueError, match="duplicate locale"):
        CharacterDefinition(
            identity=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000002",
            ),
            names=(
                LocalizedName(
                    locale="en-US",
                    value="Kaedehara Kazuha",
                ),
                LocalizedName(
                    locale="en-US",
                    value="Kazuha",
                ),
            ),
        )


def test_weapon_definition_rejects_duplicate_name_locale() -> None:
    with pytest.raises(ValueError, match="duplicate locale"):
        WeaponDefinition(
            identity=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            names=(
                LocalizedName(
                    locale="en-US",
                    value="Freedom-Sworn",
                ),
                LocalizedName(
                    locale="en-US",
                    value="Freedom Sworn",
                ),
            ),
        )


def test_artifact_set_definition_rejects_duplicate_name_locale() -> None:
    with pytest.raises(ValueError, match="duplicate locale"):
        ArtifactSetDefinition(
            identity=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            names=(
                LocalizedName(
                    locale="en-US",
                    value="Gladiator's Finale",
                ),
                LocalizedName(
                    locale="en-US",
                    value="Gladiator Finale",
                ),
            ),
        )


def test_material_definition_rejects_duplicate_name_locale() -> None:
    with pytest.raises(ValueError, match="duplicate locale"):
        MaterialDefinition(
            identity=CanonicalId(
                kind=EntityKind.MATERIAL,
                key="104003",
            ),
            names=(
                LocalizedName(
                    locale="en-US",
                    value="Hero's Wit",
                ),
                LocalizedName(
                    locale="en-US",
                    value="Heroes Wit",
                ),
            ),
        )

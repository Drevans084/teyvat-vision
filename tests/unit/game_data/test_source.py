import pytest

from teyvat_vision.game_data.source import GameDataSource


def test_game_data_source_preserves_provider_and_version() -> None:
    source = GameDataSource(
        provider="anime-game-data",
        version="6.8",
    )

    assert source.provider == "anime-game-data"
    assert source.version == "6.8"
    assert source.revision is None


def test_game_data_source_preserves_optional_revision() -> None:
    source = GameDataSource(
        provider="anime-game-data",
        version="6.8",
        revision="abc123",
    )

    assert source.revision == "abc123"


@pytest.mark.parametrize(
    "provider",
    [
        "",
        "   ",
    ],
)
def test_game_data_source_rejects_blank_provider(provider: str) -> None:
    with pytest.raises(ValueError, match="provider"):
        GameDataSource(
            provider=provider,
            version="6.8",
        )


def test_game_data_source_rejects_provider_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="provider"):
        GameDataSource(
            provider=" anime-game-data ",
            version="6.8",
        )


@pytest.mark.parametrize(
    "version",
    [
        "",
        "   ",
    ],
)
def test_game_data_source_rejects_blank_version(version: str) -> None:
    with pytest.raises(ValueError, match="version"):
        GameDataSource(
            provider="anime-game-data",
            version=version,
        )


def test_game_data_source_rejects_version_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="version"):
        GameDataSource(
            provider="anime-game-data",
            version=" 6.8 ",
        )


@pytest.mark.parametrize(
    "revision",
    [
        "",
        "   ",
    ],
)
def test_game_data_source_rejects_blank_revision(revision: str) -> None:
    with pytest.raises(ValueError, match="revision"):
        GameDataSource(
            provider="anime-game-data",
            version="6.8",
            revision=revision,
        )


def test_game_data_source_rejects_revision_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="revision"):
        GameDataSource(
            provider="anime-game-data",
            version="6.8",
            revision=" abc123 ",
        )


def test_game_data_source_preserves_case() -> None:
    source = GameDataSource(
        provider="Provider-RC",
        version="6.8-RC1",
        revision="AbC123",
    )

    assert source.provider == "Provider-RC"
    assert source.version == "6.8-RC1"
    assert source.revision == "AbC123"

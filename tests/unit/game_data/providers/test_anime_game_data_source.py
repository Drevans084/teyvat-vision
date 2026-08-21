from pathlib import Path

from teyvat_vision.game_data.providers.anime_game_data import AnimeGameDataProvider


def test_anime_game_data_provider_preserves_root(
    tmp_path: Path,
) -> None:
    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0.0",
        revision="be8d439be0796208fa6533d7e9f3eefaa7ecab26",
    )

    assert provider.root == tmp_path


def test_anime_game_data_provider_reports_game_version(
    tmp_path: Path,
) -> None:
    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0.0",
        revision="be8d439be0796208fa6533d7e9f3eefaa7ecab26",
    )

    assert provider.version() == "7.0.0"


def test_anime_game_data_provider_owns_source_metadata(
    tmp_path: Path,
) -> None:
    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0.0",
        revision="be8d439be0796208fa6533d7e9f3eefaa7ecab26",
    )

    source = provider.source()

    assert source.provider == "Dimbreath/AnimeGameData2"
    assert source.version == "7.0.0"
    assert source.revision == "be8d439be0796208fa6533d7e9f3eefaa7ecab26"


def test_anime_game_data_provider_allows_unknown_revision(
    tmp_path: Path,
) -> None:
    provider = AnimeGameDataProvider(
        root=tmp_path,
        game_version="7.0.0",
    )

    source = provider.source()

    assert source.provider == "Dimbreath/AnimeGameData2"
    assert source.version == "7.0.0"
    assert source.revision is None

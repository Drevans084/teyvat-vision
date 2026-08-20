"""Provider-to-dataset loading boundary for static game data."""

from dataclasses import dataclass

from teyvat_vision.game_data.dataset import StaticGameData
from teyvat_vision.game_data.provider import GameDataProvider
from teyvat_vision.game_data.source import GameDataSource


@dataclass(frozen=True, slots=True)
class LoadedGameData:
    """Validated static game data together with its source metadata."""

    data: StaticGameData
    source: GameDataSource


def load_game_data(
    provider: GameDataProvider,
    source: GameDataSource,
) -> LoadedGameData:
    """Load one provider into validated canonical static game data."""

    provider_version = provider.version()

    if provider_version != source.version:
        raise ValueError("provider version does not match game data source version")

    data = StaticGameData(
        version=provider_version,
        characters=provider.characters(),
        weapons=provider.weapons(),
        artifact_sets=provider.artifact_sets(),
        materials=provider.materials(),
    )

    return LoadedGameData(
        data=data,
        source=source,
    )

"""Source metadata for normalized static game data."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameDataSource:
    """Identifies where one normalized static dataset originated."""

    provider: str
    version: str
    revision: str | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("provider must not be blank")

        if self.provider != self.provider.strip():
            raise ValueError("provider must not contain surrounding whitespace")

        if not self.version.strip():
            raise ValueError("version must not be blank")

        if self.version != self.version.strip():
            raise ValueError("version must not contain surrounding whitespace")

        if self.revision is not None:
            if not self.revision.strip():
                raise ValueError("revision must not be blank")

            if self.revision != self.revision.strip():
                raise ValueError("revision must not contain surrounding whitespace")

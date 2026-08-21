"""Provider-independent static game-data asset references."""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId


@dataclass(frozen=True, slots=True)
class GameDataAsset:
    """Associates one canonical game-data entity with an asset reference."""

    subject: CanonicalId
    reference: str

    def __post_init__(self) -> None:
        if not self.reference.strip():
            raise ValueError("reference must not be blank")

        if self.reference != self.reference.strip():
            raise ValueError("reference must not contain surrounding whitespace")

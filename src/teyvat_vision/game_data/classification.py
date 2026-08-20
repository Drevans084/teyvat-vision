"""Canonical static game-data classifications for Teyvat Vision."""

from enum import StrEnum


class WeaponType(StrEnum):
    """Canonical weapon classes used by characters and weapons."""

    SWORD = "sword"
    CLAYMORE = "claymore"
    POLEARM = "polearm"
    BOW = "bow"
    CATALYST = "catalyst"

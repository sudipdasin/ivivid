"""Explicit Free/Pro boundaries. Public builds never import private modules."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

PUBLIC_FEATURES: Tuple[str, ...] = (
    "igpu_detection", "mpv_preset_configuration", "shader_selection",
    "audio_filters", "local_settings",
)

@dataclass(frozen=True)
class Edition:
    name: str
    features: Tuple[str, ...]
    proprietary: bool = False

FREE = Edition("free", PUBLIC_FEATURES)


def describe_edition():
    """Free is the only edition shipped from this repository."""
    return FREE


def require_public_feature(feature: str) -> None:
    if feature not in PUBLIC_FEATURES:
        raise ValueError("Feature is not part of the public Free edition: " + feature)

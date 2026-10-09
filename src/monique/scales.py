"""Scales that give whole logical pixels for a monitor mode.

Hyprland (CMonitor::applyMonitorRule, 0.55) accepts a scale only when
``pixels / scale`` is a whole number on both axes. Any other value is
replaced by the nearest valid one in 1/120 steps, and Hyprland shows an
"invalid scale" notification on every config load. Fractional-scale
Wayland clients use the same 1/120 steps, so the list fits Sway and Niri
too.
"""

from __future__ import annotations

import math
import struct

SCALE_STEPS = 120
MIN_SCALE = 0.5
MAX_SCALE = 4.0


def _float32(value: float) -> float:
    """Round to C float, the type Hyprland keeps the scale in."""
    return struct.unpack("f", struct.pack("f", value))[0]


def is_clean_scale(width: int, height: int, scale: float) -> bool:
    """Return True if the mode divides into whole logical pixels."""
    if width <= 0 or height <= 0 or scale <= 0:
        return False
    return (width / scale).is_integer() and (height / scale).is_integer()


def clean_scales(
    width: int, height: int, lo: float = MIN_SCALE, hi: float = MAX_SCALE,
) -> list[float]:
    """Return every clean scale between ``lo`` and ``hi``, ascending."""
    first = math.ceil(lo * SCALE_STEPS)
    last = math.floor(hi * SCALE_STEPS)
    scales = [
        step / SCALE_STEPS
        for step in range(first, last + 1)
        if is_clean_scale(width, height, step / SCALE_STEPS)
    ]
    return scales or [1.0]


def nearest_clean_scale(width: int, height: int, scale: float) -> float:
    """Return the clean scale Hyprland would pick for ``scale``.

    Ties go to the larger scale, as in Hyprland's search.
    """
    if width <= 0 or height <= 0:
        return 1.0
    candidates = clean_scales(width, height, 1 / SCALE_STEPS, 10.0)
    return min(candidates, key=lambda s: (abs(s - scale), -s))


def format_scale(scale: float) -> str:
    """Format a scale so Hyprland reads back the same 1/120 step."""
    return f"{scale:g}"


def hyprland_keeps(width: int, height: int, text: str) -> bool:
    """Return True if Hyprland applies ``text`` without a warning.

    Mirrors the 0.55 check: the parsed float must divide the mode, or
    rounding it to 1/120 must.
    """
    scale = _float32(float(text))
    if is_clean_scale(width, height, scale):
        return True
    return is_clean_scale(width, height, round(scale * SCALE_STEPS) / SCALE_STEPS)

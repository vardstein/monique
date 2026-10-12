"""Modes a monitor really offers.

Hyprland, Sway and Niri list every mode a monitor supports. A width,
height or refresh outside that list makes Hyprland fall back to another
mode and warn on every config load, so Monique only saves listed modes
when the list is known.
"""

from __future__ import annotations

import re

_MODE_RE = re.compile(r"^\s*(\d+)x(\d+)@([0-9.]+)\s*(?:Hz)?\s*$")


def parse_mode(text: str) -> tuple[int, int, float] | None:
    """Parse ``WxH@R`` or ``WxH@R.RRHz`` into width, height and refresh."""
    match = _MODE_RE.match(text)
    if match is None:
        return None
    width, height, rate = match.groups()
    try:
        return int(width), int(height), round(float(rate), 3)
    except ValueError:
        return None


def nearest_mode_index(
    modes: list[str], width: int, height: int, refresh: float,
) -> int | None:
    """Return the listed mode closest to ``width``x``height``@``refresh``.

    The size must match; among modes of that size the nearest refresh
    wins. Without a mode of that size, the first listed mode (the one the
    monitor prefers) is used. ``None`` when no mode can be parsed.
    """
    parsed = [(i, parse_mode(m)) for i, m in enumerate(modes)]
    parsed = [(i, p) for i, p in parsed if p is not None]
    if not parsed:
        return None
    same_size = [(i, p) for i, p in parsed if p[0] == width and p[1] == height]
    if not same_size:
        return parsed[0][0]
    return min(same_size, key=lambda item: abs(item[1][2] - refresh))[0]

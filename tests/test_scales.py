"""Monique must offer only scales Hyprland applies without a warning."""

from __future__ import annotations

import pytest

from monique.scales import (
    clean_scales,
    format_scale,
    hyprland_keeps,
    is_clean_scale,
    nearest_clean_scale,
)

MODES = [
    (2256, 1504),  # Framework 13
    (1920, 1080),
    (2560, 1440),
    (3840, 2160),
    (1366, 768),
    (2880, 1920),
]


@pytest.mark.parametrize(("width", "height"), MODES)
def test_every_offered_scale_survives_the_config_round_trip(width, height):
    scales = clean_scales(width, height)
    assert 1.0 in scales
    for scale in scales:
        assert hyprland_keeps(width, height, format_scale(scale)), scale


def test_framework_13_has_no_clean_1_5_or_2_2():
    scales = clean_scales(2256, 1504)
    assert 1.5 not in scales
    assert 2.2 not in scales
    assert not hyprland_keeps(2256, 1504, "2.2")
    assert 2.0 in scales and 2.35 in scales


def test_nearest_matches_hyprland_suggestion():
    # 2.2 on the FW13: 2.35 is 18 steps up, 2.0 is 24 down; Hyprland picks 2.35.
    assert nearest_clean_scale(2256, 1504, 2.2) == 2.35
    # 2.2 on 1080p: 2.0 and 2.4 are both 24 steps away; Hyprland searches up first.
    assert nearest_clean_scale(1920, 1080, 2.2) == 2.4
    assert nearest_clean_scale(1920, 1080, 1.25) == 1.25


def test_clean_scale_gives_whole_logical_pixels():
    assert is_clean_scale(2256, 1504, 2.35)
    assert (2256 / 2.35, 1504 / 2.35) == (960.0, 640.0)
    assert not is_clean_scale(0, 1080, 1.0)


def test_unknown_mode_falls_back_to_1():
    assert clean_scales(0, 0) == [1.0]
    assert nearest_clean_scale(0, 0, 2.2) == 1.0

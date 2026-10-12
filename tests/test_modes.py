"""Monique must save only modes the monitor lists."""

from __future__ import annotations

from monique.models import MonitorConfig, ResolutionMode
from monique.modes import nearest_mode_index, parse_mode

# hyprctl monitors -j availableModes style, preferred mode first
HYPR_MODES = [
    "3840x2160@60.00Hz",
    "3840x2160@48.00Hz",
    "2560x1440@60.00Hz",
    "1920x1080@60.00Hz",
]


def test_parse_hyprland_sway_and_bare_modes():
    assert parse_mode("3840x2160@60.00Hz") == (3840, 2160, 60.0)
    assert parse_mode("2256x1504@59.999Hz") == (2256, 1504, 59.999)
    assert parse_mode("1920x1080@60") == (1920, 1080, 60.0)
    assert parse_mode("preferred") is None
    assert parse_mode("") is None


def test_nearest_mode_keeps_size_and_picks_closest_refresh():
    assert nearest_mode_index(HYPR_MODES, 3840, 2160, 59.997) == 0
    assert nearest_mode_index(HYPR_MODES, 3840, 2160, 50.0) == 1
    assert nearest_mode_index(HYPR_MODES, 1920, 1080, 60.0) == 3


def test_refresh_out_of_range_moves_to_listed_rate():
    # The field's 600 maximum ended up in monitors.conf as @600.
    assert nearest_mode_index(HYPR_MODES, 3840, 2160, 600.0) == 0


def test_unlisted_size_falls_back_to_preferred_mode():
    assert nearest_mode_index(HYPR_MODES, 3000, 2000, 60.0) == 0


def test_no_list_means_no_change():
    assert nearest_mode_index([], 3840, 2160, 600.0) is None
    assert nearest_mode_index(["garbage"], 3840, 2160, 600.0) is None


def test_saved_profile_with_bad_refresh_is_snapped():
    monitor = MonitorConfig.from_dict({
        "name": "eDP-1",
        "width": 3840,
        "height": 2160,
        "refresh_rate": 600.0,
        "resolution_mode": "explicit",
        "available_modes": HYPR_MODES,
    })
    assert (monitor.width, monitor.height, monitor.refresh_rate) == (3840, 2160, 60.0)
    assert "  mode = 3840x2160@60\n" in monitor.to_hyprland_v2_block()


def test_profile_without_mode_list_is_left_alone():
    monitor = MonitorConfig.from_dict({
        "name": "HEADLESS-1",
        "width": 1234,
        "height": 567,
        "refresh_rate": 75.0,
        "resolution_mode": "explicit",
        "available_modes": [],
    })
    assert (monitor.width, monitor.height, monitor.refresh_rate) == (1234, 567, 75.0)


def test_non_explicit_mode_is_left_alone():
    monitor = MonitorConfig.from_dict({
        "name": "DP-1",
        "width": 1,
        "height": 1,
        "refresh_rate": 600.0,
        "resolution_mode": ResolutionMode.PREFERRED.value,
        "available_modes": HYPR_MODES,
    })
    assert monitor.refresh_rate == 600.0

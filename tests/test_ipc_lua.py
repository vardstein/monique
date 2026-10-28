"""Hyprland with a Lua config takes Lua over IPC, not hyprlang keywords."""

import pytest

from monique.hyprland import HyprlandIPC


class FakeIPC(HyprlandIPC):
    """Records what would go over the socket and answers like Hyprland."""

    def __init__(self, eval_reply: str) -> None:
        super().__init__()
        self.eval_reply = eval_reply
        self.sent: list[str] = []

    def command(self, cmd: str) -> str:
        self.sent.append(cmd)
        if cmd.startswith("eval "):
            return self.eval_reply
        return "ok"


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("ok", True),
        ("eval is only supported with the lua config manager", False),
        ("unknown request", False),
    ],
)
def test_lua_mode_follows_the_eval_reply(reply, expected):
    ipc = FakeIPC(reply)
    assert ipc.uses_lua is expected
    assert ipc.uses_lua is expected
    assert ipc.sent == ["eval do end"]


def test_lua_config_moves_workspaces_with_the_lua_dispatcher():
    ipc = FakeIPC("ok")
    ipc.move_workspace_to_monitor("2", "DP-1")
    assert ipc.sent[-1] == (
        'dispatch hl.dsp.workspace.move({ workspace = "2", monitor = "DP-1" })'
    )


def test_lua_dispatch_quotes_names():
    ipc = FakeIPC("ok")
    ipc.move_workspace_to_monitor('a"b', "DP-1\\")
    assert ipc.sent[-1] == (
        'dispatch hl.dsp.workspace.move({ workspace = "a\\"b", monitor = "DP-1\\\\" })'
    )


def test_hyprlang_config_keeps_the_old_dispatcher():
    ipc = FakeIPC("eval is only supported with the lua config manager")
    ipc.move_workspace_to_monitor("2", "DP-1")
    assert ipc.sent[-1] == "dispatch moveworkspacetomonitor 2 DP-1"

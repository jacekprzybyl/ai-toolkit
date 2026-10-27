# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
"""MCP refresh preserves explicit user policy only for the same connection."""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from mcp_editors import install_servers  # noqa: E402


POLICY = {
    "default_tools_approval_mode": "approve",
    "enabled_tools": ["search", "read"],
    "disabled_tools": ["delete"],
    "tools": {"search": {"approval_mode": "prompt"}},
}


def _install(target: Path, server: dict) -> dict:
    path = install_servers(
        ["codex"], {"docs": server}, scope="project", project_dir=target
    )[0]
    return tomllib.loads(path.read_text())["mcp_servers"]["docs"]


@pytest.mark.parametrize("managed", [True, False])
def test_refresh_preserves_user_policy_for_same_connection(tmp_path: Path, managed: bool) -> None:
    server = {"url": "https://example.invalid/mcp"}
    _install(tmp_path, {**server, **POLICY})
    if not managed:
        path = tmp_path / ".codex/config.toml"
        path.write_text("\n".join(line for line in path.read_text().splitlines() if not line.startswith("#")))

    actual = _install(tmp_path, {**server, "tool_timeout_sec": 60})

    assert all(actual[key] == value for key, value in POLICY.items())
    assert actual["tool_timeout_sec"] == 60


def test_refresh_honors_explicit_policy_replacement(tmp_path: Path) -> None:
    server = {"url": "https://example.invalid/mcp"}
    _install(tmp_path, {**server, **POLICY})

    actual = _install(tmp_path, {
        **server, "default_tools_approval_mode": "prompt",
        "enabled_tools": [], "tools": {},
    })

    assert actual["default_tools_approval_mode"] == "prompt"
    assert actual["enabled_tools"] == []
    assert actual.get("tools", {}) == {}
    assert actual["disabled_tools"] == ["delete"]


def test_refresh_keeps_disabled_server_with_empty_connection_options(tmp_path: Path) -> None:
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '[mcp_servers.docs]\ncommand = "python3"\nargs = []\nenv = {}\n'
        'scopes = []\nenabled = false\nenabled_tools = []\n'
    )

    actual = _install(tmp_path, {"command": "python3", "args": [], "env": {}, "scopes": []})

    assert actual["enabled"] is False
    assert actual["enabled_tools"] == []


@pytest.mark.parametrize("connection", [
    {"url": "https://other.invalid/mcp"},
    {"url": "https://example.invalid/mcp", "http_headers": {"X-Account": "other"}},
    {"command": "python3", "args": ["server.py"]},
])
def test_refresh_does_not_transfer_approval_to_changed_connection(tmp_path: Path, connection: dict) -> None:
    _install(tmp_path, {"url": "https://example.invalid/mcp", **POLICY})

    actual = _install(tmp_path, connection)

    assert not set(POLICY).intersection(actual)

# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
"""Unit tests for the stable-read signature in scripts/install_steps/install_state.py.

Run: npm run test:py (pytest, config in pytest.ini).
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from install_steps import install_state  # noqa: E402


def _metadata(ctime_ns: int) -> SimpleNamespace:
    return SimpleNamespace(st_dev=1, st_ino=2, st_mode=0o100644, st_size=3,
                           st_mtime_ns=4, st_ctime_ns=ctime_ns)


def test_windows_signature_ignores_a_tunneled_creation_time(monkeypatch: pytest.MonkeyPatch) -> None:
    # NTFS reports one creation time for the directory entry and another for
    # the open handle after a rename-over write; the state file is unchanged.
    monkeypatch.setattr(install_state.os, "name", "nt")

    by_name = install_state._state_file_signature(_metadata(5))
    by_handle = install_state._state_file_signature(_metadata(6))

    assert by_name == by_handle


def test_posix_signature_still_detects_an_inode_change(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(install_state.os, "name", "posix")

    before = install_state._state_file_signature(_metadata(5))
    after = install_state._state_file_signature(_metadata(6))

    assert before != after

# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
"""Pair equivalent global/local advisory hooks without suppressing repeat calls.

Exit zero only for a duplicate from the opposite layer. Every uncertainty runs
the hook normally. No payload text is persisted, only hashes and source labels.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time

MAX_PENDING = 128
LOCK_ATTEMPTS = 10
MAX_RECORD_BYTES = 64 * 1024
MAX_RECORD_AGE = 7 * 24 * 60 * 60
MAX_CLEANUP_ENTRIES = 256
MAINTENANCE_SECONDS = 0.1
MAX_RUNTIME_ENTRIES = 128
MAX_RUNTIME_FILES = 64
MAX_RUNTIME_BYTES = 1024 * 1024
RECORD_NAME = re.compile(r"[0-9a-f]{24}-[0-9a-f]{64}\.json")
EVENTS = {"UserPromptSubmit", "SubagentStart", "SubagentStop", "Stop", "PostToolUse"}


def invocation_key(payload: dict[str, object]) -> str | None:
    event = payload.get("hook_event_name")
    required = ["session_id", "turn_id"]
    if not isinstance(event, str) or event not in EVENTS:
        return None
    if event in {"SubagentStart", "SubagentStop"}:
        required.append("agent_id")
    if event == "PostToolUse":
        required.append("tool_use_id")
    if any(not isinstance(payload.get(key), str) or not payload[key] for key in required):
        return None
    # Layer-specific opt-outs/output modes are distinct behavior even when the
    # installed scripts are byte-identical.
    environment = {key: value for key, value in os.environ.items()
                   if key.startswith(("AI_TOOLKIT_", "TOOLKIT_HOOK_"))
                   or key in {"CLAUDE_SKIP_SEARCH_FIRST", "CLAUDE_SEARCH_PROVIDER",
                              "CLAUDE_PROJECT_DIR", "CODEX_THREAD_ID"}}
    encoded = json.dumps([payload, environment], sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def open_state_directory() -> int:
    """Create private state without following symlinks below the user's home."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(Path.home().resolve(), flags)
    try:
        for name in (".softspark", "ai-toolkit", "state", "codex-hook-dedup"):
            try:
                os.mkdir(name, mode=0o700, dir_fd=descriptor)
            except FileExistsError:
                pass
            child = os.open(name, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def runtime_assets(script: Path, deadline: float) -> list[Path]:
    """Never enumerate an unbounded directory just to avoid duplicate output."""
    paths = []
    with os.scandir(script.parent) as entries:
        for index, entry in enumerate(entries):
            if index >= MAX_RUNTIME_ENTRIES or time.monotonic() >= deadline:
                raise ValueError("hook runtime enumeration budget exceeded")
            if Path(entry.name).suffix not in {".sh", ".py"}:
                continue
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ValueError("unverified hook asset")
            paths.append(Path(entry.path))
            if len(paths) > MAX_RUNTIME_FILES:
                raise ValueError("hook runtime file budget exceeded")
    return sorted(paths)


def runtime_digest(script: Path) -> str:
    """Hash bounded runtime data; uncertainty falls back to normal execution."""
    deadline = time.monotonic() + MAINTENANCE_SECONDS
    digest = hashlib.sha256()
    remaining = MAX_RUNTIME_BYTES
    for path in runtime_assets(script, deadline):
        if time.monotonic() >= deadline:
            raise ValueError("hook runtime time budget exceeded")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as asset:
            metadata = os.fstat(asset.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > remaining:
                raise ValueError("hook runtime byte budget exceeded")
            content = asset.read(remaining + 1)
        remaining -= len(content)
        if remaining < 0:
            raise ValueError("hook runtime byte budget exceeded")
        digest.update(path.name.encode() + b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def lock_record(descriptor: int) -> bool:
    """Bound contention instead of letting an advisory hook wait indefinitely."""
    import fcntl

    for attempt in range(LOCK_ATTEMPTS):
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            if attempt < LOCK_ATTEMPTS - 1:
                time.sleep(0.01)
    return False


def pair_invocation(descriptor: int, key: str, source: str) -> bool:
    """A same-source invocation always runs; one opposite-source copy skips."""
    with os.fdopen(descriptor, "r+", encoding="utf-8") as state:
        if not lock_record(state.fileno()):
            return False
        raw = state.read(MAX_RECORD_BYTES)
        pending = json.loads(raw) if raw else {}
        if not isinstance(pending, dict):
            return False
        prior = pending.pop(key, None)
        duplicate = isinstance(prior, str) and prior in {"global", "local"} and prior != source
        if not duplicate:
            pending[key] = source
        while len(pending) > MAX_PENDING:
            pending.pop(next(iter(pending)))
        state.seek(0)
        json.dump(pending, state)
        state.truncate()
        return duplicate


def session_prefix(session: str) -> str:
    return hashlib.sha256(session.encode()).hexdigest()[:24] + "-"


def safe_record(metadata: os.stat_result) -> bool:
    return (stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
            and metadata.st_uid == os.getuid() and metadata.st_size <= MAX_RECORD_BYTES)


def clean_session(payload: dict[str, object]) -> None:
    """Best-effort bounded cleanup of ephemeral records, never audit files."""
    session = payload.get("session_id")
    if not isinstance(session, str) or not session:
        return
    directory = open_state_directory()
    deadline = time.monotonic() + MAINTENANCE_SECONDS
    try:
        with os.scandir(directory) as entries:
            for index, entry in enumerate(entries):
                if index >= MAX_CLEANUP_ENTRIES or time.monotonic() >= deadline:
                    break
                if not RECORD_NAME.fullmatch(entry.name):
                    continue
                try:
                    metadata = entry.stat(follow_symlinks=False)
                    expired = metadata.st_mtime < time.time() - MAX_RECORD_AGE
                    if safe_record(metadata) and (entry.name.startswith(session_prefix(session)) or expired):
                        os.unlink(entry.name, dir_fd=directory)
                except FileNotFoundError:
                    pass
    finally:
        os.close(directory)


def is_duplicate(script: Path, payload: dict[str, object]) -> bool:
    key = invocation_key(payload)
    source = {"ai-toolkit-hooks": "global", "hooks": "local"}.get(script.parent.name)
    if key is None or source is None:
        return False
    identity = f"{payload['session_id']}:{payload['hook_event_name']}:{script.name}:{runtime_digest(script)}"
    filename = session_prefix(str(payload["session_id"])) + hashlib.sha256(identity.encode()).hexdigest() + ".json"
    directory = open_state_directory()
    try:
        try:
            descriptor = os.open(filename, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 mode=0o600, dir_fd=directory)
        except FileExistsError:
            descriptor = os.open(filename, os.O_RDWR | os.O_NOFOLLOW, dir_fd=directory)
        if not safe_record(os.fstat(descriptor)):
            os.close(descriptor)
            return False
        return pair_invocation(descriptor, key, source)
    finally:
        os.close(directory)


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        if isinstance(data, dict) and sys.argv[1:] == ["--cleanup"]:
            clean_session(data)
            duplicate = False
        else:
            duplicate = isinstance(data, dict) and is_duplicate(Path(sys.argv[1]), data)
    except (OSError, ValueError, AttributeError, ImportError, IndexError):
        duplicate = False
    sys.exit(0 if duplicate else 1)

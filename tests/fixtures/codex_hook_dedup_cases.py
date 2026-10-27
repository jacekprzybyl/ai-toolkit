# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
"""Exercise generated hooks from both config layers using isolated HOME."""
from __future__ import annotations

import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys

root, toolkit = map(Path, sys.argv[1:])
sys.path.insert(0, str(toolkit / "scripts"))
from generate_codex_hooks import generate  # noqa: E402

home, project = root / "home", root / "project"
home.mkdir()
project.mkdir()
generate(home, global_install=True, codex_home=home / ".codex")
generate(project, global_install=False)
environment = {
    **os.environ, "HOME": str(home), "USERPROFILE": str(home),
    "CODEX_HOME": str(home / ".codex"), "TOOLKIT_HOOK_PROFILE": "standard",
    "AI_TOOLKIT_DISABLED_HOOKS": "", "AI_TOOLKIT_SEARCH_FIRST": "strict",
}
assets = [home / ".codex/ai-toolkit-hooks", project / ".codex/hooks"]
payload = {"session_id": "session", "turn_id": "turn", "agent_id": "agent",
           "agent_type": "reviewer", "hook_event_name": "SubagentStart"}


def invoke(layer: int, data: dict[str, object], name: str = "subagent-start.sh",
           overrides: dict[str, str] | None = None) -> str:
    result = subprocess.run(["bash", str(assets[layer] / name)],
                            input=json.dumps(data), env={**environment, **(overrides or {})}, text=True,
                            capture_output=True, check=True)
    return result.stdout


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(lambda layer: invoke(layer, payload), range(2)))
assert sum(bool(output.strip()) for output in results) == 1, results

# A later invocation from the same layer must still execute; missing stable
# identity must never suppress a hook, and another agent is independent.
assert invoke(0, {**payload, "turn_id": "repeat"})
assert invoke(0, {**payload, "turn_id": "repeat"})
assert not invoke(1, {**payload, "turn_id": "repeat"})
for layer in range(2):
    assert invoke(layer, {key: value for key, value in payload.items() if key != "turn_id"})
    assert invoke(layer, {**payload, "agent_id": f"agent-{layer}"})
profile = {**payload, "turn_id": "different-profile"}
assert not invoke(0, profile, overrides={"TOOLKIT_HOOK_PROFILE": "minimal"})
assert invoke(1, profile)

# Versions with distinct behavior must not suppress one another.
local = assets[1] / "subagent-start.sh"
original = local.read_text()
local.write_text(original.replace("SubagentStart:", "SubagentStart local-extra:"))
different = {**payload, "turn_id": "different-version"}
assert invoke(0, different)
assert "local-extra" in invoke(1, different)
local.write_text(original)

# Both Stop hooks can race over the same flag. Exactly one may continue the
# turn, and it must retain the original prompt rather than an empty preview.
state = home / ".softspark/ai-toolkit/state"
state.mkdir(parents=True, exist_ok=True)
(state / "search-required-session.flag").write_text("0\nInvestigate the failing test\n")
stop = {"session_id": "session", "turn_id": "stop-turn", "hook_event_name": "Stop"}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    outputs = list(pool.map(lambda layer: invoke(layer, stop, "codex-stop-search-check.sh"), range(2)))
decisions = [json.loads(output) for output in outputs if output.strip()]
assert len(decisions) == 1, outputs
assert "Investigate the failing test" in decisions[0]["reason"], decisions

# SessionEnd cleans only its own dedup state; unrelated recent sessions and
# audit files remain. Abandoned dedup records expire after seven days.
records = state / "codex-hook-dedup"
before_other = set(records.iterdir())
assert invoke(0, {**payload, "session_id": "other-session"})
other_records = set(records.iterdir()) - before_other
assert other_records
audit = records / "audit.log"
audit.write_text("retain audit evidence")
invoke(0, {"session_id": "session"}, "session-end.sh")
assert set(records.iterdir()) == other_records | {audit}
for record in other_records | {audit}:
    os.utime(record, (0, 0))
invoke(0, {"session_id": "finished-session"}, "session-end.sh")
assert set(records.iterdir()) == {audit}

# A replaced or hardlinked state record cannot cause a skip or be overwritten.
assert invoke(0, {**payload, "session_id": "linked-state"})
record = next(path for path in records.iterdir() if path != audit)
contents = record.read_bytes()
backup = root / "linked-record-backup"
os.link(record, backup)
assert invoke(1, {**payload, "session_id": "linked-state"})
assert record.read_bytes() == contents == backup.read_bytes()

# Cleanup is best effort within the native SessionEnd budget, even with a large
# abandoned state directory. It must leave remaining records for later passes.
for index in range(3000):
    old = records / ("a" * 24 + "-" + f"{index:064x}" + ".json")
    old.write_text("{}")
    os.utime(old, (0, 0))
invoke(0, {"session_id": "bounded-cleanup"}, "session-end.sh")
assert any(path.name.startswith("a" * 24 + "-") for path in records.iterdir())

# Oversized runtime assets must fall back to executing both hooks normally.
for directory in assets:
    (directory / "large-custom-helper.py").write_bytes(b"#" * (2 * 1024 * 1024))
large = {**payload, "turn_id": "oversized-runtime"}
assert invoke(0, large)
assert invoke(1, large)
for directory in assets:
    (directory / "large-custom-helper.py").rename(directory / "large-custom-helper.fixture")
    for index in range(64):
        (directory / f"custom-helper-{index}.py").write_text("# user runtime helper\n")
many = {**payload, "turn_id": "many-runtime-files"}
assert invoke(0, many)
assert invoke(1, many)

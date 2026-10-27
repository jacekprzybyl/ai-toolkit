#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
"""Check parent-signal forwarding using only isolated fake account clients."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
NODE = shutil.which("node")
FAKE_CLIENT = '''#!/usr/bin/env python3
import os
from pathlib import Path
import signal
import time
root = Path(os.environ["SIGNAL_FIXTURE_ROOT"])
def stop(signum, _frame):
    (root / "received").write_text(str(signum))
    raise SystemExit(128 + signum)
def interrupt(_signum, _frame):
    with (root / "interrupts").open("a") as stream:
        stream.write("interrupt\\n")
signal.signal(signal.SIGHUP, stop)
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, interrupt)
(root / "ready").write_text(str(os.getpid()))
time.sleep(20)
'''


@unittest.skipUnless(os.name == "posix" and NODE, "POSIX signals and node required")
class AccountSwitchSignalTests(unittest.TestCase):
    def test_parent_shutdown_reaches_client_and_wrapper_reaps_it(self) -> None:
        for client in ("claude", "codex"):
            for signum in (signal.SIGHUP, signal.SIGTERM):
                with self.subTest(client=client, signum=signum):
                    self.check_shutdown(client, signum)

    def check_shutdown(self, client: str, signum: int) -> None:
        with tempfile.TemporaryDirectory(prefix="toolkit-signal-test-") as directory:
            root = Path(directory)
            env = self.prepare_client(root, client)
            process = subprocess.Popen(
                [str(NODE), str(ROOT / "bin/ai-toolkit.js"), f"{client}-switch", "run"],
                cwd=root, env=env, start_new_session=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
            try:
                deadline = time.monotonic() + 5
                while not (root / "ready").exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue((root / "ready").exists(), "fake client did not start")
                os.killpg(process.pid, signal.SIGINT)
                time.sleep(0.15)
                self.assertIsNone(process.poll(), "wrapper exited before its client")
                self.assertEqual((root / "interrupts").read_text(), "interrupt\n")
                process.send_signal(signum)
                _, error = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 128 + signum, error.decode())
                self.assertEqual((root / "received").read_text(), str(signum))
                with self.assertRaises(ProcessLookupError):
                    os.kill(int((root / "ready").read_text()), 0)
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.communicate(timeout=5)

    def prepare_client(self, root: Path, client: str) -> dict[str, str]:
        binary = root / "bin"
        binary.mkdir()
        executable = binary / client
        executable.write_text(FAKE_CLIENT)
        executable.chmod(0o755)
        config = root / "switch.json"
        config.write_text(json.dumps({
            "version": 1, "default": "default", "accounts": {"default": None}, "projects": {},
        }))
        env = {key: value for key, value in os.environ.items() if key not in {
            "CLAUDE_CONFIG_DIR", "CLAUDE_SECURESTORAGE_CONFIG_DIR", "CODEX_HOME",
            "CODEX_SQLITE_HOME", "SOFTSPARK_HOME", "CLAUDE_SWITCH_CONFIG", "CODEX_SWITCH_CONFIG",
        }}
        env.update(HOME=str(root), USERPROFILE=str(root), AI_TOOLKIT_HOME=str(root / "data"),
                   SIGNAL_FIXTURE_ROOT=str(root), PATH=str(binary) + os.pathsep + env["PATH"])
        env[f"{client.upper()}_SWITCH_CONFIG"] = str(config)
        return env


if __name__ == "__main__":
    unittest.main()

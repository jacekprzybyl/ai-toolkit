---
title: "Claude Teammates Wait at Startup or Remain Idle"
category: troubleshooting
service: ai-toolkit
tags: [claude-code, teammates, subagents, tmux, permissions, startup]
created: "2026-10-27"
last_updated: "2026-10-27"
description: "Distinguish hidden startup consent, idle teammates and stuck shell waits without approving prompts or terminating unrelated sessions."
---

# Claude Teammates Wait at Startup or Remain Idle

## Symptoms and confirmed cause

A split-pane teammate has a live process but produces no work or messages.
Messages in its inbox remain unread. A confirmed cause on Claude Code 2.1.311
was the startup dialog **Allow external CLAUDE.md file imports?** in every
teammate pane. The teammates had not reached their assigned tasks.

The lead started at a repository root, whose `CLAUDE.md` imported `@AGENTS.md`.
Teammates started in module subdirectories. The imported root file was outside
their working directories and therefore required external-import consent, even
though it was in the same repository. General workspace trust and external-import
consent are separate decisions. A switched Claude profile can also have different
recorded consent from the original profile.

This is a startup approval wait, not evidence of a model or MCP deadlock. An idle
process is not itself a failure: a teammate remains addressable after its turn.

## Inspect without changing the session

1. Identify the effective configuration directory. Use `CLAUDE_CONFIG_DIR` when
   set; with toolkit account routing, inspect `ai-toolkit claude-switch status
   --json`. Do not assume the relevant data is under `~/.claude`.
2. Read `teams/session-<prefix>/config.json` in that directory. Match the lead
   session, teammate names, working directories and tmux pane IDs. Treat these
   files as runtime state; do not edit them.
3. Inspect the exact teammate pane. A process command line can show which tmux
   socket the lead created. Replace the example socket and pane with observed
   values:

   ```bash
   tmux -L <observed-socket> list-panes -a -F '#{pane_id} #{pane_pid} #{pane_dead} #{pane_current_command}'
   tmux -L <observed-socket> capture-pane -p -t <observed-pane> -S -60
   ```

4. Classify the last visible state: startup trust/import dialog, permission
   request, active tool call, API failure, or finished/idle. Record the session,
   timestamp and waiting reason. Redact private prompts and credentials before
   sharing captured output. Unread inbox entries support a startup-wait diagnosis
   but do not prove it without the pane or transcript evidence.
5. Recheck that the process and pane still belong to this session before any
   recovery action. A closed socket means the earlier observation is historical.

In-process teammates can be inspected from the lead's agent panel instead.
Read the selected teammate's transcript; do not infer readiness from a row alone.

## Recovery and prevention

- For an external-import dialog, show the user the exact imported path and let
  them decide. Review the file and any nested imports first. Do not press approval
  keys, copy trust flags from another profile, or change permissions automatically.
- Prefer starting the lead and teammates at the same already-trusted repository
  root. Assign `app/api/` or `app/frontend/` as file ownership, and scope commands
  to those paths. This keeps the root `@AGENTS.md` inside the startup directory;
  other external imports can still require consent.
- After spawning, confirm startup before waiting for results. Do not start more
  teammates as a workaround for an unseen consent dialog.
- After collecting the final report, send a native teammate shutdown request and
  check its result. `TaskStop` cancellation of an ordinary background subagent is
  a different lifecycle operation. A teammate may finish its current request or
  tool call before shutdown. Do not kill another session's tmux server.

Updating toolkit hooks replaces the two exact older toolkit idle reminders,
including untagged copies left by Claude settings rewrites. Customized commands,
matchers and groups containing additional user handlers are preserved. If a
preserved custom reminder still advises `TaskStop` for a teammate, review that
local customization separately.

## Shell waits that match themselves

A separate source of indefinite waits is a shell loop such as
`until ! pgrep -f 'runtime-tests'; do sleep 5; done`. The shell's own command line
contains the searched string, so `pgrep -f` can keep matching the waiting shell
after the real test process has exited. Two identical waiters can match each
other as well.

Inspect PID, PPID, elapsed time and full command lines to establish this condition.
Do not launch another copy of the loop as a diagnostic. Prefer the original tool
task's completion result or a captured child PID and bounded wait. Keep separate
the test process exit, its output file and the waiting shell's state. Stop only a
confirmed, owned waiter after approval; retain its output and audit evidence.

## Account wrapper termination

Before this fix, `ai-toolkit claude-switch` and `codex-switch` used a synchronous
Node child wait. Sending `SIGHUP` or `SIGTERM` only to the wrapper could terminate
the wrapper without delivering the signal to its client. An isolated fake-client
test reproduces that leak for both account commands. The wrapper now forwards
those shutdown signals and waits for the client to exit, preserving its exit
code or signal-derived status. Terminal `SIGINT` already reaches the shared
process group, so the wrapper waits without sending a duplicate interrupt.

This explains one way a client can outlive its launcher; it does not establish
which signal an IDE delivered to an already-orphaned process. Updating the
wrapper affects new launches. Inspect old processes and their children before
any separately approved cleanup; never stop every process named `claude`.

## Verification and scope

After a user-approved recovery, confirm that the startup dialog is gone, the
teammate receives its assignment, and its transcript records new task activity.
Process existence alone is insufficient. After shutdown, confirm the specific
teammate exits and the lead receives the outcome.

Claude Code 2.1.311 includes fixes for repeated `SubagentStop` hooks, late MCP
tool availability and interrupted MCP reads. These do not remove the deliberate
external-import consent gate. Keep runtime version fixes distinct from toolkit
instruction and configuration fixes.

Sources reviewed 2026-10-27:

- [Claude memory imports](https://code.claude.com/docs/en/memory#import-additional-files)
- [Agent teams, startup, shutdown and limitations](https://code.claude.com/docs/en/agent-teams)
- [Subagent lifecycle](https://code.claude.com/docs/en/sub-agents)
- [Claude Code 2.1.311 release notes](https://github.com/anthropics/claude-code/releases/tag/v2.1.311)

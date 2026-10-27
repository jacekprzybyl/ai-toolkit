---
title: "Ecosystem sync and Claude teammate diagnostics"
category: planning
service: ai-toolkit
tags: [ecosystem, compatibility, claude, codex, subagents]
created: "2026-10-27"
last_updated: "2026-10-27"
description: "Execution plan and evidence for the October ecosystem refresh and reported hanging Claude teammates."
---

# Ecosystem sync and Claude teammate diagnostics

## Objective and authorization

The user requested a compatibility review of Codex, Claude and all other
supported editors, updates following the SOP, and investigation of hanging
Claude teammates. Implementation and installed-toolkit refresh are authorized.
Preserve configured models, permissions, user files and active sessions.

## Execution plan

1. Capture installed versions, effective configuration, live process evidence
   and the online ecosystem report before modifying runtime configuration.
2. Review all 13 registry targets against current official feature references;
   classify each finding using `kb/procedures/sop-ecosystem-sync.md`.
3. Reproduce confirmed integration defects, add regression coverage, and update
   their canonical sources, adapters, generated artifacts and affected docs.
4. Run validation, audit, lint/type checks and full test suites. Refresh the
   ecosystem snapshot only after the corresponding sources are reviewed.
5. Refresh the installed toolkit and installed plugin packs using the maintenance
   SOP, verify delivered files and configuration preservation, and record remaining
   limitations. Prepare any release through the release SOP, never manual tagging.

## Ownership

- Coordinator: execution plan, online doctor, registry and snapshot integration,
  shared documentation, verification and installed-toolkit refresh.
- Claude diagnostics reviewer: live teammate/process evidence and native Claude
  lifecycle contracts; initially read-only.
- Codex reviewer: native agent/skill/hook/plugin contracts and duplicate or false
  search-first hook behavior; initially read-only.
- Other-editor reviewer: the remaining eleven registry targets, official sources
  and drift classifications; initially read-only.

## Acceptance criteria

- Every registry target has a dated evidence-based disposition, including source
  access gaps; installed versions are distinguished from vendor release versions.
- Every confirmed changed behavior has appropriate regression tests and docs.
- Teammate diagnosis identifies a supported cause with evidence, or states exactly
  which live evidence is missing; an idle process is not called hung without proof.
- Full applicable local gates pass on the final source revision.
- Installed output preserves user configuration, including the explicit global
  `rag-mcp` automatic approval preference.

## Pre-mortem

- Documentation landing-page changes can mask feature-contract drift: review
  priority feature references as well as automated heading/marker differences.
- Restarting or killing an active teammate can lose useful execution state:
  collect process and session evidence before any disruptive action.
- Concurrent generation can overwrite independent changes: centralize shared
  registry, snapshot and artifact regeneration in the coordinator.
- Global/local hooks can run twice or block on conversational messages: inspect
  actual emitted hooks and event payloads, then reproduce before patching.
- Local test tooling can create false failures: use the verified Node/npm path;
  the preceding merge passed with npm 11.13.0, 2003 Bats tests and 1026 Python tests.

## Initial evidence

- Starting revision: `678cbeff7a6a16e50147b612a4e428fcce494160` (clean `main`).
- Installed versions: ai-toolkit 5.4.1, Claude Code 2.1.311, Codex CLI 0.164.0.
- Installed profile: standard; all eleven editor integrations registered globally.
- Installed plugin state: `legal-pl-pack` 1.3.0 for Claude; no Codex, Cursor or
  Gemini plugin packs recorded.
- The registry's last documentation review predates this task (2026-10-05).
- All 13 targets now have dated official-source dispositions in
  `scripts/ecosystem_tools.json` and `kb/reference/supported-tools-registry.md`.
- The online doctor refresh completed without fetch errors. A subsequent online
  check passed; four pages changed content hashes only, with no structural drift.

## Confirmed defects and implementation

- Claude teammates launched below the repository root waited at the external
  instruction-import consent dialog before consuming their task messages.
  Readiness/root-directory guidance and native shutdown instructions are fixed;
  exact legacy idle reminders migrate without changing user hook variants.
- Parent-directed SIGHUP/SIGTERM left account clients running after the Node
  wrapper exited. Isolated fake Claude/Codex clients reproduce this; supervision
  now forwards shutdown and preserves single terminal SIGINT delivery.
- Codex search guards re-armed on conversational handoffs/continuations and
  ignored `stop_hook_active`; SubagentStop emitted invalid plain output. Native
  regressions cover fixes and safe pairing of equivalent global/local advisory
  invocations, with bounded state cleanup and normal execution on uncertainty.
- Codex MCP refresh discarded user policies and empty allowlists. Seven
  integration cases cover preservation for unchanged connections, explicit
  replacement, empty transport options and no trust transfer to changed servers.
- Antigravity retirement guidance was stale; current guidance uses October 19
  while retaining older-client fallback. Copilot event metadata and model
  reference guidance are refreshed without changing selected models.
- Full macOS gates exposed a 1 MiB Node output-buffer failure once the expanded
  catalogue exceeded that size. A bounded 16 MiB generator buffer and explicit
  overflow diagnostics now pass small/large/overflow CLI regressions.

## Verification and remaining operational work

Independent reviews approved MCP policy preservation and the corrected Codex
hooks. Focused suites passed, including 243 Codex/search Bats tests, 18 prompt
Python tests, seven MCP policy tests, and account signal/idle migration cases.
The first complete macOS run passed 2009 of 2011 tests and identified the two
CLI export failures above. After that fix, every `release --gates-only` gate
passed: 2012 Bats tests on macOS, 2012 on Ubuntu, 1035 Python tests on Python
3.11, Ruff, mypy, Python 3.13 syntax/import checks, validation, audit, ShellCheck,
generation drift, package build and isolated install smoke. Initial logs remain
retained. No tag or publication was performed by the rehearsal.

The verified 5.4.2 package is installed locally, the existing legal pack was
updated from 1.3.0 to 1.7.0, and the updater refreshed 99 registered projects.
Package/configuration backups were verified before installation. Model and
permission settings, the global RAG approval, and constitution bytes were
preserved. Global/project Codex assets match byte-for-byte; each Claude profile
has one current idle reminder. Doctor reports no errors.

An enabled older synced toolkit plugin was confirmed with the native Claude
plugin list and disabled through its supported command, leaving the global
install authoritative. The new Claude Chat/Cowork ZIP and global instructions
passed native runtime validation; uploading that bundle requires the user's
Claude application UI. Live-process cleanup still requires an explicit selection
because an additional idle session has an open terminal. No existing session or
external-import consent flag has been changed.

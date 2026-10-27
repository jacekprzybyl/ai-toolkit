#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
#
# subagent-stop.sh — Enforce a concise completion checklist for subagents.
#
# Fires on: SubagentStop
# Matcher: all
# Skipped when TOOLKIT_HOOK_PROFILE=minimal.

# shellcheck source=_profile-check.sh
source "$(dirname "$0")/_profile-check.sh"

# Read from stdin (Claude Code passes JSON with .agent_id, .agent_type)
INPUT=$(cat)
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // "subagent"' 2>/dev/null)

MESSAGE="SubagentStop: ${AGENT_TYPE} should report findings, exact files touched, tests run, remaining risks, and any docs that must be updated by the lead agent."
if [ "${AI_TOOLKIT_HOOK_FORMAT:-}" = "codex" ]; then
    # Codex rejects plain stdout for SubagentStop. This is an advisory message,
    # not a continuation decision that could restart a completed subagent.
    jq -nc --arg message "$MESSAGE" '{"systemMessage":$message}'
else
    printf '%s\n' "$MESSAGE"
fi

exit 0


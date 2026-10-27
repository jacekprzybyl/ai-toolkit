---
title: "Supported Tools Registry"
category: reference
service: ai-toolkit
tags: [editors, platforms, generators, integration, ecosystem]
version: "1.21.0"
created: "2026-04-23"
last_updated: "2026-10-27"
description: "Human-readable view of scripts/ecosystem_tools.json: Claude Code, Claude Chat/Cowork, and 11 editors."
---

# Supported Tools Registry

The canonical data lives in **`scripts/ecosystem_tools.json`** and is consumed by `scripts/ecosystem_doctor.py`. This document is a derived view. Update it whenever the JSON changes. The [2026-09-23 review](../planning/ecosystem-sync-20260923.md) records source-backed classifications for every target; local CLI versions are observations, not claims about the latest upstream release.

## Tool Count: 13

The [2026-10-02 release review](../planning/ecosystem-sync-20261002.md) verifies
all 13 integrations and records the adopted Augment and Antigravity migrations.

The recommended primary working set is Claude Code, Codex and Antigravity.
Other listed integrations remain supported and opt-in. This changes neither
`--editors all` nor recorded editor selections, and does not uninstall software.
For current model defaults and optional Claude-to-Codex execution, see
[Model Compatibility](model-compatibility.md#conditional-claude-to-codex-delegation).

1 primary runtime, 1 Claude app target, and 11 editor integrations.

---

## Primary Runtime

### Claude Code

| Field | Value |
|-------|-------|
| ID | `claude-code` |
| Review 2026-10-27 | Classes A/B. Stable and locally installed 2.1.311. Native [team lifecycle](https://code.claude.com/docs/en/agent-teams) and [external import consent](https://code.claude.com/docs/en/memory#import-additional-files) informed readiness, shutdown and legacy idle-reminder corrections. Other emitted contracts remain compatible. |
| Docs | https://code.claude.com/docs (platform.claude.com/docs 307-redirects here) |
| Release notes | https://github.com/anthropics/claude-code/releases |
| Changelog | https://code.claude.com/docs/en/changelog; GitHub release feed is authoritative when the generated page lags (local version observed 2026-09-23: 2.1.280; documentation contracts were reviewed independently of the local version) |
| Config paths | Settings and direct content: `~/.claude/settings.json`, `.claude/settings.json` (project, committed), `.claude/settings.local.json`, `CLAUDE.md`, `.claude/rules/*.md`, `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `~/.claude/themes/*.json` (v2.1.118+). Native plugin root: `.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `commands/*.md`, `agents/*.md`, `workflows/`, `output-styles/`, `themes/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `monitors/monitors.json`, `bin/*`, `settings.json` |
| Our generators | — (Claude Code is the primary target; toolkit content ships directly as `.md` files and `settings.json` merges) |
| Tracked hook events | Core: `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `Notification`, `MessageDisplay`. Tool: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`. Turn: `Stop`, `StopFailure`, `UserPromptExpansion`. Subagent: `SubagentStart`, `SubagentStop`. Compaction: `PreCompact`, `PostCompact`. Permissions: `PermissionRequest`, `PermissionDenied`. Elicitation: `Elicitation`, `ElicitationResult`. Teams: `TaskCreated`, `TaskCompleted`, `TeammateIdle`. Worktrees/env: `WorktreeCreate`, `WorktreeRemove`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `ConfigChange`. Setup: `Setup`, `InstructionsLoaded`. Model changes: `PreModelSwitch`, `PostModelSwitch` |
| Tracked handler types | `command`, `prompt`, `agent`, `mcp_tool`, `http` (POST event JSON to allowlisted URLs via `allowedHttpHookUrls`) |
| Other capabilities | slash commands, MCP server/client, sub-agent, output style, `SKILL.md` (≥500 lines warn) |
| Plugin component coverage | Existing plugin packaging uses skills and hooks. Native workflows, output styles, LSP servers, experimental themes and monitors, MCP-backed channels, and root plugin `settings.json` are recognized class C surfaces and are not generated. Claude Code accepts only `agent` and `subagentStatusLine` in root plugin settings. |
| Version probe | `claude --version` |
| Notes | v2.1.169 added `disableBundledSkills` setting + `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` env var (hides bundled skills/built-in slash commands from the model; toolkit skills in `.claude/skills/` are unaffected — useful when toolkit skills overlap built-ins) and `claude --safe-mode` / `CLAUDE_CODE_SAFE_MODE` (starts with hooks, skills, agents, and CLAUDE.md disabled — first isolation step when debugging toolkit rule enforcement). `fallbackModel` settings key (v2.1.166) noted as not-adopted (class C, no toolkit surface writes model settings). |

---

## Claude App Target

### Claude Chat / Cowork

| Field | Value |
|-------|-------|
| ID | `claude-app` |
| Review 2026-10-27 | Classes A/C. [Plugin distribution](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) retains the exported ZIP and runtime split. Account sync is separate from local installation; inspect duplicate components before disabling either copy. |
| Docs | https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork |
| Plugin docs | https://support.claude.com/en/articles/13837440-use-plugins-in-claude |
| Config surfaces | `Settings > Cowork > Global instructions`, Cowork folder instructions, `Customize > Skills`, `Customize > Plugins`, plus the one file-based surface: `claude_desktop_config.json` (macOS `~/Library/Application Support/Claude/`, Windows `%APPDATA%/Claude/`, Linux `~/.config/Claude/`; `CLAUDE_USER_DATA_DIR` overrides the root) |
| Plugin layout | `.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `agents/*.md`, `hooks/hooks.json`; ai-toolkit uses manifest paths under `claude-app/` for its generated app-only rules and hooks |
| Our generator | `scripts/claude_app.py` (`ai-toolkit claude-app export`); `scripts/mcp_editors.py` for the `claude-app` MCP adapter |
| Runtime split | Skills work in Chat (web/Desktop) and Cowork. App hooks and sub-agents run in Cowork. Plugins enabled on the account also sync to Claude Code terminal sessions from 2.1.273, under `~/.claude/plugins/synced/` with `@synced` IDs. Claude app does **not** scan Claude Code's `~/.claude/rules/`, `CLAUDE.md`, or `~/.claude/settings.json`. |
| MCP | `ai-toolkit mcp install --editor claude-app --scope global <template>` writes `claude_desktop_config.json` directly -- no plugin involved. Entries are validated by the app as `{command, args, env}`; remote endpoints belong to the separate UI-managed `remoteMcpServers` surface, so HTTP/SSE templates are bridged through `mcp-remote`. Restart the app to load a change. |
| Install/update | Export the ZIP, upload it from `Customize > Plugins`, then paste the generated global-instructions file into `Settings > Cowork > Global instructions`. Re-export/re-upload after toolkit updates. Account sync does not upload local toolkit updates; the doctor diagnoses possible duplicate loading without automatically disabling organization-required plugins. MCP config is the exception -- it updates from the CLI like any other editor. |

---

## Editor Integrations

### Cursor

| Field | Value |
|-------|-------|
| ID | `cursor` |
| Review 2026-10-27 | Classes A/C. [Hooks](https://cursor.com/docs/hooks) retain the generated version-1 events. [Subagents](https://cursor.com/docs/subagents) retain the emitted metadata and `model: inherit`; optional per-model parameters do not authorize changing user selections. |
| Docs | https://cursor.com/docs |
| Changelog | https://cursor.com/changelog |
| Stable docs mirror | https://cursor.com/llms.txt (all doc pages have .md twins) |
| Config paths | `.cursorrules` (**legacy** — no longer in cursor.com/docs/rules; deprecated ~0.43–0.45 in favor of `.cursor/rules/*.mdc`, still read, no removal deadline; we keep emitting for back-compat), `.cursor/rules/*.mdc` (plain `.md` files in `.cursor/rules/` are **ignored** by the rules system), `AGENTS.md`, `.cursor/mcp.json`, `~/.cursor/mcp.json`, `.cursor/hooks.json`, `~/.cursor/hooks.json` (user-level hooks scope; enterprise system paths + dashboard team hooks not adopted, class C), `.cursor/skills/*/SKILL.md`, `~/.cursor/skills/*/SKILL.md`, `.cursor/agents/*.md`, `~/.cursor/agents/*.md` |
| Compat read paths | skills: `.agents/skills/`, `~/.agents/skills/`, `.claude/skills/`, `~/.claude/skills/`, `.codex/skills/`, `~/.codex/skills/`; subagents: `.claude/agents/`, `~/.claude/agents/`, `.codex/agents/`, `~/.codex/agents/` (`.cursor/` wins on name conflicts) |
| Our generators | `scripts/generate_cursor_rules.py`, `scripts/generate_cursor_mdc.py`, `scripts/generate_cursor_hooks.py` (complete version-1 event set plus self-contained `.cursor/hooks/ai-toolkit/cursor_hook.py`; profile=full local **and** global `~/.cursor/hooks.json`), `scripts/generate_cursor_agents.py` (profile=full), `scripts/generate_cursor_skills.py` (profile=full pointer) |
| Global install | Cursor is in `GLOBAL_CAPABLE_EDITORS` for **hooks only**: `ai-toolkit install --editors cursor` writes `~/.cursor/hooks.json` (profile ≥ standard). RULES stay project-local (Cursor's only global rules surface is the Settings UI). |
| Tracked capabilities | `cursorrules`, `.cursor/rules`, `AGENTS.md`, `mcp.json`, Composer, Agent Mode, hooks.json, subagents, skills, plugins |
| Hook compatibility | Cursor 3.11 project hooks run locally and in cloud agents from repository `.cursor/hooks.json`; cloud VMs do not load `~/.cursor/hooks.json`. The generated project manifest uses only documented command-entry keys, calls a repo-relative runtime, covers conversation hooks including `afterAgentResponse` and `afterAgentThought`, preserves user entries, returns explicit `permission: allow` on successful permission checks, and caps `stop`/`subagentStop` follow-up loops at 5. |

### Windsurf

| Field | Value |
|-------|-------|
| ID | `windsurf` |
| Review 2026-10-27 | Class A. [Lifecycle hooks](https://docs.devin.ai/cli/extensibility/hooks/lifecycle-hooks) retain the emitted event mappings. [Skill discovery](https://docs.devin.ai/cli/extensibility/skills/overview) still supports `.windsurf/skills/`; retain one pointer instead of duplicating it in `.devin/skills/`. |
| Docs | https://docs.devin.ai/desktop (Windsurf rebranded to Devin Desktop ~2026-06-02; docs.windsurf.com resolves here) |
| Changelog | https://docs.devin.ai/desktop/changelog (windsurf.com/changelog 308-permanent-redirects here) |
| Stable docs mirror | https://docs.devin.ai/desktop/... per-page .md twins; legacy `.windsurf/`, `.windsurfrules`, `~/.codeium/windsurf/` rule paths still read as fallback (new canonical rules/hooks tree: `.devin/`) |
| Config paths | **Primary (Devin Desktop):** `.devin/rules/*.md`, `.devin/workflows/*.md`, `.devin/hooks.v1.json` (Devin CLI hooks, Claude format), `.devin/config.json`, `.devin/config.local.json`, `~/.config/devin/config.json` (Devin Local MCP/permissions). **Skills:** the current reference documents project `.agents/skills/`, `.devin/skills/`, and `.windsurf/skills/`. ai-toolkit emits a single canonical pointer under `.windsurf/skills` to avoid duplicate registration. **Legacy fallback:** `.windsurfrules`, `.windsurf/rules/*.md`, `.windsurf/workflows/*.md`, `~/.codeium/windsurf/memories/global_rules.md`, `~/.codeium/windsurf/skills/*/SKILL.md`, `~/.codeium/windsurf/mcp_config.json`. Current Devin also documents `~/.config/devin/skills/*/SKILL.md`. Plus `AGENTS.md`. |
| Compat read paths | Current skill docs list project `.agents/skills/`, `.devin/skills/`, `.windsurf/skills/`, and global `~/.agents/skills/`, `~/.config/devin/skills/`, `~/.codeium/<channel>/skills/`. **Hooks:** Devin CLI reads `.claude/settings.json` + `~/.claude/settings.json` hooks when `read_config_from.claude` is enabled, so globally-installed toolkit hooks also work under Devin. |
| Our generators | `scripts/generate_windsurf.py`, `scripts/generate_windsurf_rules.py` (dual-emits `.devin/` + `.windsurf/` rules/workflows), `scripts/generate_devin_hooks.py` (profile=full; `.devin/hooks.v1.json`), `scripts/generate_windsurf_skills.py` (`.windsurf/skills` pointer) |
| Global install | `ai-toolkit install --editors windsurf` writes `~/.codeium/windsurf/memories/global_rules.md` + skills pointer **and** `~/.config/devin/AGENTS.md` (Devin CLI global rules — the Desktop `global_rules.md` path is absent from `read_config_from.windsurf`, so editor-only Devin CLI installs need this). |
| Tracked capabilities | Cascade, `windsurfrules`, `AGENTS.md`, activation triggers (`always_on`/`glob`/`model_decision`), workflows, skills, MCP, memories, hooks |
| Activation modes emitted | always_on (agents/security/quality), glob (testing + language rules), model_decision (code-style/workflow) |
| Hooks migration | **Complete.** Cascade and `.windsurf/hooks.json` ended on 2026-07-01. `generate_devin_hooks.py` is now the only Windsurf-family hook generator and emits `.devin/hooks.v1.json` with Claude-style events, Devin tool-name matchers, and the flat Devin block contract. |
| Earlier reviewed release | Devin Desktop v3.10.31 (2026-09-16), a historical baseline rather than a latest-version claim. Workflows have been deprecated in favor of skills since v3.6.22; generation reports this while retaining compatibility files. v3.4.22 made skill `permissions:` frontmatter affect auto-approvals; ai-toolkit does not emit permissions because its pointer skill executes no privileged workflow. |

### GitHub Copilot

| Field | Value |
|-------|-------|
| ID | `github-copilot` |
| Review 2026-10-27 | Classes A/C/D. [The hook reference](https://docs.github.com/en/copilot/reference/hooks-reference) retains generated command handlers and documents `userPromptTransformed`, now recognized without adding a toolkit handler. Direct `exec`/`args`, agent-scoped hooks, HTTP/prompt handlers and progress messages are optional surfaces. The dedicated toolkit file does not validate sibling user hook files. [Retired `infer`](https://docs.github.com/en/copilot/reference/custom-agents-configuration) is already replaced by invocation controls. |
| Docs | https://docs.github.com/en/copilot |
| Release notes | https://github.blog/changelog/label/copilot/ |
| Native docs | [VS Code hooks](https://code.visualstudio.com/docs/agent-customization/hooks), [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [Hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference), [skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills), [CLI config directory](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| Config paths | **Repo (`.github/`):** `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md`, `.github/agents/*.agent.md`, `.github/skills/<name>/SKILL.md`, `.github/hooks/*.json`, `AGENTS.md`. **Copilot CLI user-level (`~/.copilot/`, `COPILOT_HOME` override):** `copilot-instructions.md`, `instructions/*.instructions.md`, `agents/*.agent.md`, `skills/<name>/SKILL.md`, `hooks/*.json`, `settings.json`, `mcp-config.json` below the active config root. |
| Compat read paths | Copilot also discovers project `.claude/skills` and `.agents/skills`, and personal `~/.agents/skills`. ai-toolkit nevertheless materializes self-contained native skills under `.github/skills` and the active Copilot config root so assets and helper scripts remain available and `COPILOT_HOME` sessions do not depend on fallback discovery. |
| Our generators | `scripts/generate_copilot.py` (instructions, prompts, agents, and portable skill directories), `scripts/generate_copilot_hooks.py` (native version-1 hook config plus self-contained runtime) |
| Global install | `ai-toolkit install --editors copilot` writes instructions, agents, skills, and, for profile ≥ `standard`, native hooks below `$COPILOT_HOME` when set or `~/.copilot` otherwise. VS Code Copilot and GitHub.com use repo `.github/` files, so local emission remains required. |
| Tracked capabilities | `copilot-instructions.md`, Copilot Chat, Copilot Workspace, Copilot cloud agent, `applyTo`, custom agents, prompt files, `instructions.md`, `AGENTS.md`, MCP, skills, CLI hooks, `~/.copilot/` |
| Compatibility notes | Skills preserve `user-invocable` and `disable-model-invocation` for clients supporting those controls. Custom agents use native `.agent.md` files with `name` and `description` and a 30,000-character limit; `tools` is omitted instead of guessing editor-specific aliases. Prompt and skill bodies remove Claude-only interpolation and delegation APIs. Hooks use the GitHub version-1 schema and camelCase event names, with separate CLI/cloud and VS Code native decision payloads, and a repository/config-root-contained Python runtime instead of Claude hook scripts. Project MCP remains owned by the editor MCP sync path. Copilot code review also reads the nearest `AGENTS.md`; local install keeps its generated section separate from Codex/OpenCode sections. Surface loading semantics and the prompt/skill duplication are documented in `kb/reference/copilot-compatibility.md`. |

### Gemini CLI

| Field | Value |
|-------|-------|
| ID | `gemini-cli` |
| Review 2026-10-27 | Class A. Stable [0.65.0](https://github.com/google-gemini/gemini-cli/releases/tag/v0.65.0), published 2026-10-20, fixes runtime/authentication/resume behavior without requiring generator changes. The [eleven hook events](https://geminicli.com/docs/hooks/) still match the allowlist; completion remains `AfterAgent`. Release review is separate from the local version probe. |
| Docs | https://github.com/google-gemini/gemini-cli/tree/main/docs |
| Release notes | https://github.com/google-gemini/gemini-cli/releases |
| Config paths | `GEMINI.md`, `.gemini/settings.json`, `~/.gemini/settings.json`, `.gemini/commands/*.toml`, `.gemini/skills/*/SKILL.md`, `.gemini/agents/*.md`, `.agents/skills/*/SKILL.md`, `~/.gemini/skills/*/SKILL.md`, `~/.gemini/agents/*.md`, `~/.agents/skills/*/SKILL.md` (the `.agents/skills` alias wins over `.gemini/skills` within the same tier). Extension packages keep `gemini-extension.json` at the package root and install below `~/.gemini/extensions/<name>/`. |
| Our generators | `scripts/generate_gemini.py`, `scripts/generate_gemini_hooks.py` (profile>=standard), `scripts/generate_gemini_commands.py` (profile=full), `scripts/generate_gemini_skills.py` (profile=full), `scripts/generate_gemini_agents.py` (profile=full) |
| Global install | `ai-toolkit install --editors gemini` writes `~/.gemini/GEMINI.md` **plus** hooks at `~/.gemini/settings.json` (profile ≥ standard) and `~/.gemini/{commands,skills,agents}/` (profile=full). Agents use native `name`, `description`, and `kind: local` metadata; incompatible Claude `model` and `tools` fields are omitted. |
| Tracked capabilities | `GEMINI.md`, `mcpServers`, tools, `settings.json`, `BeforeTool`, `AfterTool`, `BeforeToolSelection`, `BeforeAgent`, `AfterAgent`, `BeforeModel`, `AfterModel`, `Notification`, `PreCompress`, `SessionStart`, `SessionEnd`, `SKILL.md`, `activate_skill`, custom commands, `.gemini/agents/*.md` subagents, `gemini-extension.json` (no native `Stop` event — generator maps Stop-equivalent to `AfterAgent`; 11 documented hook events total) |
| Version probe | `gemini --version` |
| Extension coverage | Current Gemini extensions can bundle root `GEMINI.md`, `commands/`, `hooks/hooks.json`, `skills/`, `agents/`, and `policies/`. ai-toolkit does not export a Gemini extension package; this distribution surface is class C / not adopted. |
| Earlier baseline / notes | v0.49.0 (2026-06-25) completed the `coreTools` to `tools.core` migration; the toolkit emits neither key. Gemini CLI dropped free/paid individual tiers on 2026-06-18 in favor of Antigravity CLI; enterprise Code Assist and paid API keys keep Gemini CLI, so the integration remains supported. Native project and user-tier subagents are emitted by `generate_gemini_agents.py` for profile `full`. |

### Cline

| Field | Value |
|-------|-------|
| ID | `cline` |
| Review 2026-10-27 | Classes A/C/D. Reviewed [4.1.26](https://github.com/cline/cline/releases/tag/v4.1.26), published 2026-10-26, independently of local installation. [Skills](https://docs.cline.bot/customization/skills) still recommend the emitted `.cline/skills/` and accept `.clinerules/skills/`. Cloud/plugin features are optional; `.clineignore` deprecation does not affect toolkit output. The extension-hook availability caveat below remains current. |
| Docs | https://docs.cline.bot |
| Release notes | https://github.com/cline/cline/releases |
| Config paths | **Extension compatibility:** `.clinerules/*.md`, `.clinerules/workflows/*.md`, `.clinerules/skills/*/SKILL.md`, `.clinerules/hooks/` (project), `~/Documents/Cline/Rules/` (global rules), `~/Documents/Cline/Hooks/` (global hooks), `~/.cline/data/settings/cline_mcp_settings.json`. **CLI/SDK primary layout:** `.cline/{rules,hooks,agents,plugins,skills}/`, `~/.cline/{rules,hooks,agents,plugins,skills}/`; CLI `--hooks-dir` defaults to `~/.cline/hooks`. **Cross-tool:** `AGENTS.md` + `~/.agents/AGENTS.md` (rules sources), `.claude/skills/*/SKILL.md` (native skill discovery). |
| Our generators | `scripts/generate_cline.py`, `scripts/generate_cline_rules.py` (native + compatibility rules), `scripts/generate_cline_skills.py`, `scripts/generate_cline_hooks.py` (exact eight extensionless events with a self-contained adapter) |
| Tracked capabilities | `clinerules`, Plan Mode, Act Mode, MCP, custom modes, workflows, hooks, skills, subagents, conditional rules, `AGENTS.md`, plugins |
| Plugins | `.cline/plugins/` + `~/.cline/plugins/` and the `package.json` `cline.plugins` manifest belong to Cline CLI/SDK and Kanban plugin flows. They are not a plugin-loading surface for the VS Code or JetBrains extension, so ai-toolkit does not auto-package or install a Cline plugin. |
| Notes | Current Cline docs announce `.clineignore` deprecation; ai-toolkit does not emit it. [Upstream hook documentation](https://github.com/cline/cline/blob/main/.clinerules/hooks/README.md) confirms the executable-hook schema but still marks `TaskComplete` and `PreCompact` as coming soon; emitted files do not guarantee these events fire. Conditional rules (`paths:` YAML frontmatter) are emitted for testing and language-specific rules. Project installs write `.cline/rules/` as the native primary plus `.clinerules/` compatibility, and dual-emit hooks to `.cline/hooks/` plus extension-native `.clinerules/hooks/`. The documented `.cline/agents/` and `~/.cline/agents/` paths are tracked, but ai-toolkit does not emit agents until a portable file schema is verified. Hook input validates `preToolUse.toolName` and command parameters, including CLI `run_commands`; output uses only `cancel`, `contextModification`, and `errorMessage`, with bounded input and runtime. |
| Global install | `ai-toolkit install --editors cline` writes `~/.cline/{rules,hooks}/` as the CLI primary and `~/Documents/Cline/{Rules,Hooks}/` for extension compatibility. Hooks are absent in `minimal` and present in `standard`, `strict`, and `full`. A skill pointer is emitted under `~/.cline/skills/` only when real Claude skills are not already discoverable. MCP remains managed by `ai-toolkit mcp install --editor cline`. |

### Roo Code

| Field | Value |
|-------|-------|
| ID | `roo-code` |
| Review 2026-10-27 | Classes A/C. Reviewed successor Zoo [3.92.0](https://github.com/Zoo-Code-Org/Zoo-Code/releases/tag/v3.92.0), published 2026-10-24. [Custom modes](https://docs.zoocode.dev/features/custom-modes) explicitly retain JSON `.roomodes`; [Roo-to-Zoo import](https://docs.zoocode.dev/roo-to-zoo-migration) remains documented. Model catalog and UI changes require no generator migration. |
| Docs | https://roocodeinc.github.io/Roo-Code (frozen; docs.roocode.com 301-redirects here). Successor docs: https://docs.zoocode.dev |
| Release notes | https://github.com/Zoo-Code-Org/Zoo-Code/releases (authoritative). Original RooCodeInc/Roo-Code is archived/read-only since 2026-05-15, frozen at v3.54.0. Follow the successor **Zoo-Code-Org/Zoo-Code** (marketplace `ZooCodeOrganization.zoo-code`); the reviewed release is recorded above. |
| Config paths | `.roomodes` (JSON still fully supported), `.roo/rules/*.md`, `.roo/rules-{slug}/*.md`, `.roo/skills/*/SKILL.md`, `~/.roo/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`, `~/.agents/skills/*`, `.roo/commands/*.md`, `~/.roo/commands/*.md`, `.roo/mcp.json`, `~/.roo/rules/`, `mcp_settings.json` + global custom modes live in VS Code globalStorage (`<globalStorage>/rooveterinaryinc.roo-cline/settings/custom_modes.yaml`), NOT `~/.roo/custom_modes.yaml` |
| Our generators | `scripts/generate_roo_modes.py`, `scripts/generate_roo_rules.py` |
| Tracked capabilities | `roomodes`, custom modes, Code Actions, MCP, Orchestrator mode, `whenToUse`, `description`, `roleDefinition`, `groups`, skills, slash commands |
| Notes | The emitted custom-mode and rules contracts remain compatible with Zoo; this does not establish parity for every product feature. `.roomodes` includes `description`/`whenToUse` for every mode; JSON remains supported while new UI-created modes default to YAML. Global install writes `~/.roo/rules/` plus `~/.agents/skills/*` (skipped when `codex` is also selected). `~/.roo/commands/` is a documented surface not yet generated. |

### Aider

| Field | Value |
|-------|-------|
| ID | `aider` |
| Review 2026-10-27 | Class A. The current [options reference](https://aider.chat/docs/config/options.html) retains the emitted architect, read/conventions, lint/test, attribution and commit-language settings. This is a contract review, not a latest-release or installed-version claim. |
| Docs | https://aider.chat/docs |
| Changelog | https://aider.chat/HISTORY.html |
| Config paths | `.aider.conf.yml`, `CONVENTIONS.md`, `~/.aider.conf.yml` |
| Our generators | `scripts/generate_aider_conf.py`, `scripts/generate_conventions.py` |
| Tracked capabilities | `.aider.conf.yml`, `CONVENTIONS.md`, `architect`, `auto-accept-architect`, `read`, `lint-cmd`, `test-cmd`, `commit-prompt`, `attribute-co-authored-by`, `chat-language`, `commit-language`, `watch-files`, `auto-commits` |
| Global install | `ai-toolkit install --editors aider` creates `~/.aider.conf.yml` only when absent and always refreshes `~/.aider-ai-toolkit-CONVENTIONS.md`; existing YAML is preserved. |
| Version probe | `aider --version` |
| Earlier reviewed release | v0.86.1 (Aug 2025); this review checks the current options contract, not latest-release availability. |

### Augment

| Field | Value |
|-------|-------|
| ID | `augment` |
| Review 2026-10-27 | Class A. Current [hooks](https://docs.augmentcode.com/cli/hooks) and [subagents](https://docs.augmentcode.com/cli/subagents) retain the emitted paths and native allowlist contract. `disabled_tools` still overrides `tools`; omit it and retain the CLI's selected model. |
| Docs | https://docs.augmentcode.com |
| Changelog | https://www.augmentcode.com/changelog |
| Config paths | `.augment/rules/*.md`, `.augment-guidelines` (workspace root, legacy single-file), `~/.augment/user-guidelines.md`, `.augment/agents/*.md`, `.augment/commands/*.md`, `.augment/skills/*/SKILL.md`, `.augment/settings.json`, `.augment/settings.local.json`, `~/.augment/rules/*.md`, `~/.augment/settings.json`, `/etc/augment/settings.json`. Auggie CLI also discovers skills/commands from `.claude/` and `.agents/` (`.augment/` wins on precedence). |
| Our generators | `scripts/generate_augment.py`, `scripts/generate_augment_rules.py`, `scripts/generate_augment_agents.py` (profile=full), `scripts/generate_augment_commands.py` (profile=full), `scripts/generate_augment_hooks.py` (profile=full, HOME-scoped), `scripts/generate_augment_skills.py` (profile=full) |
| Agent permission contract | Native allowlist only: `Read` → `view`, `Grep` → `codebase-retrieval`, `Glob` → `view` + `codebase-retrieval` (deduplicated), `Edit` → `str-replace-editor`, `Write` → `save-file`, `Bash` → `launch-process`. `disabled_tools` is omitted because it overrides `tools`, even when empty. Unmapped Claude orchestration tools are omitted with an explicit capability note; unknown tools and empty native allowlists fail before any output changes. Model remains the CLI default. Generated agents carry ownership markers; cleanup recognizes legacy exports and preserves user files. [Official subagent reference](https://docs.augmentcode.com/cli/subagents) |
| Global install | `ai-toolkit install --editors augment` writes `~/.augment/rules/ai-toolkit.md` **plus** (profile=full) `~/.augment/agents/`, `~/.augment/commands/`, and hooks in `~/.augment/settings.json` — all documented user-tier surfaces. A global-only Augment user previously got no hooks/agents/commands. Skills need no global emission: Auggie natively reads `~/.claude/skills/`. |
| Tracked capabilities | `.augment`, Agent mode, Next Edit, MCP, context engine, Auggie CLI, `always_apply`, `agent_requested`, subagents, custom commands, `SKILL.md`, `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `Stop`, `Notification`, ACP Mode, plugins/marketplace |
| Earlier baseline / notes | Auggie CLI v0.31.0. Since v0.30.0 (2026-06-25) `PreToolUse`/`PostToolUse` hooks fire during sub-agent sessions. The shared hook input adapter normalizes Augment's `conversation_id`, so edit and quality state remains isolated across parallel sub-agents. `Notification` is enum-only (doctor flipped its marker), with no dedicated handler documented, so class C (do NOT wire). Plugins/marketplace (`auggie plugin marketplace add`, `.augment-plugin`/`.claude-plugin` layouts, `enabledPlugins`/`autoUpdateMarketplaces` in settings) are documented but not yet a shipping target. |
| SPA caveat | Mintlify Next.js SPA; use `https://docs.augmentcode.com/<path>.md` siblings (discoverable via `/llms.txt`) for machine reads |

### Google Antigravity

Workflows retired on 2026-10-19. The generator adds the 13 existing command
names as `.agents/skills/<workflow-name>/SKILL.md`, and in both documented global
skill roots. Legacy workflow files remain with a deprecation comment. User-owned
skill collisions and extra resources are preserved; `emit_skill_pointer=False`
still opts out of skill-directory writes. Doctor reports unmigrated local/global
workflows. On native Windows, use WSL or `/migrate-workflows`; the generator
retains legacy output and explains why it skipped protected skill writes.
[Official migration](https://antigravity.google/docs/migration/workflows-to-skills/).
Legacy output remains an older-client fallback until a documented removal
release under [issue #34](https://github.com/softspark/ai-toolkit/issues/34);
the retirement date alone does not authorize removing user workflow files.

| Field | Value |
|-------|-------|
| ID | `google-antigravity` |
| Review 2026-10-27 | Classes A/C/D. Reviewed App [2.27.0](https://antigravity.google/docs/changelog), published 2026-10-26, separately from CLI/IDE installations. [Migration](https://antigravity.google/docs/migration/workflows-to-skills/) now dates workflow retirement to 2026-10-19. [Hooks](https://antigravity.google/docs/hooks) adds optional `SessionStart`; only three existing handlers remain wired. |
| Docs | https://antigravity.google/docs (official hook and configuration pages are now readable through the web index; use feature pages to verify) |
| Changelog | https://antigravity.google/docs/changelog |
| Config paths | Rules/workflows: `.agents/rules/*.md` (each needs `trigger:` frontmatter or Antigravity silently discards it; 24,000-byte per-file cap; always-on and global rules share a 20,000-token budget), `.agents/workflows/*.md`. Skills: canonical `.agents/skills/*/SKILL.md`; `.agent/skills/*/SKILL.md` is legacy, no longer written, and the old pointer copy is removed on reinstall. Agents: `.agents/agents/ai-toolkit-*/agent.md`. Hooks: `.agents/hooks.json` plus `.agents/hooks/ai-toolkit-antigravity-hook.py`, invoked as `python3 hooks/…` because handlers run from the `hooks.json` directory. Plugins: `.agents/plugins/<plugin>/plugin.json`. MCP: `.agents/mcp_config.json`. Cross-tool instructions: `AGENTS.md`, `GEMINI.md`. |
| Global config paths | CLI skills `~/.gemini/antigravity-cli/skills/*/SKILL.md` and CLI plugins `~/.gemini/antigravity-cli/plugins/<plugin>/plugin.json` are current canonical CLI surfaces. IDE/shared-product skills use `~/.gemini/config/skills/*/SKILL.md`; agents use `~/.gemini/config/agents/ai-toolkit-*/agent.md`; hooks use `~/.gemini/config/hooks.json` plus adjacent runtime; IDE/shared plugins use `~/.gemini/config/plugins/<plugin>/plugin.json`; MCP uses `~/.gemini/config/mcp_config.json`. The toolkit emits no modular global rules (`~/.gemini/config/rules/*.md`); only workspace `.agent/skills/` is legacy. `~/.gemini/GEMINI.md` is the Gemini-CLI-shared instruction surface and Antigravity's always-on global rule, so it carries no inline agent or skill catalogue. |
| Our generators | `scripts/generate_antigravity.py` (rules with activation frontmatter, workflows, canonical skill pointer), `scripts/generate_antigravity_hooks.py` (three-event schema, `run_command` matcher, and self-contained adapter), `scripts/registered_rules.py` (registered MCP rules only when Antigravity has the server configured), `scripts/generate_antigravity_agents.py` (native subagents and explicit tool mapping), `scripts/antigravity_plugin.py` (deterministic opt-in export/verify), and `scripts/mcp_editors.py` (transactional project/global MCP adapter). |
| Install profiles | `minimal`: rules/workflows/skills only. `standard` and `strict`: add native hooks. `full`: additionally adds native agents. Global install follows the same gates under `~/.gemini/config/`; it never auto-installs the plugin. |
| Plugin flow | `ai-toolkit antigravity-plugin export [output]` creates a self-contained ZIP with exact manifest fields `$schema`, `name`, `description`, rules, skills, agents, hooks, runtime, and LICENSE. Verify offline with `ai-toolkit antigravity-plugin verify <archive-or-dir>`, then install manually under `.agents/plugins/<plugin>/` for a workspace, `~/.gemini/antigravity-cli/plugins/<plugin>/` for CLI, or `~/.gemini/config/plugins/<plugin>/` for the IDE/shared product. Hook commands resolve from `${extensionPath}`. |
| Tracked capabilities | Antigravity, agent manager, artifacts, MCP, workflows, rules, skills, hooks, six native hook events (three wired), subagents, agent permissions, plugins, global skills/hooks/agents, `AGENTS.md`, `GEMINI.md`, `serverUrl` |
| Reviewed baseline / notes | The release reviewed above is the Antigravity App; earlier CLI/IDE observations are historical. Native agent models remain `inherit`/`flash`/`pro`; toolkit agents preserve `inherit` and validate tool names. Antigravity defines `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, and `Stop`; the toolkit wires only `PreToolUse` (matcher `run_command`), `PreInvocation`, and `Stop`. Optional `SessionStart` is tracked without adding a handler. The shell command is `.toolCall.args.CommandLine`. Handlers run via `sh -c` from the directory containing `hooks.json` (agy 1.3.1 runtime observation, 2026-10-07). The adapter returns native camelCase payloads, object-shaped `injectSteps`, and bounded Stop continuation. MCP normalizes legacy input `url` into `serverUrl` and rejects `httpUrl`; optional arguments, environment, working directory, authentication and tool controls remain preserved. |
| Doc access note | Docs are a JavaScript SPA, but the official search index exposes the current MCP guide and changelog text. Verify changelog claims against the dated official entry because the MCP guide's warning can lag schema releases. |

### Codex CLI

| Field | Value |
|-------|-------|
| ID | `codex-cli` |
| Review 2026-10-27 | Classes A/B/C. Stable CLI and local daemon 0.164.0. Current [hook contracts](https://learn.chatgpt.com/docs/hooks) require SubagentStop JSON and treat Stop feedback as a new prompt; toolkit corrections also pair identical advisory invocations across global/project layers when native identity is available. Models and permissions remain configured by the user. |
| Docs | https://learn.chatgpt.com/docs/codex/cli (official Codex CLI documentation; local version observed during the 2026-09-23 review: codex-cli 0.155.1) |
| Release notes | https://github.com/openai/codex/releases |
| Config paths | **Instructions:** project `AGENTS.md` (root→cwd chain, closest wins) and global `~/.codex/AGENTS.md` (`$CODEX_HOME/AGENTS.md`; `~/.codex/AGENTS.override.md` takes precedence). NOTE: `~/AGENTS.md` is NOT a global-instruction surface — Codex only reads it if a session's cwd is exactly `$HOME`. Plus `.agents/skills/*/SKILL.md`, `.codex/agents/*.toml`, `~/.codex/agents/*.toml`, `.codex/hooks.json`, `~/.codex/hooks.json`, `.codex/config.toml` (project layers, root→cwd, closest wins, trusted projects only), `~/.codex/config.toml`. **Native plugins:** root `plugin.json` (portable Agent Plugins manifest), `.codex-plugin/plugin.json` (compatibility overlay), root `skills/*/SKILL.md`, default `hooks/hooks.json`, and `.agents/plugins/marketplace.json`. |
| Our generators | `scripts/generate_codex.py`, `scripts/generate_codex_agents.py` (native custom-agent TOML), `scripts/generate_codex_hooks.py`, `scripts/generate_codex_skills.py` (opt-in via `--codex-skills`), `scripts/codex_plugin.py` (deterministic native plugin exporter/validator) |
| Rules delivery | Universal coding rules are inlined into `AGENTS.md` (Codex reads instructions only from AGENTS.md, not `.agents/rules/`); language rules ship as `<lang>-rules` skills under `.agents/skills/`. Global install writes `~/.codex/AGENTS.md` (not `~/AGENTS.md`, which Codex never loads globally); plugin-pack rules are marker-injected into the same file. `project_doc_max_bytes` default is 32 KiB and Codex silently truncates AGENTS.md past that (see codex-cli-compatibility.md). |
| Tracked hook events | Official Codex hooks contract: `PreToolUse`, `PostToolUse`, `PermissionRequest`, `PreCompact`, `PostCompact`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, `Interrupt` (12 events). We wire 10 through the Codex map, including the advisory `SessionEnd` handoff and destructive-command and wrong-home path guards on both Bash `PreToolUse` and `PermissionRequest`. `PostCompact` and `Interrupt` are accepted but not emitted by the base bundle. MCP search tools trigger the search tracker; Stop continuation uses `decision: block` with a reason. |
| Tracked handler types | `command` (generated by ai-toolkit) and `mcp_tool` (validated and preserved for user configuration). MCP handlers use `server`, `tool` and optional `input`; `SessionEnd` remains command-only. `prompt` and `agent` are not generated. |
| Other capabilities | `AGENTS.md`, `config.toml`, `mcp_servers`, sandbox policies, `.agents/skills/*/SKILL.md` (native Codex skill discovery path), `.codex/agents/*.toml` (native custom agents) |
| Native plugin distribution | `ai-toolkit codex-plugin export` packages root `plugin.json` plus `.codex-plugin/plugin.json`, plugin-adapted skills, default lifecycle hooks, executable assets, and LICENSE. Hook commands resolve through `${PLUGIN_ROOT}`. Installation uses a local marketplace and `/plugins`; Codex IDE does not support plugins. |
| Version probe | `codex --version` |

### opencode

| Field | Value |
|-------|-------|
| ID | `opencode` |
| Review 2026-10-27 | Classes A/C/D. Stable [1.19.4](https://github.com/anomalyco/opencode/releases/tag/v1.19.4), published 2026-10-22, updates bundled Bun without changing [plugin](https://opencode.ai/docs/plugins/) or [agent](https://opencode.ai/docs/agents/) contracts. Deprecated agent `tools` is already omitted. Release review is separate from the local version probe. |
| Docs | https://opencode.ai/docs |
| Release notes | https://github.com/sst/opencode/releases (redirects to anomalyco/opencode) |
| Config paths | `opencode.json`, `opencode.jsonc`, `.opencode/agents/*.md`, `.opencode/commands/*.md`, `.opencode/plugins/*`, `.opencode/skills/*/SKILL.md`, `AGENTS.md`; skill fallback discovery: `.claude/skills/`, `.agents/skills/`, `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`; v2 beta package/config surfaces: `skills/*.md`, `skills/**/SKILL.md`, `skills` array with local paths or HTTP URLs |
| Our generators | `scripts/generate_opencode.py`, `scripts/generate_opencode_agents.py`, `scripts/generate_opencode_commands.py`, `scripts/generate_opencode_json.py`, `scripts/generate_opencode_plugin.py`, `scripts/generate_opencode_skills.py` |
| Native skills delivery | `profile=full` copies complete skill directories to the native project/global roots. Lower profiles use compatibility discovery and remove only toolkit-managed native copies. |
| Hook isolation | Tool hooks preserve native `sessionID` as normalized `session_id`; exit code 2 from a blocking pre-tool guard is raised back to OpenCode instead of being ignored. |
| Tracked plugin events | `session.created`, `session.compacted`, `session.deleted`, `message.updated`, `message.part.updated`, `tool.execute.before`, `tool.execute.after`, `permission.asked`, `command.executed` |
| Other capabilities | `opencode.json` config, primary + subagent modes, `@`-mention subagents, `/`-invocation commands, MCP (local + remote), plugin hooks in JS/TS, native `SKILL.md` discovery with Claude-compatible fallback, `permission.skill.*` matrix |
| Version probe | `opencode --version` |
| Watch item | The v2 plugin API is beta. It adds root-package skill files and configurable local/HTTP skill sources, but there is no migration: keep the stable JavaScript plugin generator until v2 stabilizes. |

---

## How the Registry is Consumed

```
┌─────────────────────────┐
│  ecosystem_tools.json   │  ← authoritative config (this doc mirrors it)
└──────────┬──────────────┘
           │ read
           ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│  ecosystem_doctor.py    │◄───►│  ecosystem-doctor-snapshot.json │  (last-seen state)
└──────────┬──────────────┘     └─────────────────────────────────┘
           │ emits
           ▼
    Drift report  (JSON or text)  →  human review  →  generator updates  →  commit
```

---

## Adding a New Tool

1. Append an entry to `scripts/ecosystem_tools.json` with all required fields (schema: `schema_version: 1`).
2. Add a generator under `scripts/generate_<tool>_*.py` (or link to an existing one).
3. Update this registry doc with a new section matching the format above.
4. Baseline the snapshot: `python3 scripts/ecosystem_doctor.py --update --tool <id>`.
5. Run the doctor again to confirm clean state: `python3 scripts/ecosystem_doctor.py --tool <id> --format text`.
6. Update tool count at the top of this document.

---

## Removing a Tool

1. Delete the tool's entry from `scripts/ecosystem_tools.json`.
2. Delete its section from this document.
3. Delete its snapshot entry from `benchmarks/ecosystem-doctor-snapshot.json` (or let the next `--update` prune it — currently not pruned automatically).
4. Decide whether to keep the generator (`scripts/generate_<tool>_*.py`) for backwards compatibility or delete it.
5. Remove references from `README.md`, `manifest.json` `description` field, and `kb/procedures/sop-maintenance.md` `Supported editors` line.

---

## Related

- [Ecosystem Sync SOP](../procedures/sop-ecosystem-sync.md) — how to use the doctor
- [MCP Editor Compatibility](./mcp-editor-compatibility.md) — MCP-specific subset
- `scripts/ecosystem_tools.json` — source of truth
- `scripts/ecosystem_doctor.py` — drift detector
- `benchmarks/ecosystem-doctor-snapshot.json` — last-seen state

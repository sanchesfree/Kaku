# Codex CLI vs Claude Code: A Practical Comparison

> Codex CLI and Claude Code compared on install, sign-in, config files, approvals, extension points and notifications, and how to run both on one repo.

Published 2026-10-09 · Tw93 · https://kaku.fun/blog/codex-vs-claude-code

Codex CLI and Claude Code are both terminal coding agents. Each one reads a repository, edits files, and runs commands on your machine. They differ in accounts and pricing, how the sandbox and approval prompts work, and configuration formats: TOML for Codex, JSON for Claude Code. Both support skills, hooks, and MCP.

## Comparison

Checked October 2026, against the [Codex CLI](https://developers.openai.com/codex/cli) page, the [config reference](https://developers.openai.com/codex/config-reference), the [Codex pricing page](https://developers.openai.com/codex/pricing), and the Claude Code [overview](https://code.claude.com/docs/en/overview), [settings](https://code.claude.com/docs/en/settings), and [hooks guide](https://code.claude.com/docs/en/hooks).

| | Codex CLI | Claude Code |
|---|---|---|
| Install | macOS/Linux: `curl -fsSL https://chatgpt.com/codex/install.sh \| sh`. The page also has Windows, npm, and Homebrew tabs | `curl -fsSL https://claude.ai/install.sh \| bash`, or `brew install --cask claude-code` |
| Login | Run `codex`, then Sign in with ChatGPT or another method | `claude` asks you to log in. An approved `ANTHROPIC_API_KEY` skips the prompt |
| Config file | `~/.codex/config.toml`, and `.codex/config.toml` in a trusted project | `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json` |
| Sandbox and approvals | `sandbox_mode`: `read-only`, `workspace-write`, `danger-full-access`. `approval_policy`: `on-request` or `never`. `/permissions` shows the sandbox | `allow`, `ask`, `deny`. Enter plan mode with `Shift + Tab`, `/plan` or `--permission-mode plan`. `auto` and `bypassPermissions` from user or managed settings, or `--permission-mode` |
| Models | `model`, for example `gpt-6.1-sol`. `/model` sets the model and reasoning effort | `/model` switches mid-session. `--model` applies to a single session. Examples on the settings page: `claude-sonnet-5`, `claude-opus-5-5` |
| MCP | `codex mcp` | Servers stored in `~/.claude.json` |
| Hooks | `hooks.json` or `[hooks]`, with `features.hooks` on | `hooks` in a settings file. `/hooks` lists them |
| Notifications | `tui.notification_method`: `auto` (default), `osc9`, `bel`. Condition defaults to `unfocused` | `preferredNotifChannel` in `~/.claude/settings.json`, or a `Notification` hook |
| Resume | `codex resume` | `claude --continue` or `claude --resume`. `claude --teleport` brings a web or mobile task into the terminal (claude.ai subscription) |

The native Claude Code install updates itself. Homebrew does not: `claude-code` is the stable cask, about a week behind, and `claude-code@latest` is current. `claude --version` prints the version once `claude` is on `PATH`. Settings files are strict JSON.

A project `.codex/config.toml` loads only after you trust the project, and it cannot set notifications, so `notification_method` stays in `~/.codex/config.toml`. `approval_policy = "untrusted"` is unsupported, `on-failure` is deprecated, and the docs advise against combining permission profiles (`:read-only`, `:workspace`, `:danger-full-access`) with `sandbox_mode`.

```toml
model = "gpt-6.1-sol"
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

Claude Code's example for lint and tests, while blocking `.env`, goes in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

`/status` confirms what loaded. Commit `.claude/settings.json` for the whole team, and keep personal overrides in `.claude/settings.local.json`. `permissions.allow` merges across those files. `ANTHROPIC_MODEL` overrides `model`, and `--model` overrides both for one session.

## Accounts and prices

Per OpenAI's [pricing page](https://developers.openai.com/codex/pricing), Codex is included in every ChatGPT plan, but the Free and Go plans list only the desktop app; the CLI, IDE extension, and web start at Plus. An OpenAI API key also works. It is billed at API rates and does not include cloud features such as GitHub code review and Slack.

Plus and Pro can buy credits after the included usage runs out, and a turn already running can finish, subject to fair use. Plan prices and per-model usage limits are on the [pricing page](https://developers.openai.com/codex/pricing).

Claude Code runs on a [Claude subscription](https://claude.com/pricing) (Pro, Max, Team, or Enterprise) or an [Anthropic Console](https://platform.claude.com/) account billed per use. The terminal, VS Code, and JetBrains also support third-party providers. The desktop app needs a paid subscription. More details are on [code.claude.com](https://code.claude.com/).

## Where each one fits

`codex exec` is the non-interactive command for scripts and CI. `/review` checks uncommitted changes, a commit, or a base branch, and leaves the working tree unchanged. `/init` writes `AGENTS.md`. Skills hold repeatable instructions, and plugins connect external tools.

Claude Code handles these workflows through `claude`, and `claude -p` accepts a one-shot prompt or a pipe:

```bash
git diff main --name-only | claude -p "review these changed files for security issues"
```

[`CLAUDE.md`](https://code.claude.com/docs/en/memory) at the project root is read at every session start. Skills are shared commands such as `/review-pr`. A `PreToolUse` hook that returns deny still blocks the tool in `bypassPermissions` mode and with `--dangerously-skip-permissions`. Claude Code also runs prompt hooks and agent hooks. Codex runs command hooks and MCP tool hooks, and skips prompt and agent handlers after parsing them.

[Plan mode](/blog/claude-code-plan-mode) blocks source edits until you approve, except in interactive terminal sessions with bypass permissions available. A [hook](/blog/claude-code-hooks) can block a tool call in any mode.

## One repository, both agents

Shared instructions can live in `AGENTS.md`. Codex creates it with `/init`. If that file is already in the repo, Claude Code can read it in place of a `CLAUDE.md`. Any `CLAUDE.md` you add is still loaded at the start of a Claude Code session. `model_instructions_file` replaces Codex's built-in instructions instead of `AGENTS.md`.

Both can edit the same checkout. Claude Code opens a git worktree for `--worktree`, for `isolation: "worktree"`, and for a background session (`WorktreeCreate`). Cleanup is covered in [git worktrees](/blog/claude-code-git-worktrees). Codex CLI has no matching flag. Install notes: [Codex CLI setup](/blog/codex-cli-setup), [install Claude Code](/blog/install-claude-code-mac).

## Side by side in Kaku

[Kaku](/docs/ai-coding) runs both CLIs as ordinary programs. `kaku ai` configures Claude Code, Codex, and other external tools, shows plan usage, writes a setting only when you edit it there, and does not add hooks or instructions on its own.

`Cmd + D` splits side by side, `Cmd + Shift + D` top and bottom, and `Cmd + Shift + Enter` zooms the pane you are reading. Closing a pane or tab asks first while Claude Code, Codex, or another long-running program is in the foreground. After a restart, those panes keep their last screen.

Codex needs no notification setting in Kaku. It rings the terminal bell, and Kaku turns that into a notification while Kaku is in the background. For Codex's own text, set the method in `~/.codex/config.toml`:

```toml
[tui]
notification_method = "osc9"
```

`auto` is the default, `osc9` carries one line, and `bel` is the bell. `tui.notification_condition` is `unfocused` unless you set `always`.

Claude Code needs no setting on Kaku 0.25.0 or later with Claude Code 2.1.295 or later, and before that it needs `"preferredNotifChannel": "ghostty"` in `~/.claude/settings.json`; [Claude Code notifications](/blog/claude-code-notifications) explains why. If nothing shows, click Kaku > Notification Settings and turn on Allow Notifications in System Settings.

## FAQ

### Can I run both in one repository?

Yes. Put shared instructions in `AGENTS.md`. Codex writes it with `/init`, and Claude Code can read it in place of a `CLAUDE.md`. Start the Claude Code session with `--worktree` when the two should not edit the same files. In Kaku, `Cmd + D` puts the CLIs in adjacent panes.

### Which one costs less?

Codex is included in every ChatGPT plan, but the CLI starts at Plus ($20 a month), since Free and Go list only the desktop app, and an OpenAI API key also works. Claude Code needs a Pro, Max, Team, or Enterprise subscription or a Console account. Check the [Codex pricing page](https://developers.openai.com/codex/pricing) and [claude.com/pricing](https://claude.com/pricing) for the latest rates.

### Why does only one of them notify me?

In Kaku, Codex's bell already becomes a notification while the window is in the background. Claude Code needs no setting on Kaku 0.25.0 or later with Claude Code 2.1.295 or later, and before that it needs `"preferredNotifChannel": "ghostty"`, as [Claude Code notifications](/blog/claude-code-notifications) explains. Kaku also needs Allow Notifications.

### Do both have hooks and MCP?

Yes. Codex uses `features.hooks` with `hooks.json` or `[hooks]`, and `codex mcp` for servers. Claude Code uses a `hooks` object in `settings.json` and stores MCP servers in `~/.claude.json`. Shared event names include `PreToolUse`, `PostToolUse`, `SessionStart`, and `Stop`.

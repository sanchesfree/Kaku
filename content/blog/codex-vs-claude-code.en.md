Codex CLI and Claude Code are both terminal coding agents. Each one reads a repository, edits files, and runs commands on your machine. They differ in the account and the price, in how the sandbox and approval prompts work, and in the config file: TOML for Codex, JSON for Claude Code. Both have skills, hooks, and MCP, and a lot of people keep both installed.

## Comparison

Checked October 2026, against the [Codex CLI](https://developers.openai.com/codex/cli) page, the [config reference](https://developers.openai.com/codex/config-reference), and the Claude Code [overview](https://code.claude.com/docs/en/overview), [settings](https://code.claude.com/docs/en/settings), and [hooks guide](https://code.claude.com/docs/en/hooks).

| | Codex CLI | Claude Code |
|---|---|---|
| Install | macOS/Linux: `curl -fsSL https://chatgpt.com/codex/install.sh \| sh`. The page also has Windows, npm, and Homebrew tabs | `curl -fsSL https://claude.ai/install.sh \| bash`, or `brew install --cask claude-code` |
| Login | `codex`, then Sign in with ChatGPT or another method | `claude` asks you to log in. An approved `ANTHROPIC_API_KEY` skips the prompt |
| Config file | `~/.codex/config.toml`, and `.codex/config.toml` in a trusted project | `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json` |
| Sandbox and approvals | `sandbox_mode`: `read-only`, `workspace-write`, `danger-full-access`. `approval_policy`: `on-request` or `never`. `/permissions` shows the sandbox | `allow`, `ask`, `deny`. Plan Mode from `/config`. `auto` and `bypassPermissions` from user or managed settings, or `--permission-mode` |
| Models | `model`, for example `gpt-6.1-sol`. `/model` sets the model and reasoning effort | `/model` switches mid-session. `--model` is one session. Examples on the settings page: `claude-sonnet-5`, `claude-opus-5-5` |
| MCP | `codex mcp` | Servers stored in `~/.claude.json` |
| Hooks | `hooks.json` or `[hooks]`, with `features.hooks` on | `hooks` in a settings file. `/hooks` lists them |
| Notifications | `tui.notification_method`: `auto` (default), `osc9`, `bel`. Condition defaults to `unfocused` | `Notification` hook. Channel setting is in the Kaku section |
| Resume | `codex resume` | `SessionStart` source `resume`. `claude --teleport` brings a web or mobile task into the terminal (claude.ai subscription) |

The native Claude Code install updates itself. Homebrew does not: `claude-code` is the stable cask, about a week behind, and `claude-code@latest` is current. `claude --version` prints a version once `claude` is on `PATH`. Settings files are strict JSON.

A project `.codex/config.toml` loads only after you trust the project, and it cannot set notifications, so `notification_method` stays in `~/.codex/config.toml`. `approval_policy = "untrusted"` is unsupported, `on-failure` is deprecated, and the docs say not to combine permission profiles (`:read-only`, `:workspace`, `:danger-full-access`) with `sandbox_mode`.

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

Checked October 2026 on the [Codex pricing page](https://developers.openai.com/codex/pricing). Codex is included in ChatGPT Free, Go, Plus, Pro, Business, Edu, and Enterprise, and ChatGPT Work uses the same allowance.

Free is $0/month and Go is $8/month. Both cards list GPT-6 Luna at Standard speed in the desktop app, subject to rollout. Plus is $20/month and lists Codex on the web, in the CLI, in the IDE extension, and on iOS, with GPT-6.1 Sol and GPT-6 Luna. Pro starts at $100/month, in tiers of $100, $200, and $500, and Ultrafast mode is on the $500 plan. Business is $20 per user per month billed annually for two or more users, or $25 billed monthly. An API key is billed at API rates, works in the CLI, SDK, or IDE extension, and does not include cloud features such as GitHub code review and Slack.

API rates are separate from included tasks. Plus and Pro can buy credits later, and a turn already running can finish, subject to fair use. Plus and Standard Business have estimated local messages per five hours, not fixed caps: GPT-6 Astra 5-45, GPT-6.1 Sol 15-160, GPT-6 Sol 15-150, GPT-6 Luna 350-3,000. Pro has no five-hour limit. Weekly limits may also apply.

The Claude Code overview prints no dollar rates. Most surfaces need a [Claude subscription](https://claude.com/pricing) or an [Anthropic Console](https://platform.claude.com/) account. The terminal, VS Code, and JetBrains also support third-party providers. The desktop app needs a paid subscription. More is on [code.claude.com](https://code.claude.com/).

## Where each one fits

`codex exec` is the non-interactive command for scripts and CI. `/review` checks uncommitted changes, a commit, or a base branch, and leaves the working tree unchanged. `/init` writes `AGENTS.md`. Skills hold repeatable instructions, and plugins connect outside tools.

Claude Code does that loop from `claude`, and `claude -p` takes a one-shot prompt or a pipe:

```bash
git diff main --name-only | claude -p "review these changed files for security issues"
```

[`CLAUDE.md`](https://code.claude.com/docs/en/memory) at the project root is read at every session start. Skills are shared commands such as `/review-pr`. A `PreToolUse` hook that returns deny still blocks the tool in `bypassPermissions` mode and with `--dangerously-skip-permissions`. Claude Code also runs prompt hooks and agent hooks. Codex runs command hooks and MCP tool hooks, and skips prompt and agent handlers after parsing them.

Plan Mode limits hook approvals for file edits until the plan is approved. See [plan mode](/blog/claude-code-plan-mode) and [Claude Code hooks](/blog/claude-code-hooks).

## One repository, both agents

Shared instructions can sit in `AGENTS.md`. Codex creates it with `/init`. If that file is already in the repo, Claude Code can read it in place of a `CLAUDE.md`. A `CLAUDE.md` you add is still loaded at the start of a Claude Code session. `model_instructions_file` replaces Codex's built-in instructions instead of `AGENTS.md`.

Both can edit the same checkout. Claude Code opens a git worktree for `--worktree`, for `isolation: "worktree"`, and for a background session (`WorktreeCreate`). Cleanup is in [git worktrees](/blog/claude-code-git-worktrees). The Codex CLI page has no matching flag. Install notes: [Codex CLI setup](/blog/codex-cli-setup), [install Claude Code](/blog/install-claude-code-mac).

## Side by side in Kaku

[Kaku](https://kaku.fun/docs/ai-coding) runs both CLIs as ordinary programs. `kaku ai` configures Claude Code, Codex, and the other external tools, shows plan usage, writes a setting only when you edit it there, and does not add hooks or instructions on its own.

`Cmd + D` splits vertically, `Cmd + Shift + D` horizontally, and `Cmd + Shift + Enter` zooms the pane you are reading. Closing a pane or tab asks first while Claude Code, Codex, or another long-running program is in the foreground. After a restart, those panes keep their last screen.

Codex needs no notification setting in Kaku. It rings the terminal bell, and Kaku turns that into a notification while Kaku is in the background. For Codex's own text, set the method in `~/.codex/config.toml`:

```toml
[tui]
notification_method = "osc9"
```

`auto` is the default, `osc9` carries one line, and `bel` is the bell. `tui.notification_condition` is `unfocused` unless you set `always`.

Claude Code 2.1.295 and later reports whether it is working, waiting or done, and Kaku 0.25.0 and later reads that report and notify you with no setting, so on those versions leave `preferredNotifChannel` at `auto`, since `ghostty` would post a second notification. Check with `claude --version` and `kaku --version`. With an older Claude Code or Kaku before 0.25.0, Claude Code only notifies terminals it recognizes, so Kaku stays silent until `~/.claude/settings.json` contains:

```json
{ "preferredNotifChannel": "ghostty" }
```

If nothing shows, open Kaku > Notification Settings and turn on Allow Notifications. macOS remembers a denial, and Kaku tells you the next time you return after a drop. Sequence details are in [Claude Code notifications](/blog/claude-code-notifications).

## FAQ

### Can I run both in one repository?

Yes. Put shared instructions in `AGENTS.md`. Codex writes it with `/init`, and Claude Code can read it in place of a `CLAUDE.md`. Start the Claude Code session with `--worktree` when the two should not edit the same files. In Kaku, `Cmd + D` puts the CLIs in adjacent panes.

### Which one costs less?

Checked October 2026. Codex is included with ChatGPT: Free $0, Go $8, Plus $20, Pro from $100. The Claude Code overview lists no price. Recheck the [Codex pricing page](https://developers.openai.com/codex/pricing) and [claude.com/pricing](https://claude.com/pricing).

### Why does only one of them notify me?

In Kaku, Codex's bell already becomes a notification. With Claude Code 2.1.295 and later on Kaku 0.25.0 or later, Claude Code's status reaches Kaku with `preferredNotifChannel` left at `auto`. Older versions of either need `"preferredNotifChannel": "ghostty"`. Kaku also needs Allow Notifications, and it shows these while its window is in the background.

### Do both have hooks and MCP?

Yes. Codex uses `features.hooks` with `hooks.json` or `[hooks]`, and `codex mcp` for servers. Claude Code uses a `hooks` object in `settings.json` and stores MCP servers in `~/.claude.json`. Shared event names include `PreToolUse`, `PostToolUse`, `SessionStart`, and `Stop`.

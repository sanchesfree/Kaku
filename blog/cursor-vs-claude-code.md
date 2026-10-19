# Cursor vs Claude Code: Editor Agent or Terminal Agent

> How Cursor and Claude Code differ in where you review changes, what you pay for, context, parallel sessions, and how to use both together.

Published 2026-09-25 · Tw93 · https://kaku.fun/blog/cursor-vs-claude-code

Cursor is an editor with a coding agent inside it. Claude Code is an agent that reads your codebase, edits files, and runs commands in the terminal and in an IDE extension, so those files stay ordinary project files you can open in Cursor or another editor. Choose based on where you want to read diffs and how many sessions you want running at once.

## How each one works

[Cursor](https://cursor.com/docs/models-and-pricing) describes itself as an AI editor and a coding agent. You use it to understand a repo, plan and build features with Plan Mode, fix bugs, and review changes by inspecting diffs and running checks before you merge. Plugins, skills, MCPs, and rules are added from one place.

[Claude Code](https://code.claude.com/docs/en/overview) runs in the terminal, in IDE extensions, in a desktop app, and in the browser. They share one engine, so a project's `CLAUDE.md`, settings, and MCP servers apply across all of them. In a project:

```bash
cd your-project
claude
```

It edits files, runs commands, and uses git for staging, commit messages, branches, and pull requests. `CLAUDE.md` in the project root is read at the start of every session. An existing `AGENTS.md` can stand in for it.

## What you pay for

Checked October 2026. The figures are on the pricing pages.

[Cursor's pricing page](https://cursor.com/pricing) lists Free, Plus, Premium, Super, and Ultra, plus Teams and Enterprise. Cursor and Grok Chat, Imagine, Voice, and Bot share one usage pool. It refreshes weekly, higher tiers include a larger pool, and you can buy a top-off past the included amount. Free includes limited agent requests and limited chat requests. Plus includes Grok models only. Premium and above include Grok usage, and third-party models are billed at API list price outside that allowance, with spending caps. Cloud agents and Bugbot code reviews start at Premium. The agent is on every plan, including Free.

Claude Code runs on a [Claude subscription](https://claude.com/pricing) (Pro, Max, Team, or Enterprise) or an [Anthropic Console](https://platform.claude.com/) account billed per use, and is also available through Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. [Anthropic's setup guide](https://code.claude.com/docs/en/setup) covers installing it and signing in. On a claude.ai plan, `/usage` shows usage for the current session and the week. An API key or third-party sign-in shows that session's cost and tokens. More pricing is on [code.claude.com](https://code.claude.com).

## Context and models

Cursor lists each model with a default context window and, for many, a larger maximum. That table changes as models are added, so check the current numbers on the [models page](https://cursor.com/docs/models-and-pricing) rather than trusting a copy.

Claude Code's context window depends on the model: 200K tokens by default, and 1M tokens on models with extended context. The extension shows how full the window is. Claude compacts when it needs to, and `/compact` does it on request. An `@` directory reference adds only the list of files, not their contents. Click the model name to switch, or type `/model` on Claude Code v2.1.284 or later.

## Parallel work and long sessions

A git worktree checks the repo out again in another directory on another branch, so `claude --worktree feature-auth` keeps two Claude Code tasks off the same files, and a second terminal uses another name. [Anthropic's worktree guide](https://code.claude.com/docs/en/worktrees) covers setup and cleanup.

**Open in New Tab** (`Cmd + Shift + Esc` on Mac) or **Open in New Window** opens another conversation, with its own history and context.

```bash
claude --continue
claude --resume
```

`--continue` reopens the newest session in this directory, or prints `No conversation found to continue` and exits. `--resume`, or `/resume` inside a session, lets you pick.

[claude.ai/code](https://claude.ai/code) runs long browser tasks, several at once, including repos you do not have locally. The desktop app shows sessions side by side and needs a paid subscription. Routines run in the cloud with the computer off. Create one on the web, in the desktop app, or with `/schedule`.

## Reviewing the changes

Cursor's review stays in the editor: inspect the diff, run checks, and catch problems before you merge.

In Claude Code, [plan mode](/blog/claude-code-plan-mode) reads the repo and writes nothing until you approve. You reach it with `Shift + Tab`, `/plan`, or `--permission-mode plan`.

The extension has several permission modes. Edit writes files without asking. Auto has a classifier review most actions. Manual waits on a side-by-side diff, where you accept, reject, or correct the proposal. **Accept this change** and **Reject this change** step through hunks on Claude Code v2.1.275 or later. A diff with more than 100 changes opens without those buttons.

`claude "commit my changes with a descriptive message"` makes the commit. Read it with `git diff`, or in [lazygit](/blog/lazygit-and-delta). From a message in the extension you can fork the conversation, rewind the files, or do both.

## Using Claude Code inside Cursor

The [overview](https://code.claude.com/docs/en/overview) links to install the extension in Cursor with `cursor:extension/anthropic.claude-code`, and in VS Code with `vscode:extension/anthropic.claude-code`. After that, **Open in New Tab** is in the Command Palette (`Cmd + Shift + P`). See [IDE integrations](https://code.claude.com/docs/en/ide-integrations). The terminal steps are from the [VS Code guide](https://code.claude.com/docs/en/vs-code).

Open the integrated terminal with Command and backtick, then run `claude`. The CLI uses the editor for diffs and diagnostics. The extension does not put `claude` on `PATH`, so the terminal needs the standalone CLI. `/ide` connects an outside terminal to VS Code. `claude --resume` continues a panel chat. If it is still open elsewhere, the panel warns that two copies can mix messages. Close the other one, or choose **Open here anyway**.

## Side by side in Kaku

In [Kaku](/docs/ai-coding), `Cmd + D` splits side by side and `Cmd + Shift + D` top and bottom, so Claude Code can sit next to a shell or next to Codex. `Cmd + Shift + Enter` zooms the pane you are reading. Closing a pane or tab asks first while Claude Code, Codex, or another long-running program is in the foreground.

`restore_previous_session` is on by default. Launch reopens the last tabs and panes, and the layout is saved within a minute of opening or closing a window, tab, or pane, so a crash or force quit restores that layout. After a restart, a pane that was running Claude Code or Codex keeps its last screen. Resume Claude Code with `claude --resume`. In the other pane, `codex resume` reopens a recent Codex chat from the same repository.

`Cmd + Click` opens a path such as `src/main.rs:42:7` even while the tool captures the mouse, the same reason it matters in [a terminal for Claude Code](/blog/best-terminal-for-claude-code). Point it at Cursor in `~/.config/kaku/kaku.lua`:

```lua
config.file_link_editor = "cursor --goto"
```

`Cmd + Shift + G` opens lazygit in the pane. Kaku finds the binary on `PATH` or in the usual Homebrew locations.

## FAQ

### Can I run Claude Code inside Cursor?

Yes. Use `cursor:extension/anthropic.claude-code`, or run `claude` in the integrated terminal. `claude --resume` continues a panel chat. The extension does not install `claude`.

### How do I stop two Claude Code sessions from editing the same files?

`claude --worktree feature-auth` creates another checkout on its own branch, and the next terminal uses a different name. [Anthropic's worktree guide](https://code.claude.com/docs/en/worktrees) covers setup and cleanup.

### How do I pick up a Claude Code session later?

`claude --continue` resumes the newest session in this directory. `claude --resume` or `/resume` opens a picker, and the extension warns you if that chat is still open somewhere else.

### Does a Cursor subscription include Claude and GPT models?

Plus includes Grok models only. From Premium up, third-party models such as Claude and GPT are billed at API list price, on top of the monthly price. Claude Code is billed separately through Pro, Max, Team, Enterprise, Console, or a provider such as Bedrock.

### What does Kaku keep after a restart?

Tabs and splits. Restore is on by default and is saved within a minute of a layout change, including after a crash. A Claude Code or Codex pane keeps its last screen. Closing it still asks first while that program is in the foreground.

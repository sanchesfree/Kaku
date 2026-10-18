Cursor is an editor with a coding agent inside it. Claude Code is an agent that reads your codebase, edits files, and runs commands, in the terminal and in an IDE extension, so those files stay ordinary project files you can open in Cursor or another editor. Choose by where you want to read the diff, and by how many sessions you want running at once.

## How each one works

[Cursor](https://cursor.com/docs) describes itself as an AI editor and a coding agent. You use it to understand a repo, plan and build features with Plan Mode, fix bugs, and review changes by inspecting diffs and running checks before you merge. Plugins, skills, MCPs, and rules are added from one place.

[Claude Code](https://code.claude.com/docs/en/overview) runs in the terminal, in IDE extensions, in a desktop app, and in the browser. Those share one engine, so a project's `CLAUDE.md`, settings, and MCP servers apply on each of them. In a project:

```bash
cd your-project
claude
```

It edits files, runs commands, and uses git for staging, commit messages, branches, and pull requests. `CLAUDE.md` in the project root is read at the start of every session. An existing `AGENTS.md` can stand in for it.

## What you pay for

Checked October 2026. The figures are on the pricing pages.

[Cursor's pricing page](https://cursor.com/pricing) lists Free, Plus, Premium, Super, and Ultra, plus Teams and Enterprise. Cursor and Grok Chat, Imagine, Voice, and Bot share one usage pool. It refreshes weekly, higher tiers include a larger pool, and you can buy a top-off past the included amount. Free is limited agent requests and limited chat requests. Plus includes Grok models only. Premium and above include Grok usage, and third-party models are billed at API list price outside that allowance, with spending caps. Cloud agents and Bugbot code reviews start at Premium. The agent is on every plan, including Free.

The overview prints no Claude Code rates. Most surfaces need a [Claude subscription](https://claude.com/pricing) or an [Anthropic Console](https://platform.claude.com/) account. The [extension](https://code.claude.com/docs/en/vs-code) takes Pro, Max, Team, or Enterprise, or Console, with no API key. The terminal, VS Code, and JetBrains also support Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. On a claude.ai plan, `/usage` shows the current session and the week. An API key or third-party sign-in shows that session's cost and tokens. More pricing is on [code.claude.com](https://code.claude.com).

## Context and models

Cursor lists each model with a default context window and, for many, a larger maximum, and that table changes as models are added, so check the current numbers on the [models page](https://cursor.com/docs) rather than trusting a copy (checked October 2026).

These Claude Code pages do not state one window size. The extension shows how full the window is. Claude compacts when it needs to, and `/compact` does it on request. An `@` file is included up to the Read tool's default of 25,000 tokens. A text file over 256KB is skipped, and a directory reference is only a listing. Click the model name to switch, or type `/model` on Claude Code v2.1.284 or later.

## Parallel work and long sessions

A git worktree is a separate checkout and branch, so two Claude Code tasks do not edit the same files. The repo needs a commit:

```bash
claude --worktree feature-auth
```

A second terminal uses another name. The command is in [common workflows](https://code.claude.com/docs/en/common-workflows). With no commits it fails with `Failed to resolve base branch "HEAD": git rev-parse failed`.

**Open in New Tab** (`Cmd+Shift+Esc` on Mac) or **Open in New Window** is another conversation, with its own history and context.

```bash
claude --continue
claude --resume
```

`--continue` reopens the newest session in this directory, or prints `No conversation found to continue` and exits. `--resume`, or `/resume` inside a session, lets you pick.

[claude.ai/code](https://claude.ai/code) runs long browser tasks, several at once, including repos you do not have locally. The desktop app shows sessions side by side and needs a paid subscription. Routines run in the cloud with the computer off. Create one on the web, in the desktop app, or with `/schedule`.

Checked October 2026, Cursor's cloud agents start at Premium.

## Reviewing the changes

Cursor's review stays in the editor: inspect the diff, run checks, and catch problems before you merge.

`claude --permission-mode plan` reads the repo and writes nothing until you approve. `Shift+Tab` reaches the same mode, and the status bar shows plan mode on. In the extension the plan opens as Markdown you can comment on. `/plan` switches to it on Claude Code v2.1.280 or later.

Edit automatically writes files without asking. Auto has a classifier review most actions. Manual waits on a side-by-side diff, where you accept, reject, or correct the proposal. **Accept this change** and **Reject this change** step through hunks on Claude Code v2.1.275 or later. A diff with more than 100 changes opens without those buttons.

`claude "commit my changes with a descriptive message"` makes the commit. Read it with `git diff`, or in [lazygit](/blog/lazygit-and-delta). From a message in the extension you can fork the conversation, rewind the files, or do both.

## Using Claude Code inside Cursor

The [overview](https://code.claude.com/docs/en/overview) installs the extension in Cursor with `cursor:extension/anthropic.claude-code`, and in VS Code with `vscode:extension/anthropic.claude-code`. After that, **Open in New Tab** is in the Command Palette (`Cmd+Shift+P`). See [IDE integrations](https://code.claude.com/docs/en/ide-integrations). The terminal steps are from the [VS Code guide](https://code.claude.com/docs/en/vs-code).

Open the integrated terminal with Command and backtick, then run `claude`. The CLI uses the editor for diffs and diagnostics. The extension does not put `claude` on `PATH`, so the terminal needs the standalone CLI. `/ide` connects an outside terminal to VS Code. `claude --resume` continues a panel chat. If it is still open elsewhere, the panel says two copies can mix the messages. Close the other one, or choose **Open here anyway**.

## Side by side in Kaku

In [Kaku](https://kaku.fun/docs/ai-coding), `Cmd + D` splits vertically and `Cmd + Shift + D` horizontally, so Claude Code can sit next to a shell or next to Codex. `Cmd + Shift + Enter` zooms the pane you are reading. Closing a pane or tab asks first while Claude Code, Codex, or another long-running program is in the foreground.

`restore_previous_session` is on by default. Launch reopens the last tabs and panes, and the layout is saved within a minute of opening or closing a window, tab, or pane, so a crash or force quit brings that layout back. After a restart, a pane that was running Claude Code or Codex keeps its last screen. Resume Claude Code with `claude --resume`. Codex in the other pane is in [the Codex CLI post](/blog/codex-cli-setup).

`Cmd + Click` opens a path such as `src/main.rs:42:7` even while the tool captures the mouse. Point it at Cursor in `~/.config/kaku/kaku.lua`:

```lua
config.file_link_editor = "cursor --goto"
```

`Cmd + Shift + G` opens lazygit in the pane. Kaku finds the binary on `PATH` or in the usual Homebrew locations.

## FAQ

### Can I run Claude Code inside Cursor?

Yes. Use `cursor:extension/anthropic.claude-code`, or run `claude` in the integrated terminal. `claude --resume` continues a panel chat. The extension does not install `claude`.

### How do I stop two Claude Code sessions from editing the same files?

`claude --worktree feature-auth` creates another checkout on its own branch. The repo needs a commit first, and the next terminal uses a different name.

### How do I pick up a Claude Code session later?

`claude --continue` resumes the newest session in this directory. `claude --resume` or `/resume` opens a picker, and the extension warns you if that chat is still open somewhere else.

### Does a Cursor subscription include Claude and GPT models?

Checked October 2026, Plus is Grok models only. From Premium up, third-party models such as the Claude and GPT rows on the docs index are API list price, on top of the monthly price. Claude Code is a separate bill: Pro, Max, Team, Enterprise, Console, or a provider such as Bedrock.

### What does Kaku keep after a restart?

Tabs and splits. Restore is on by default and is saved within a minute of a layout change, including after a crash. A Claude Code or Codex pane keeps its last screen. Closing it still asks first while that program is in the foreground.

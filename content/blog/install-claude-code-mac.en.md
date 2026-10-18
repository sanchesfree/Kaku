Install Claude Code on a Mac with the native installer, `curl -fsSL https://claude.ai/install.sh | bash`, or with Homebrew, `brew install --cask claude-code`. Open a new terminal in your project, run `claude`, and sign in through the browser with a Pro, Max, Team, or Enterprise subscription, or a Console account. A native install updates in the background, and `claude update` installs an update immediately. A Homebrew install does not auto-update, so the upgrade command is `brew upgrade claude-code` (checked October 2026).

## Install options

Claude Code needs macOS 13.0 or later, 4 GB+ RAM, x64 or ARM64, and an internet connection. The [setup page](https://code.claude.com/docs/en/setup) recommends the native installer. The download shows no progress. When it finishes, open a new terminal and run `claude --version`.

Latest channel, the default:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Stable is typically about a week behind and skips releases with major regressions. The channel you pass here becomes the default for later auto-updates:

```bash
curl -fsSL https://claude.ai/install.sh | bash -s stable
```

Homebrew picks the channel by cask name. `claude-code` tracks stable. `claude-code@latest` tracks latest:

```bash
brew install --cask claude-code
brew install --cask claude-code@latest
```

npm installs the same native binary. It asks for Node.js 22 or later. Older Node versions print `EBADENGINE` but still finish, because `claude` does not run on Node. Optional dependencies have to be allowed. Do not use `sudo npm install -g`. It can cause permission and security problems.

```bash
npm install -g @anthropic-ai/claude-code
```

If the shell says `claude` is not found, the install directory is not on `PATH` yet. The native launcher is `~/.local/bin/claude`, a symlink into `~/.local/share/claude/versions/`.

## Sign in

`claude` starts in the current directory. The first launch sends you to the browser. The free claude.ai plan does not include Claude Code. Pro, Max, Team, Enterprise, and Console do. Console is API access with pre-paid credits, and the first Console login creates a workspace named "Claude Code". Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry work too.

If `ANTHROPIC_API_KEY` is set and you approve that key when asked, the login prompt is skipped. `claude auth login --console` signs in with Console billing rather than a subscription. Inside a session, `/login` switches accounts. Credentials are stored after login. See the [quickstart](https://code.claude.com/docs/en/quickstart).

## Confirm the install

`claude doctor` prints install health, settings-file validation errors, suggested fixes, and the last update attempt, without starting a session. `/doctor` inside a session can apply fixes.

## Updates and release channels

A native install checks for updates at startup and periodically while it runs. The download happens in the background and takes effect the next time you start Claude Code. `claude update` applies an update immediately. It reports `Successfully updated from <old version> to version <new version>`, or `Claude Code is up to date (<version>)` when nothing is newer. A Homebrew install reports `Claude is up to date!` instead.

Upgrade the cask you installed:

```bash
brew upgrade claude-code
brew upgrade claude-code@latest
```

Set `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` to `1`. Claude Code then runs that upgrade in the background when a new version is available, and shows a restart prompt on success. You may be told about an update before the cask has it. If the upgrade fails, wait and try again.

npm auto-updates when its global directory is writable. Otherwise, Claude Code shows a one-time notice at startup, and `claude doctor` lists fixes. Upgrade with `npm install -g @anthropic-ai/claude-code@latest`. Avoid `npm update -g`, which can stay on the old semver range.

On a native install, `autoUpdatesChannel` chooses the channel for auto-update and for `claude update`. `"latest"` is the default. `"stable"` is typically about a week behind. Set it under Auto-update channel in `/config`, or in `~/.claude/settings.json`:

```json
{
  "autoUpdatesChannel": "stable"
}
```

`claude install stable` and `claude install latest` install the native binary on that channel. Homebrew ignores `autoUpdatesChannel` and follows the cask name. A new model can require a version newer than stable serves. Switch to latest to run it.

To stop the background check on a native or npm install, set `DISABLE_AUTOUPDATER` to `"1"`:

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

`claude doctor` should then show `disabled (set by env: DISABLE_AUTOUPDATER)` on the Auto-updates line. `claude update` and `claude install` still work. Set `DISABLE_UPDATES` to block those as well.

## Uninstall, or move from npm to the native installer

Remove a native install with:

```bash
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
```

For Homebrew, run `brew uninstall --cask claude-code`, or `brew uninstall --cask claude-code@latest` if that is the cask you installed. For npm, run `npm uninstall -g @anthropic-ai/claude-code`.

To move from npm to the native installer, uninstall the npm package, run `curl -fsSL https://claude.ai/install.sh | bash`, then open a new terminal and run `claude --version`. Leave `~/.claude` in place to keep settings and session history. Deleting `~/.claude` and `~/.claude.json` removes settings, allowed tools, MCP server configurations, and session history. The VS Code extension, the JetBrains plugin, and the Desktop app recreate that directory the next time they run. If `claude` still starts, you likely have a second installation or a leftover shell alias.

## Newlines and notifications

Enter submits the prompt, and `Ctrl + J`, or `\` then Enter, inserts a newline in every terminal. [The best terminal for Claude Code](/blog/best-terminal-for-claude-code) lists where `Shift + Enter` works with no setup and where `/terminal-setup` has to run once. In VS Code, Cursor and Devin Desktop that command also sets `terminal.integrated.gpuAcceleration` to `"off"`, which you undo by setting it back to `"auto"` and reloading the window. By default a desktop notification is sent only in Ghostty, Kitty and iTerm2, and [Claude Code notifications](/blog/claude-code-notifications) covers the setting for other terminals, the iTerm2 alert option, SSH and [tmux](/blog/tmux-alternative-mac).

## In Kaku

Kaku 0.25.0 or later with Claude Code 2.1.295 or later needs no notification setting, and Kaku before 0.25.0 needs `"preferredNotifChannel": "ghostty"` in `~/.claude/settings.json`. [Claude Code notifications](/blog/claude-code-notifications) explains why, and what to check when none appear.

`Shift + Enter` and `Cmd + Enter` insert a newline in the prompt.

`kaku ai` opens the AI settings panel. It configures Claude Code, Codex, Gemini CLI, Copilot CLI, and Kimi Code, shows their plan usage, and sets up Kaku Assistant. Kaku only changes a tool's settings when you edit them there, keeps the fields you wrote yourself, and never adds hooks or instructions to your agents on its own.

```bash
kaku ai
```

## FAQ

### Does the free Claude plan include Claude Code?

No. You need a Pro, Max, Team, Enterprise, or Console account. The free claude.ai plan does not include Claude Code.

### Does Homebrew update Claude Code by itself?

No. Run `brew upgrade claude-code` or `brew upgrade claude-code@latest`. Set `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` to `1` to have Claude Code run that upgrade in the background.

### Why does the shell say claude is not found?

Open a new terminal and run `claude --version`. The native launcher is `~/.local/bin/claude`.

### Shift + Enter sends the message. How do I insert a newline?

`Ctrl + J`, or `\` then Enter, works in every terminal. Where `Shift + Enter` does not, run `/terminal-setup` once outside tmux. That covers VS Code, Cursor, Devin Desktop, Alacritty before 0.16, and Zed.

### How do I stop Claude Code from updating itself?

On a native or npm install, set `DISABLE_AUTOUPDATER` to `"1"` under `env` in `~/.claude/settings.json`. The background check stops. `claude update` still runs until you set `DISABLE_UPDATES`.

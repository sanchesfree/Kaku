Ghostty, iTerm2 and WezTerm are all good terminals, and the real difference between them is how you configure them. iTerm2 is configured through a settings window with more features than either of the others, Ghostty is a fast native app configured with a text file of `key = value` lines, and WezTerm uses a Lua script that can compute its own config. Pick iTerm2 if you depend on `tmux -CC` or triggers, Ghostty if you want something fast that you configure once, and WezTerm if you want to program your terminal. The sections below compare them on splits, images, notifications, release cadence and AI coding tools, as of 2026-10-17: iTerm2 3.7.6, Ghostty 1.3.1, and WezTerm 20240203 plus nightly builds. Warp, Kitty, Alacritty and Terminal.app are covered in [the best terminal for Mac](/blog/best-terminal-for-mac).

[[figure:terminal-config-models|iTerm2 is configured in a settings window saved to a plist, Ghostty in a text file of key = value lines, WezTerm in a Lua script with hot reload|The configuration model decides more about daily use than any single feature.]]

## Configuration

**iTerm2** keeps everything in a settings window, saved to a property list. Profiles let one app hold several setups, and almost every behavior has a checkbox somewhere. That depth is its strength, and keeping it in sync across machines means exporting profiles or pointing iTerm2 at a folder of saved preferences.

**Ghostty** reads `~/.config/ghostty/config.ghostty` (named `config` before 1.2.3), a plain list of settings:

```ini
font-family = JetBrains Mono
font-size = 15
macos-option-as-alt = true
```

`Cmd + Shift + ,` reloads it, and `ghostty +show-config --default --docs` prints every option with its documentation. It is the easiest of the three to read and to keep in dotfiles.

**WezTerm** runs `~/.wezterm.lua` and uses whatever table it returns:

```lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()
config.font = wezterm.font 'JetBrains Mono'
config.font_size = 15
return config
```

Because the config is a program, it can pick a color scheme from the system appearance, build a status bar from events, or define keys that run Lua. It reloads on save. The cost is that a typo is a Lua error, not an ignored line.

## Splits, tabs and tmux

All three have tabs and splits. They differ in how they treat tmux.

- **iTerm2** has `tmux -CC`, which shows a tmux session as native windows, tabs and splits. You get tmux's persistence on a remote server with the terminal's own scrolling and copying. Nothing else on macOS does this as well.
- **WezTerm** has its own multiplexer, so a WezTerm session can keep running on a remote machine without tmux, as long as WezTerm is installed there too.
- **Ghostty** has native splits and works with tmux the ordinary way, without a special integration.

## Images

| | iTerm2 | Ghostty | WezTerm |
|---|---|---|---|
| iTerm2 inline images (`imgcat`) | Yes | No | Yes |
| Kitty graphics protocol | Yes | Yes | Yes |
| Sixel | Yes | No | Yes |

Most modern tools that show images in the terminal speak the Kitty protocol, so all three cover the common cases.

## Notifications

All three can turn an escape sequence into a macOS notification, but AI coding tools do not treat them alike. Claude Code's default `auto` channel works in Ghostty, and in iTerm2 once you enable escape sequence alerts in its settings, while in WezTerm it stays silent until you set `preferredNotifChannel` to `terminal_bell` or add a hook. The [notification guide](/blog/claude-code-notifications) has the details for each.

## Restarting

iTerm2 can restore windows and keep sessions alive across a restart of the app. Ghostty uses macOS window restoration through `window-save-state`, bringing back windows, tabs, splits and working directories. WezTerm does not restore sessions on its own; people usually add a plugin or rely on its multiplexer.

## Release cadence

iTerm2 and Ghostty ship regular releases. WezTerm's last stable release is from February 2024. Development continues, but fixes only reach users through nightly builds, so on WezTerm you either live on nightly or accept older bugs.

## Running Claude Code and Codex

All three support `Shift + Enter` for a new line in Claude Code without setup, and all three ask before closing a pane with a running program, so the differences come down to notifications, as above, and how much setup each needs before a long agent session feels right, which [the best terminal for Claude Code](/blog/best-terminal-for-claude-code) goes through in more detail.

Kaku sits next to WezTerm here. It is a fork that keeps the Lua config and the engine, sets up the parts AI coding CLIs use, such as `Cmd + Click` on `path:line` and an agent's last screen after a restart, and ships them as regular macOS releases instead of nightly builds. If you like WezTerm's model but want it ready for Claude Code and Codex, it is worth a try.

## FAQ

### Is Ghostty faster than iTerm2?

Ghostty is built around GPU rendering and generally feels lighter. iTerm2 also renders with Metal, and for most daily work both are fast enough that features matter more than speed.

### Which of the three works best with tmux?

iTerm2, because `tmux -CC` turns tmux windows into native tabs and splits. With Ghostty or WezTerm, tmux works the usual way.

### Is WezTerm still maintained?

Yes, development continues on GitHub, but the latest stable release is from February 2024 and newer changes ship as nightly builds.

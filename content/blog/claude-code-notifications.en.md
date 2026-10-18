If Claude Code never tells you it finished or that it is waiting for permission, the cause is almost always the same: with its default settings it only sends desktop notifications in three terminals, iTerm2, Ghostty and Kitty. Everywhere else it stays silent until you tell it which channel to use. Codex has the opposite default and rings the terminal bell, which some terminals turn into a notification and others only flash. This post covers the setting that fixes each case, the macOS permission that blocks both, and what happens between the escape sequence and Notification Center.

## The quick fix for Claude Code

Open `~/.claude/settings.json` and set `preferredNotifChannel` to a channel your terminal understands. The values Claude Code accepts are `auto`, `terminal_bell`, `iterm2`, `iterm2_with_bell`, `kitty`, `ghostty` and `notifications_disabled`.

| Terminal | What to set |
|---|---|
| iTerm2 | Nothing in Claude Code. In iTerm2, open Settings > Profiles > Terminal, check Notification Center Alerts, then under Filter Alerts enable Send escape sequence-generated alerts |
| Ghostty, Kitty | Nothing, `auto` already works |
| Kaku | `"ghostty"` |
| Terminal.app | `auto` rings the bell only when the audible bell is off; `/terminal-setup` turns it off for you |
| WezTerm, Warp, VS Code | `"terminal_bell"`, or a Notification hook |

For Kaku the whole change is one line:

```json
{ "preferredNotifChannel": "ghostty" }
```

## The quick fix for Codex

Codex works in Kaku without changes. With its default settings it rings the terminal bell when it needs you, and Kaku turns a bell in a background window into a notification. The text of that notification is generic, built from the last command or the pane title. To see Codex's own message instead, switch it to the OSC 9 sequence in `~/.codex/config.toml`:

```toml
[tui]
notification_method = "osc9"
```

`notification_method` takes `auto`, `osc9` or `bel`. Two neighbours are worth knowing: `notifications` turns them on or off, or limits them to certain events, and `notification_condition` decides whether they fire only while the terminal is unfocused, the default, or always.

## When nothing shows up at all

If the setting is right and still nothing appears, macOS is the next suspect. A notification from a terminal is shown by the terminal app, so the terminal itself needs permission. In System Settings > Notifications, find your terminal and turn on Allow Notifications. In Kaku the same page is one click away under Kaku > Notification Settings.

macOS only asks for that permission once. If you clicked Don't Allow at some point, it never asks again, and every later notification is dropped without a trace. Kaku checks for that case and, after a notification was dropped, tells you the next time you switch back to it.

Two more causes are common:

- **tmux.** tmux swallows the sequences unless you add `set -g allow-passthrough on` to `~/.tmux.conf` and reload it with `tmux source-file ~/.tmux.conf`.
- **You were looking at it.** Most terminals, Kaku included, suppress notifications from the window in front of you, and Codex by default only notifies while the terminal is unfocused. Test with the window in the background.

## How a notification gets from the agent to macOS

Neither Claude Code nor Codex talks to Notification Center. They write a short escape sequence into the terminal, the same way they write colors, and the terminal decides what to do with it.

[[figure:claude-code-notifications|Claude Code, Codex and your own scripts send sequences or a bell to Kaku, which turns them into a macOS notification only while Kaku is in the background|Every source ends up in the same place: a sequence the terminal reads and turns into a notification.]]

There are a few sequences in use. OSC 9, which started in iTerm2, carries one line of text. OSC 777 carries a title and a body. The plain bell character carries nothing but the fact that something happened. Ghostty and Kaku handle both OSC 9 and OSC 777, while Kitty uses its own OSC 99. That spread is why Claude Code keeps a list of channels instead of one switch.

In Kaku all three paths meet in one place. The `notification_handling` setting decides which ones become notifications:

```lua
-- Default: only while the Kaku window is in the background
config.notification_handling = "AlwaysShow"
-- Also notify for tabs or panes you are not looking at:
-- config.notification_handling = "SuppressFromFocusedTab"
-- config.notification_handling = "SuppressFromFocusedPane"
-- Never:
-- config.notification_handling = "NeverShow"
```

A bell in a background window becomes a notification too, and bells also add to the badge on Kaku's Dock icon, so you can see that something rang even after the notification is gone.

## Notifications for your own scripts

Because a notification is just a sequence, any script can send one. This is handy at the end of a long build or test run:

```bash
# One line of text (OSC 9)
printf '\e]9;%s\a' "Tests finished"

# Title and body (OSC 777)
printf '\e]777;notify;%s;%s\a' "Build" "Release build finished"
```

Run it with the terminal in the background and it arrives like any other notification. Inside tmux the passthrough setting above still applies.

## FAQ

### Why does Claude Code send notifications in iTerm2 but not in my terminal?

With `preferredNotifChannel` left at `auto`, Claude Code only sends desktop notifications to iTerm2, Ghostty and Kitty. Set the channel explicitly, for example `ghostty` in Kaku or `terminal_bell` elsewhere.

### Do Claude Code notifications work over SSH?

Yes. The sequence travels back through the SSH connection to the terminal on your Mac, which shows the notification, as long as that terminal understands the channel you picked.

### Can I also play a sound when Claude needs me?

Yes, with a [Notification hook](https://code.claude.com/docs/en/terminal-config#play-a-sound-with-a-notification-hook) in `~/.claude/settings.json`. Hooks run alongside the built-in notification:

```json
{
  "hooks": {
    "Notification": [
      { "hooks": [{ "type": "command", "command": "afplay /System/Library/Sounds/Glass.aiff" }] }
    ]
  }
}
```

### Why do I get notifications for the window I'm looking at?

Some terminals show every notification. In Kaku the default `AlwaysShow` only shows them while the window is in the background; the `Suppress` options also cover tabs and panes you are not looking at.

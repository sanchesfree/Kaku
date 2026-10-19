A new tab in Kaku opens in the current folder on a local Mac because the terminal can read the working directory of the process group that owns the pane, which at a prompt is the shell. OSC sequences are the other report: the shell writes a short escape sequence, and a terminal that understands it keeps the data and does not print the sequence. In Kaku 0.25.0, fish prints OSC 7 for the directory and OSC 133 to mark the prompt, while the zsh integration prints OSC 1337 user variables for the assistant and does not print OSC 7 or OSC 133. Notifications are OSC 9 and OSC 777, a separate path, and the Claude Code and Codex settings for them are in [Claude Code notifications](/blog/claude-code-notifications).

## What the terminal does with the bytes

An OSC sequence starts with ESC and `]`, then a number, then parameters separated by semicolons, and ends with BEL (`\a`) or ST (`ESC \`). The terminal consumes the sequence. If you can read `]7;file://` in the scrollback, the ESC byte was lost before Kaku saw the stream, and the rest printed as ordinary characters.

Kaku keeps each sequence on the pane. OSC 7 sets the working directory, and that value is used before the directory read from the process. OSC 133 labels later cells as prompt, input or output, and can store an exit status. OSC 1337 stores a named variable. OSC 9 and OSC 777 become a macOS notification while the window is in the background. OSC 8 marks a span of text as a link, which `Cmd + Click` opens.

[[figure:shell-integration-osc|Kaku reads OSC 7 into the working directory used for a new tab, OSC 133 into prompt zones, OSC 1337 into the assistant hook, and OSC 9, OSC 777 and OSC 8 into a notification or a clickable link|The terminal keeps each sequence as pane state, and a local Mac can also fill the directory from the process when OSC 7 never arrives.]]

OSC 7 is the directory report. [iTerm2 documents it](https://iterm2.com/documentation-escape-codes.html) as a file URL, `file://hostname/path`, a synonym for its RemoteHost and CurrentDir sequences. [WezTerm](https://wezterm.org/shell-integration.html) uses that URL for new tabs, and so does Kaku. The three inherit switches default to on ([configuration](/docs/configuration)):

```lua
config.window_inherit_working_directory = true
config.tab_inherit_working_directory = true
config.split_pane_inherit_working_directory = true
```

`Cmd + T` opens a tab in that folder, `Cmd + D` and `Cmd + Shift + D` split there, and `Cmd + Shift + T` reopens the last closed tab in the folder it had. On a local Mac, Kaku asks macOS (`proc_pidinfo`) when no OSC 7 has arrived, so the process directory is enough. Over SSH that process stays in the folder where you ran `ssh`. A remote shell that prints OSC 7 replaces it with the remote path, but a new tab is still a local shell, and Kaku reads only the path part of the URL, so that tab tries the same path on your Mac.

OSC 133 is the FinalTerm prompt markup, documented by [iTerm2](https://iterm2.com/documentation-escape-codes.html). `133 ; A` starts the prompt. `133 ; B` ends the prompt and starts what you type. `133 ; C` starts the command's output. `133 ; D ; <status>` is the exit status. Kaku reads a missing status as 0. Kaku is built on WezTerm, and the action that scrolls to an earlier prompt zone is `ScrollToPrompt`. [WezTerm leaves it unbound](https://wezterm.org/config/lua/keyassignment/ScrollToPrompt.html), and Kaku 0.25.0 does too. iTerm2's installer draws a mark at each prompt and jumps with `Cmd + Shift + Up` and `Cmd + Shift + Down`. Kaku does not install that script.

OSC 1337 `SetUserVar` is iTerm2's pane variable: a plain name and a base64 value. Kaku's assistant listens for `kaku_last_cmd` and `kaku_last_exit_code` on this channel, and a failed command can offer a fix you paste with `Cmd + Shift + E`. That is a different channel from OSC 133. Opening the chat with `Cmd + L` can also attach up to 51 rows of the last command's output, but only when marker C has recorded where the output started and marker D has recorded a non-zero status. The next `133 ; A` clears both. Fish prints A on the next prompt and never prints D, and the zsh file prints neither, so that slice stays empty.

OSC 9 is iTerm2's one-line notification, `9 ; message`. OSC 777 is `777 ; notify ; title ; body`, the form [WezTerm documents](https://wezterm.org/config/lua/config/notification_handling.html). A number after `9 ;`, such as `9 ; 4`, is a ConEmu progress command, and Kaku does not treat it as a notification. OSC 8, from the [VTE and iTerm2 proposal](https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda), makes the text between `8 ; ; URL` and `8 ; ;` a link even when those words are not a URL. `Cmd + Click` opens it. Bare URLs and paths such as `src/main.rs:42` already open without OSC 8.

## How Kaku wires the shell

`kaku init` writes a managed file and points the shell at it. For zsh it appends two lines to `~/.zshrc`. One puts `~/.config/kaku/zsh/bin` on `PATH`. The other is:

```bash
[[ -f "$HOME/.config/kaku/zsh/kaku.zsh" ]] && source "$HOME/.config/kaku/zsh/kaku.zsh" # Kaku Shell Integration
```

For fish it writes `~/.config/fish/conf.d/kaku.fish`, which sources `~/.config/kaku/fish/kaku.fish`. `kaku doctor` checks that this integration is present. Starship and Smart Tab start only inside Kaku (`TERM_PROGRAM=Kaku`, or tmux started from a Kaku shell). The plugins those files load are covered in [a zsh setup without Oh My Zsh](/blog/zsh-without-oh-my-zsh).

On `fish_prompt` the fish file prints OSC 7 as `file://` plus the hostname plus `$PWD`, and OSC `133 ; A`. On `fish_preexec` it prints OSC `133 ; C`. It does not print B or D. Both shells print OSC 1337 user variables only inside a Kaku pane: the spawn sets `WEZTERM_PANE`, and `TERM` stays `xterm-256color` so a remote host without a `kaku` terminfo entry still works. The value is a token from `~/.config/kaku/ai_inline_capability`, a colon, and the text, then base64. Without that token, `SetUserVar` does not start an assistant request. `KAKU_AUTO_DISABLE` turns the hooks off. Inside tmux the printf uses tmux's passthrough wrapper, which still needs `allow-passthrough`.

The zsh file sends those user variables from `preexec` and `precmd` and does not print OSC 7 or OSC 133. The app bundle also contains `kaku.sh`, the WezTerm script for bash and zsh, which prints OSC 7, the A/B/C/D markers, and `WEZTERM_PROG`. `kaku init` does not source it, and it rewrites `PS1` on every prompt to add the markers.

## Check it with printf

Directory. From a zsh that is not already in `/tmp` (fish prints its own OSC 7 at the next prompt and overwrites the test):

```bash
printf '\033]7;file://%s/tmp\033\\' "$(hostname)"
```

`Cmd + T`, then `pwd`, should print `/tmp`. zsh prints no OSC 7 of its own, so that path stays until another OSC 7 arrives. One whose value is not a URL fails to parse and clears it, and new tabs follow the shell process again:

```bash
printf '\033]7;x\033\\'
```

Prompt marks. Kaku reloads `~/.config/kaku/kaku.lua` on save. Append a binding. Assigning a new `config.keys` table would drop every default:

```lua
table.insert(config.keys, {
  key = 'UpArrow',
  mods = 'SHIFT',
  action = wezterm.action.ScrollToPrompt(-1),
})
```

Mark two prompts and jump:

```bash
printf '\033]133;A\a'; echo first
printf '\033]133;A\a'; echo second
```

Scroll until `first` is off the top, then press `Shift + Up`. The viewport moves to that marker. Fish already prints A at each prompt, so the key moves between real prompts there. On zsh it only hits markers something printed.

Notifications. Leave the window in the background:

```bash
printf '\e]9;%s\a' "OSC 9"
printf '\e]777;notify;%s;%s\a' "Build" "OSC 777"
```

`notification_handling` defaults to `AlwaysShow`, which in Kaku still requires an unfocused window.

A link whose text is not the URL:

```bash
printf '\e]8;;https://kaku.fun\e\\Kaku\e]8;;\e\\\n'
```

`Cmd + Click` on the word Kaku opens the site.

## What fails, and how to tell

tmux reads escape sequences itself and passes on only those wrapped in its passthrough form, and only when `~/.tmux.conf` contains `set -g allow-passthrough on`, reloaded with `tmux source-file ~/.tmux.conf`. Kaku's hooks wrap the OSC 1337 user variables that way. Fish's OSC 7 and OSC 133, and the printf checks above, are not wrapped, so inside tmux they stay with tmux. Kaku's `~/.config/kaku/tmux/kaku.tmux.conf` turns the mouse on and keeps `KAKU_SESSION`. It does not set passthrough. [tmux on a Mac](/blog/tmux-alternative-mac) is still the tool for a session that must survive a dropped SSH connection, and this line is part of keeping it.

A bare Enter does not repeat the last failure, because the exit code is sent only after a command that ran. Ctrl+C and a zero exit do not ask for a fix. If `Shift + Up` does nothing, no prompt zone sits above the viewport. On zsh that is normal until something prints OSC 133 A.

## FAQ

### Does a new tab follow an SSH session's remote directory?

No. A new tab is a local shell on your Mac. When the remote shell prints OSC 7, Kaku keeps only the path part of that URL, so the new tab tries the same path on the Mac. Without OSC 7 it opens where the `ssh` process is.

### Why does `]133;A` show up as text?

The ESC byte was lost before Kaku saw the stream, so the rest printed as ordinary characters.

### Can another program trigger an assistant fix by printing OSC 1337?

The hook sends `kaku_last_cmd` only with the token from `~/.config/kaku/ai_inline_capability` prefixed to the command. A sequence printed by some other program does not have that token, and a missing file means the hook sends nothing.

### Is iTerm2's Install Shell Integration the same setup?

iTerm2's menu installs its own script, which also keeps command history and can download with scp. Kaku does not ship that menu. Prompt jumping in Kaku is the `ScrollToPrompt` binding above.

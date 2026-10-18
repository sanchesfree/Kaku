On a Mac, Ghostty reads a plain text file of `key = value` lines at `~/.config/ghostty/config.ghostty`, or `~/.config/ghostty/config` on versions before 1.2.3. Press `Cmd + Shift + ,` to reload it, and run `ghostty +show-config --default --docs` to print every option with its documentation. Ghostty works without a config at all, so the useful settings are the few that fit your taste: font, theme, window chrome, keybinds, the Option key and the quick terminal.

## Where the config file lives

Ghostty looks in two places on macOS, checked October 2026 against the [configuration docs](https://ghostty.org/docs/config):

```text
~/.config/ghostty/config.ghostty
~/Library/Application Support/com.mitchellh.ghostty/config.ghostty
```

The first is the XDG path, which honors `$XDG_CONFIG_HOME` when it is set. Both can exist. Ghostty loads the XDG file first and the macOS one after it, so a value in `Application Support` wins. Most people keep one file in `~/.config/ghostty/` because it is easier to track in dotfiles. If neither file exists, Ghostty runs on its defaults, which already include JetBrains Mono and built-in Nerd Font symbols.

## Syntax and reloading

Each line is a key, an equals sign and a value. Comments start with `#` and must sit on their own line. Keys are lowercase and case-sensitive, quotes around values are optional, and an empty value resets that key to its default:

```ini
# ~/.config/ghostty/config.ghostty
font-family = "JetBrains Mono"
background = 282c34
font-family =
```

Every key also works as a command-line flag, so `ghostty --font-family="JetBrains Mono"` tests a value without touching the file. To split the config, add `config-file` lines. A relative path is resolved next to the current file, and a leading `?` makes the file optional, which suits machine-specific overrides:

```ini
config-file = ?local.ghostty
```

`config-file` lines are processed at the end of the file that contains them, so the included file wins over anything set after the `config-file` line.

`Cmd + Shift + ,` reloads the config, and you can rebind it with the `reload_config` action. Some options apply only to new windows or tabs, and a few need a full restart. The reference notes this for each option.

## Font and theme

`ghostty +list-fonts` prints the family names Ghostty can see. Repeat `font-family` to build a fallback list, where the first line is the main face and later lines fill in characters it lacks:

```ini
font-family = "JetBrains Mono"
font-size = 14
```

Because repeated lines append, a theme or included file can leave families you did not expect. Start with `font-family = ""` to clear the list before you set it. Bold and italic come from the same family unless you set `font-family-bold` or `font-family-italic`. `font-size` is in points and accepts halves such as `13.5`. Ghostty already bundles Nerd Font symbols, so a symbols font such as Symbols Nerd Font Mono only needs its own `font-family` line if you want a different face for the icons, and the [Nerd Fonts guide](/blog/nerd-fonts-mac) covers that case.

Themes ship with the app, and `ghostty +list-themes` lists them. To follow the macOS light and dark appearance, give both in one line:

```ini
theme = light:Rose Pine Dawn,dark:Rose Pine
```

Both halves are required in that form, and their order does not matter. Your own theme files go in `~/.config/ghostty/themes/`. Any `background`, `foreground` or `palette` line in your config overrides the theme's colors. A theme file can set any option, so only use ones from sources you trust.

## Window padding, titlebar and decorations

Padding is measured in points, so it scales with the display:

```ini
window-padding-x = 12
window-padding-y = 8,4
window-padding-balance = true
```

Two comma-separated values set left and right, or top and bottom. `window-padding-balance` spreads the leftover space that does not fit a whole cell across all four edges. Padding changes apply to new windows and tabs, not to ones already open.

The macOS titlebar has four styles in `macos-titlebar-style`: `native`, `transparent` (the default), `tabs`, which puts the tab bar in the titlebar, and `hidden`. `hidden` removes the titlebar but keeps the rounded frame, while `window-decoration = none` removes the titlebar and borders together, as well as tabs on macOS. For a translucent window, set `background-opacity` to something like `0.9` and add `background-blur = 20`, the same intensity `true` gives you. On macOS, an opacity change only takes effect after you quit and reopen Ghostty, not on reload.

## Keybinds

A binding is `keybind = trigger=action`. Modifiers are `shift`, `ctrl`, `alt` (or `opt`) and `super` (or `cmd`). An action that takes an argument uses a colon:

```ini
keybind = cmd+shift+d=new_split:right
keybind = ctrl+a>n=new_window
keybind = cmd+k=unbind
```

The second line is a sequence: press `ctrl+a`, release, then press `n`. Ghostty waits for the next key indefinitely, with no timeout. `unbind` removes a default binding so the key reaches the program running in the terminal. `ghostty +list-keybinds --default` shows the defaults and `ghostty +list-actions` lists every action, as described in the [keybind docs](https://ghostty.org/docs/config/keybind).

Prefixes change how a binding behaves. `global:` makes it work while Ghostty is in the background, which on macOS needs Accessibility permission. `unconsumed:` runs the action and still sends the key to the program. `performable:` only consumes the key when the action can run, so `performable:cmd+c=copy_to_clipboard` falls through when nothing is selected. Be careful with `keybind = clear`: it removes every binding up to that line, defaults included.

## Option as Alt and shell integration

The Option key on a Mac types characters such as `∫` instead of acting as Alt, which breaks Alt shortcuts in shells and editors. `macos-option-as-alt` fixes that:

```ini
macos-option-as-alt = left
```

`true` turns both Option keys into Alt, and `left` or `right` turns only one, so the other can still type accented letters. When the key is unset, the default depends on your keyboard layout: `true` on U.S. Standard and U.S. International, `false` everywhere else.

Shell integration is on by default (`shell-integration = detect`) for bash, elvish, fish, nushell and zsh. It reports the working directory so new tabs and splits open in the same folder, marks prompts for the `jump_to_prompt` action, and skips the close confirmation when you are sitting at a prompt. `shell-integration-features` takes a comma-separated list, with `no-` in front to turn a feature off:

```ini
shell-integration-features = no-cursor,ssh-terminfo
```

`ssh-terminfo` installs Ghostty's terminfo entry on remote hosts that lack it, and `ssh-env` falls back to `xterm-256color` there. Both arrived in 1.2.0.

## The quick terminal

The quick terminal is a window that slides in from the edge of the screen over whatever app you are using. It has no default shortcut, so bind `toggle_quick_terminal` with the `global:` prefix:

```ini
keybind = global:ctrl+backquote=toggle_quick_terminal
quick-terminal-position = top
quick-terminal-size = 40%
quick-terminal-screen = mouse
```

`backquote` is the W3C name for the key left of `1`. Position takes `top`, `bottom`, `left`, `right` or `center`, and changing it on macOS requires a restart. On macOS the window hides when it loses focus, because `quick-terminal-autohide` defaults to true there. Set it to `false` to keep the window open.

## Moving a Ghostty setup to Kaku

Kaku is configured in Lua at `~/.config/kaku/kaku.lua`, a file that loads the bundled defaults first and applies your lines on top, and Kaku reloads it when you save. Several of the settings above are already set. The default font is JetBrains Mono with PingFang SC for Chinese, and Symbols Nerd Font Mono is bundled and added as a fallback after any font you choose. Left Option sends Meta and right Option still types composed characters, which matches `macos-option-as-alt = left`. `Cmd + Opt + Ctrl + K` drops a Kaku window from the top of the screen, like the quick terminal, and `config.macos_global_hotkey` changes the key. New installs start in Kaku Dark. A config without a `config.color_scheme` line follows the macOS appearance, and Auto in `kaku config` sets that up for you.

The rest translates line by line:

```lua
-- font-family = "Fira Code"
config.font = wezterm.font("Fira Code")
-- font-size = 16
config.font_size = 16
-- background-opacity = 0.92
config.window_background_opacity = 0.92
-- window-padding-x / window-padding-y, in points
config.window_padding = { left = '12pt', right = '12pt', top = '8pt', bottom = '8pt' }
-- a goto_split:right binding (append, never replace config.keys)
table.insert(config.keys, {
  key = 'RightArrow', mods = 'CMD|SHIFT',
  action = wezterm.action.ActivatePaneDirection('Right'),
})
```

Use `pt` in `window_padding` to match Ghostty, because a bare number or `px` means physical pixels, which look smaller on a Retina screen. Splits need no translation, since `Cmd + D` and `Cmd + Shift + D` already split the pane. `table.insert` keeps Kaku's default shortcuts, while assigning a new table to `config.keys` erases them. The [Ghostty, iTerm2 and WezTerm comparison](/blog/ghostty-vs-iterm2-vs-wezterm) covers how the three configuration models differ.

## FAQ

### Where is the Ghostty config file on macOS?

`~/.config/ghostty/config.ghostty`, or `~/.config/ghostty/config` before 1.2.3. Ghostty also reads `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty`, and loads it last, so its values win.

### How do I reload the Ghostty config?

Press `Cmd + Shift + ,`. Padding applies to new windows and tabs, while `background-opacity` and `quick-terminal-position` need a full restart on macOS.

### How do I make Option work as Alt in Ghostty?

Set `macos-option-as-alt = true` for both keys, or `left` or `right` for one. On U.S. layouts it already defaults to true.

### How do I see every Ghostty option?

Run `ghostty +show-config --default --docs | less`. For keybinds, use `ghostty +list-keybinds --default` and `ghostty +list-actions`.

### Can I use my Ghostty config in Kaku?

Not directly, because Kaku reads Lua rather than `key = value` lines. Most options map to one line in `kaku.lua`, and the font fallback, Option key and dropdown window are already set by default.

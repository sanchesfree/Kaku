# Mac Terminal Shortcuts That Save the Most Time

> The shell line-editing keys that work in every terminal, how to make Option act as Meta, and the app shortcuts for tabs, splits and search.

Published 2026-10-13 · Tw93 · https://kaku.fun/blog/mac-terminal-shortcuts

The shortcuts that save the most time in a Mac terminal live in two layers. The terminal app owns tabs, splits, search and scrollback, and those keys differ between Terminal.app, Ghostty and Kaku. The shell owns line editing: Ctrl + A, Ctrl + E, Ctrl + W, Ctrl + U, Ctrl + K, Ctrl + R and the Alt word keys, and those work in every terminal once Option is set to act as Meta.

## Line editing that works everywhere

zsh and bash both start in emacs mode, so the same keys move and delete on the command line no matter which terminal draws it. These are the defaults in both shells, checked with `zsh -fc 'bindkey'` and `bash -ic 'bind -p'` on macOS:

| Key | What it does |
|---|---|
| `Ctrl + A` / `Ctrl + E` | Start / end of line |
| `Ctrl + W` | Delete the previous word (bash: back to the previous space) |
| `Ctrl + U` | Delete the whole line (bash: from the cursor back to the start) |
| `Ctrl + K` | Delete from the cursor to the end |
| `Ctrl + Y` | Paste what the last delete removed |
| `Ctrl + _` | Undo the last edit |
| `Alt + B` / `Alt + F` | Back / forward one word |
| `Alt + D` | Delete the next word |
| `Alt + Backspace` | Delete the previous word |
| `Alt + .` | Insert the last argument of the previous command |

Two keys differ between the shells. In zsh, `Ctrl + U` is `kill-whole-line`, so it also removes text after the cursor, while bash's `unix-line-discard` stops at the cursor. In zsh, `Ctrl + W` is `backward-kill-word`, where a word is letters, digits and the characters in `$WORDCHARS`. That variable includes `/` by default, so a path goes in one press; removing `/` from it makes `Ctrl + W` delete one path segment at a time. Bash's `unix-word-rubout` simply deletes back to the last space. If you switch between the two, [zsh vs bash](/blog/zsh-vs-bash) covers the other differences.

The deletes are not lost. `Ctrl + U` on a long command and then `Ctrl + Y` later puts it back, which is a quick way to park a half-typed line, run something else, and paste it back.

## Option as Meta: why Alt + B and Alt + F fail on a Mac

A Mac has no Alt key. Option plus a letter types a character, so on a U.S. layout Option + B gives `∫` instead of moving back a word, and every `Alt` row in the table above prints junk until the terminal sends Option as Meta. Each terminal has its own switch.

**Terminal.app.** Turn on Use Option as Meta key in Terminal > Settings > Profiles > Keyboard, or toggle it for the current window with `Cmd + Option + O`. Apple's [shortcut list](https://support.apple.com/guide/terminal/keyboard-shortcuts-trmlshtcts/mac) notes that Option + D for deleting a word only works with this setting on.

**iTerm2.** In Settings > Profiles > Keys, set Left Option key to Esc+, which the [iTerm2 docs](https://iterm2.com/documentation-preferences-profiles-keys.html) call the right choice for most users.

**Ghostty.** The [`macos-option-as-alt`](https://ghostty.org/docs/config/reference#macos-option-as-alt) key takes `true`, `false`, `left` or `right`. When unset it follows your keyboard layout, `true` on U.S. Standard and U.S. International and `false` on others, so on a German or French layout you set it yourself:

```
macos-option-as-alt = left
```

Using `left` keeps the right Option key for accented letters and symbols, which matters if you type anything other than English. More Ghostty keys are in [Ghostty config](/blog/ghostty-config).

**WezTerm and Kaku.** The two settings are `send_composed_key_when_left_alt_is_pressed` and `send_composed_key_when_right_alt_is_pressed`. Setting one to `false` makes that Option key act as Alt.

## History search

`Ctrl + R` is the shortcut most worth learning. It opens an incremental search backward through history (`history-incremental-search-backward` in zsh, `reverse-search-history` in bash): type a few letters of an old command, press `Ctrl + R` again to step to older matches, press Enter to run the one shown, or press `Ctrl + G` to put the line back the way it was.

Prefix search on the Up arrow is the other common setup. You type `git push` and Up only cycles through commands that start with it. zsh ships the widgets but does not bind them; these lines in `~/.zshrc` turn them on:

```bash
autoload -U up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search
```

fzf can replace `Ctrl + R` with a fuzzy list of your whole history.

## Terminal.app shortcuts

Apple publishes the full list. These are the ones that come up every day:

| Action | Shortcut |
|---|---|
| New tab / new window | `Cmd + T` / `Cmd + N` |
| Next / previous tab | `Ctrl + Tab` / `Ctrl + Shift + Tab` |
| Split window into two panes | `Cmd + D` |
| Close split pane | `Cmd + Shift + D` |
| Find / find next | `Cmd + F` / `Cmd + G` |
| Jump to previous / next mark | `Cmd + Up` / `Cmd + Down` |
| Clear to start | `Cmd + K` |
| Reverse search history | `Ctrl + R` |
| Toggle Use Option as Meta key | `Cmd + Option + O` |

Marks are the underrated one. `Cmd + Return` marks a command line as you run it, and `Cmd + Up` and `Cmd + Down` jump between marks, so you land on the start of a long output instead of scrolling for it. Terminal.app has no shortcut for moving between split panes in that list, and if you want several shells side by side with keys to move and resize them, [the best terminal for Mac](/blog/best-terminal-for-mac) compares the options.

## Moving between words with Option + Arrow

Moving by word with Option + Left and Option + Right is the habit most people bring from Mac text fields, and Apple lists it as a Terminal.app default. Not every terminal sends what the shell expects for those keys, though. When Option + Left prints `[1;3D` or `;3D` instead of moving, the terminal is sending an arrow code the shell has no binding for. Either map the key in the terminal to send `Esc b` and `Esc f`, or bind the codes in zsh:

```bash
bindkey '^[[1;3D' backward-word
bindkey '^[[1;3C' forward-word
```

In Terminal.app, holding Option while you move the pointer repositions the insertion point on the command line, which is faster than any key for a long command.

## Kaku shortcuts

Kaku's bundled config sets left Option to act as Meta and keeps right Option for composed characters, so `Alt + B`, `Alt + F` and `Alt + .` work on first launch without a setting. It also maps Option + Left and Option + Right to `Alt + B` and `Alt + F`, Cmd + Left and Cmd + Right to `Ctrl + A` and `Ctrl + E`, Option + Backspace to `Ctrl + W`, and Cmd + Backspace to `Ctrl + U`. Its zsh integration rebinds `Ctrl + U` to `backward-kill-line`, so Cmd + Backspace deletes to the start of the line the way it does in a Mac text field, not the whole line, and Up and Down do prefix history search unless a tool like atuin already owns them.

For tabs, splits, search and the assistant, these are the defaults, read from the bundled key table and the [keybindings page](/docs/keybindings):

| Action | Shortcut |
|---|---|
| New tab | `Cmd + T` |
| Switch to tab 1 to 9 | `Cmd + 1` to `Cmd + 9` |
| Previous / next tab | `Cmd + Shift + [` / `Cmd + Shift + ]` |
| Tab Navigator | `Cmd + Shift + O` |
| Split side by side / top and bottom | `Cmd + D` / `Cmd + Shift + D` |
| Move between panes | `Cmd + Option + Arrows` |
| Zoom the current pane | `Cmd + Shift + Enter` |
| Search the pane | `Cmd + F` |
| Command Palette | `Cmd + Shift + P` |
| AI Chat | `Cmd + L` |
| Apply the Kaku Assistant suggestion | `Cmd + Shift + E` |
| AI settings | `Cmd + Shift + A` |

The zoom key is the one to pair with an agent. Run Claude Code in one pane and tests in another, then press `Cmd + Shift + Enter` to give the agent the full window while you read a long diff, and again to bring the split back. Tab Navigator filters tabs by name, which beats counting to `Cmd + 7` once you have more than a handful open. To add your own key, append to `config.keys` in `~/.config/kaku/kaku.lua` rather than replacing the table, or Kaku's defaults are gone.

## FAQ

### Why does Option + B type ∫ instead of moving back a word?

The terminal is sending Option as a character key. Turn on Use Option as Meta key in Terminal.app, set `macos-option-as-alt` in Ghostty, or set `send_composed_key_when_left_alt_is_pressed = false` in WezTerm. Kaku already does this for the left Option key.

### What does Ctrl + U do in zsh compared with bash?

In zsh it deletes the whole line, including text after the cursor. In bash it deletes from the cursor back to the start of the line. `Ctrl + Y` pastes the deleted text back in both.

### How do I search command history on a Mac?

Press `Ctrl + R` and type part of the command, press `Ctrl + R` again for older matches, Enter to run it, or `Ctrl + G` to cancel. It is a shell feature, so it works in any terminal.

### How do I clear the terminal with a shortcut?

`Cmd + K` clears to the start in Terminal.app and clears the screen and scrollback in Kaku. `Ctrl + L` is the shell's `clear-screen` and works in any terminal, redrawing the prompt at the top.

### Can I keep accented characters and still use Option as Meta?

Yes. Make only one Option key act as Meta: `macos-option-as-alt = left` in Ghostty, or the left and right `send_composed_key` settings in WezTerm and Kaku, which is Kaku's default split.

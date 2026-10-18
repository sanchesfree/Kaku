To set up fzf with zsh on a Mac, run `brew install fzf` and add `source <(fzf --zsh)` to your `~/.zshrc`. Open a new shell and you get three key bindings: Ctrl + R searches your history, Ctrl + T pastes files and directories onto the command line, and Alt + C jumps into a directory. On a Mac, Alt + C only works once your terminal sends the Option key as Meta, which most terminals do not do out of the box.

## Install and enable

[fzf](https://github.com/junegunn/fzf) is a single binary, and Homebrew is the simplest way to get it:

```bash
brew install fzf
```

Then add one line to `~/.zshrc`:

```bash
# Set up fzf key bindings and fuzzy completion
source <(fzf --zsh)
```

The `--zsh` flag prints the integration script for zsh, and sourcing it sets up both the key bindings and the `**<Tab>` fuzzy completion. It only exists in recent fzf releases, so if the shell complains, check `fzf --version` and upgrade with `brew update; brew upgrade fzf`. Homebrew shipped 0.74.5 in October 2026.

If you only want some of the bindings, set the matching `*_COMMAND` variable to an empty string on the same line. Setting it afterwards has no effect:

```bash
FZF_CTRL_R_COMMAND= FZF_ALT_C_COMMAND= source <(fzf --zsh)
```

## The three key bindings

**Ctrl + R, history.** It searches your history and pastes the command you pick onto the command line without running it. Press Ctrl + R again to switch between relevance and chronological order, `TAB` to select several commands, and Alt + R for raw mode, where the lines around each match stay visible and Ctrl + N and Ctrl + P jump between matches.

**Ctrl + T, files.** It lists files and directories under the current directory and pastes the ones you pick at the cursor, so `vim ` then Ctrl + T opens a picker and drops the path in place. The list comes from fzf's built-in walker with `--walker file,dir,follow,hidden`, so hidden files are included.

**Alt + C, directories.** It lists directories only, built with `--walker dir,follow,hidden`, and runs `cd` into the one you choose.

Inside the finder, Ctrl + K and Ctrl + J (or Ctrl + P and Ctrl + N) move up and down, Enter accepts, and Ctrl + C, Ctrl + G or Esc cancels. Typing is fuzzy by default, and spaces separate terms: `'wild` matches exactly, `^music` anchors the start, `.mp3$` the end, and `!fire` excludes. The `-e` option switches the whole search to exact mode.

The same integration also adds fuzzy completion. End a word with `**` and press Tab:

```bash
vim **<Tab>      # files under the current directory
cd ~/github/**<Tab>
kill -9 **<Tab>  # pick a process
ssh **<Tab>      # hosts from /etc/hosts and ~/.ssh/config
```

## Mac gotcha: Alt + C and the Option key

zsh sees Alt + C as Esc followed by `c`, so it only works when the terminal sends Option as Meta. By default, a Mac types a character for Option plus a letter instead. Kaku's left Option key already acts as Meta, and [Mac terminal shortcuts](/blog/mac-terminal-shortcuts) covers the setting in Terminal.app, iTerm2, Ghostty and WezTerm.

## Better defaults with fd and bat

The built-in walker is fast enough for most projects, and two kinds of tweaks cover the rest: skip noisy directories, and add a preview. Each binding has its own `*_OPTS` variable, set before the `source` line:

```bash
brew install bat tree

# Ctrl + T: skip build folders, preview files with bat, Ctrl + / toggles the preview
export FZF_CTRL_T_OPTS="
  --walker-skip .git,node_modules,target
  --preview 'bat -n --color=always {}'
  --bind 'ctrl-/:change-preview-window(down|hidden|)'"

# Alt + C: show the directory as a tree
export FZF_ALT_C_OPTS="
  --walker-skip .git,node_modules,target
  --preview 'tree -C {}'"

# Ctrl + R: Ctrl + Y copies the command to the clipboard
export FZF_CTRL_R_OPTS="
  --bind 'ctrl-y:execute-silent(echo -n {2..} | pbcopy)+abort'
  --color header:italic
  --header 'Press CTRL-Y to copy command into clipboard'"

source <(fzf --zsh)
```

If you already use [fd](https://github.com/sharkdp/fd) and want fzf to list exactly what fd lists, define the two helper functions fzf uses for `**<Tab>` completion and point the key bindings at fd as well:

```bash
brew install fd

_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}
_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}
export FZF_CTRL_T_COMMAND='fd --hidden --follow --exclude .git'
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
```

`FZF_DEFAULT_COMMAND` (for example `fd --type f`) only changes what plain `fzf` lists. The README says shell integration does not use it, which is why the key bindings have their own variables. Options that should apply everywhere, such as `--height 40% --layout reverse --border`, go in `FZF_DEFAULT_OPTS`.

## fzf-tab for every completion

`**<Tab>` only kicks in when you type the trigger. [fzf-tab](https://github.com/Aloxaf/fzf-tab) replaces zsh's whole completion menu with fzf, so a plain Tab after `git checkout `, `kill ` or a variable name opens a fuzzy list. It does not complete anything itself. It shows the results of zsh's own completion system, so your existing completion settings keep working.

```bash
git clone https://github.com/Aloxaf/fzf-tab ~/.zsh/fzf-tab
```

```bash
autoload -U compinit; compinit
source <(fzf --zsh)
source ~/.zsh/fzf-tab/fzf-tab.plugin.zsh

zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'
```

The last line previews a directory with eza while you complete `cd`, so install it with `brew install eza` or drop the line.

Loading order is where setups usually break. fzf-tab needs to load after `compinit` but before plugins that wrap widgets, such as zsh-autosuggestions or fast-syntax-highlighting. It also has to be the last thing that binds Tab, and fzf's own completion binds Tab too, which is why fzf-tab comes after `source <(fzf --zsh)` above. Two keys worth knowing once it runs: Ctrl + Space selects several entries, and `/` starts continuous completion for deep paths. For a plugin-manager-free `.zshrc` that already gets the rest of this order right, see [zsh without Oh My Zsh](/blog/zsh-without-oh-my-zsh).

## Using fzf in Kaku

Kaku does not install or configure fzf. Its optional Homebrew bootstrap installs starship, delta, lazygit and yazi (zoxide only for fish), and for zsh it bundles zsh-autosuggestions, fast-syntax-highlighting, zsh-completions and zsh-z, so the `source <(fzf --zsh)` line is still yours to add. zsh-z is skipped when zoxide already defines `z`. Inside Kaku, Smart Tab binds Tab, and `kaku init` appends its source line to the end of `.zshrc`, so the order of the two lines matters. With `source <(fzf --zsh)` below the Kaku line, `**<Tab>` keeps working, because fzf hands every other Tab press back to Smart Tab. With it above, Tab stays with Smart Tab and `**` no longer opens fzf. Ctrl + T, Ctrl + R and Alt + C remain bound to fzf either way.

For fzf-tab, set `config.smart_tab_mode = 'off'` in `~/.config/kaku/kaku.lua`, which exports `KAKU_SMART_TAB_DISABLE=1` to new shells, and keep `compinit`, the fzf line and fzf-tab above the Kaku line. Kaku skips its own `compinit` when completion is already initialized and loads autosuggestions after fzf-tab, which matches the order fzf-tab asks for. Alt + C needs no extra setting here: the bundled config sends the left Option key as Meta and keeps the right one for composed characters.

## FAQ

### Why does Alt + C type a strange character instead of changing directory?

Your terminal is sending Option as a text modifier. Turn on Use Option as Meta key in Terminal.app, set Left Option Key to Esc+ in iTerm2, or set `macos-option-as-alt = left` in Ghostty.

### Why does fzf ignore my FZF_DEFAULT_COMMAND?

Shell integration does not use it. Set `FZF_CTRL_T_COMMAND` for Ctrl + T and `FZF_ALT_C_COMMAND` for Alt + C, or define `_fzf_compgen_path` and `_fzf_compgen_dir` for `**<Tab>`.

### How do I turn off one of the bindings?

Set the matching variable to an empty string on the line that sources fzf, for example `FZF_ALT_C_COMMAND= source <(fzf --zsh)`. Setting it after the `source` line has no effect.

### Does fzf-tab replace `**<Tab>`?

It covers more ground, since every Tab completion goes through fzf, but the two can live together. Load fzf-tab after `source <(fzf --zsh)` so it is the last plugin to bind Tab.

### Do I need fd for fzf?

No. fzf ships its own walker and lists files without any extra tools, and `--walker-skip` covers the usual noisy folders. fd is an option when you already rely on its filtering elsewhere and want the same list in fzf.

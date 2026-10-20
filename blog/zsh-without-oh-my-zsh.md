# A Fast Zsh Setup Without Oh My Zsh

> Autosuggestions, syntax highlighting, completions and a Starship prompt with plain zsh, the load order that keeps it fast, and how to measure it.

Published 2026-09-27 · Tw93 · https://kaku.fun/blog/zsh-without-oh-my-zsh

You do not need Oh My Zsh to get a good zsh. Four pieces cover what most people install it for: zsh-autosuggestions for the grey suggestion from your history, a syntax highlighter that colors commands as you type, zsh-completions for extra completion definitions, and Starship for the prompt. Loaded directly from your `.zshrc` in the right order, with completion caching, they start fast and stay easy to understand.

## Install the pieces

With Homebrew:

```bash
brew install zsh-autosuggestions zsh-syntax-highlighting zsh-completions starship
```

That is the whole dependency list. There is no framework to update and nothing runs at startup that you did not ask for.

## A .zshrc that loads them in order

```bash
# Completion definitions go on fpath before compinit
fpath=(${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-completions $fpath)

# Check the completion cache at most once a day.
# (#q...) needs EXTENDED_GLOB, without it the test is always true.
setopt EXTENDED_GLOB
autoload -Uz compinit
if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
  compinit && touch "${ZDOTDIR:-$HOME}/.zcompdump"
else
  compinit -C
fi

# History
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE

# Prompt
eval "$(starship init zsh)"

# Suggestions from history
source ${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-autosuggestions/zsh-autosuggestions.zsh

# Syntax highlighting must come last
source ${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

`HOMEBREW_PREFIX` is set by `brew shellenv`, and the fallback covers Apple Silicon's default path. Writing the path out instead of calling `$(brew --prefix)` saves starting a process on every shell.

## Why the order matters

Three rules decide most of it:

- **Completions before `compinit`.** `compinit` scans `fpath` once. Anything added later is not seen until the next rebuild.
- **`compinit -C` most of the time.** A full `compinit` checks every completion file. With `-C` it trusts the cached `.zcompdump`, and the check above runs a full check when the cache is more than 24 hours old, rebuilding it if needed and refreshing its timestamp only after success. On an M5 Pro the full run took 29.3 ms and the cached one 16.2 ms. The `(#q...)` test only works with `EXTENDED_GLOB` on; without it the string is never treated as a glob, the test is always true, and every shell quietly does the full check.
- **Syntax highlighting last.** It works by wrapping zsh's line editor widgets, so widgets defined after it, autosuggestions included, would not be highlighted. Its documentation advises sourcing it at the end.

## Measure it instead of guessing

```bash
time zsh -i -c exit
```

For steadier numbers, `hyperfine` runs it many times:

```bash
brew install hyperfine
hyperfine --warmup 5 'zsh -i -c exit'
```

`zsh -i -c exit` measures everything up to the first prompt except work hooked onto the prompt itself, so it is a good way to compare one change at a time. If a number jumps, comment out half the file and measure again.

## How Kaku does the same thing

Kaku ships this setup and loads it from two lines it adds to your `.zshrc`, one for `PATH` and one that sources `~/.config/kaku/zsh/kaku.zsh`. The bundled pieces are zsh-autosuggestions, fast-syntax-highlighting, zsh-completions and zsh-z for jumping to directories you visit often, with Starship for the prompt.

![The six steps of Kaku's zsh setup in order: PATH and Kaku check, Starship prompt from a cached init, history and keys, compinit -C with a full check once a day, z and autosuggestions where yours win, and syntax highlighting after the first prompt](https://kaku.fun/img/blog/kaku-zsh-load-order.webp)

*The same rules as above, plus a cached prompt init and highlighting deferred to the first prompt.*

On top of the rules above, it does three more things:

- **Caches Starship's init script**, so a warm start runs no extra process for the prompt.
- **Defers syntax highlighting** until the first prompt is about to appear, keeping it last without slowing down earlier startup steps.
- **Compiles the whole file** with `zcompile`, so zsh reads bytecode instead of parsing it again.

It also steps aside for your own setup. If your `.zshrc` already loads autosuggestions, a highlighter or a directory jumper such as zoxide, Kaku skips its own copy, and if completion is already initialized it skips `compinit`.

Measured on an M5 Pro with `hyperfine`, 30 runs each, an empty `.zshrc` starts in 10.8 ms and the full Kaku setup in 43.3 ms.

Two switches cover the common objections. `KAKU_SKIP_TOOL_BOOTSTRAP=1 kaku init` sets up the shell without installing the optional Homebrew tools, and `kaku reset` removes the Kaku-managed lines and files again while keeping everything you wrote yourself.

## FAQ

### Is Oh My Zsh slow?

It depends on how many plugins and which theme you load. Measure your own startup with `time zsh -i -c exit` and compare it with a `.zshrc` that loads only the pieces you use.

### Should I use zsh-syntax-highlighting or fast-syntax-highlighting?

Both color the command line as you type. zsh-syntax-highlighting is the more common one, fast-syntax-highlighting is a separate project with its own themes, and Kaku bundles the latter. Either one goes last in `.zshrc`.

### Why do my zsh completions not show up?

Usually because the completion directory was added to `fpath` after `compinit` ran, or because a cached `.zcompdump` predates it. Move the `fpath` line above `compinit` and run `rm ~/.zcompdump; exec zsh` once.

### Can I use Kaku's zsh setup with my own Starship config?

Yes. Kaku only writes `~/.config/starship.toml` when there is none, or when it is a byte-identical copy of the file Kaku 0.10.0 to 0.22.0 shipped, so a config you wrote or symlinked stays as it is.

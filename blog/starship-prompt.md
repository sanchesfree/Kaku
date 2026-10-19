# Starship Prompt on Mac: Install, Configure and Keep It Fast

> Install Starship for zsh or fish, configure starship.toml, format strings and presets, and find the modules and timeouts that make a prompt slow.

Published 2026-10-12 · Tw93 · https://kaku.fun/blog/starship-prompt

To use Starship on a Mac, run `brew install starship`, add `eval "$(starship init zsh)"` to `~/.zshrc`, and open a new shell. Everything else lives in one TOML file, `~/.config/starship.toml`, where you pick the modules, their format and their style, or start from one of the community presets. Keeping it fast comes down to two timeouts, `scan_timeout` and `command_timeout`, and to how much work the Git modules do in large repositories.

## Install and turn it on

The [Starship guide](https://starship.rs/guide/) lists several ways to install on macOS. Homebrew is the simplest:

```bash
brew install starship
```

`cargo install starship --locked`, `port install starship` and the official install script also work. Then add the init line for your shell to its config file, near the end and before syntax highlighting:

```bash
# ~/.zshrc
eval "$(starship init zsh)"

# ~/.bashrc
eval "$(starship init bash)"
```

```fish
# ~/.config/fish/config.fish
starship init fish | source
```

Open a new shell and the prompt changes. If you are rebuilding your zsh setup at the same time, [zsh without Oh My Zsh](/blog/zsh-without-oh-my-zsh) covers where the Starship line sits relative to completion, autosuggestions and syntax highlighting.

The guide lists one prerequisite: a [Nerd Font](https://www.nerdfonts.com/) installed and enabled in your terminal, because the default symbols for Git, languages and tools come from those glyphs. Without one you get empty boxes. [Nerd Fonts on Mac](/blog/nerd-fonts-mac) explains how to add only the symbols as a fallback instead of switching fonts.

## The config file

Starship reads nothing until you create its file:

```bash
mkdir -p ~/.config && touch ~/.config/starship.toml
```

To keep it somewhere else, for example in a dotfiles repository, set `STARSHIP_CONFIG` before the init line:

```bash
export STARSHIP_CONFIG=~/dotfiles/starship.toml
```

A small file that shows the main ideas:

```toml
"$schema" = 'https://starship.rs/config-schema.json'

add_newline = false

[character]
success_symbol = '[>](bold green)'
error_symbol = '[x](bold red)'

[directory]
truncation_length = 2

[package]
disabled = true
```

The `$schema` line lets your editor complete keys from Starship's config schema. Top-level keys such as `add_newline` apply to the whole prompt, and each `[table]` configures one module. The [configuration reference](https://starship.rs/config/) calls a module a component that shows information from your environment, such as `nodejs` showing the Node.js version when you are inside a Node.js project, and `disabled = true` hides any module completely.

A few defaults worth knowing, checked October 2026: `add_newline` is `true`, so there is a blank line between prompts until you turn it off. `directory` truncates to three parent folders and to the root of the Git repository you are in. `cmd_duration` appears only when a command took longer than two seconds, set by `min_time = 2_000`. `time` and `git_metrics` are disabled until you set `disabled = false`.

## Format strings

Each module has a `format`, and the prompt has one too. A format string mixes three things:

- **Variables** start with `$`, such as `$branch` inside `git_branch` or `$git_branch` in the prompt format.
- **Text groups** are `[text](style)`. `'[on](red bold)'` prints `on` in bold red.
- **Conditional groups** in `( )` render nothing when every variable inside is empty. `'(@$region)'` shows `@us-east-1` or nothing at all.

Styles are short strings: `'bold fg:27'`, `'fg:green bg:blue'`, `'underline bg:#bf5700'`, or `''` for none. The symbols `$ [ ] ( )` have special meaning, so escape them with a backslash when you want them printed. Single-quoted TOML strings need less escaping, which is why the reference uses them in most examples.

The default prompt format is `$all`, which expands to the full list of modules in a fixed order. To move one module and keep the rest, extend it rather than replace it:

```toml
format = '$all$directory$character'
```

Modules you name explicitly are not repeated, so this moves the directory to the second line, next to the prompt character. To control the whole order, list only the modules you want:

```toml
format = '$directory$git_branch$git_status$nodejs$python$character'
```

Colors can also be named once and reused. Set `palette` to a name and define it under `[palettes.<name>]`, then use the names in any style string:

```toml
palette = 'mine'

[palettes.mine]
mustard = '#af8700'

[git_branch]
style = 'bold mustard'
```

## Presets

The [presets page](https://starship.rs/presets/) collects community configurations. Each entry links to its own page with the TOML and how to apply it. The presets listed there, checked October 2026:

| Preset | What it changes |
|---|---|
| Nerd Font Symbols | Every module uses Nerd Font symbols |
| No Nerd Fonts | No Nerd Font symbols anywhere in the prompt |
| Bracketed Segments | Segments in brackets instead of words like "via" and "on" |
| Plain Text Symbols | Plain text symbols, for terminals without Unicode |
| No Runtime Versions | Hides language runtime versions |
| No Empty Icons | No icon when the toolset is not found |
| Pure Prompt | Emulates the Pure prompt |
| Pastel Powerline, Tokyo Night, Gruvbox Rainbow, Catppuccin Powerline | Powerline-style colored segments |
| Jetpack | A pseudo minimalist prompt |

The page notes that No Nerd Fonts will become the default in a future release. A preset is a starting point, not a mode: it becomes your `starship.toml`, and you edit it from there like any other config. Back up your current file before replacing it. The `starship` binary also prints the bundled presets, so `starship preset --list` shows their names and `starship preset tokyo-night -o ~/.config/starship.toml` writes one out.

## Keep it fast

The prompt is drawn before you can type, so anything slow in it is felt on every Enter. Three settings do most of the work.

`scan_timeout` limits how long Starship spends scanning files in the current directory, which is how language modules decide whether you are in a Node.js or Python project. The default is 30 ms. `command_timeout` limits each external command a module runs, such as `git` or `node --version`, and the default is 500 ms. Git status in a very large repository can take longer than that, so raise it if you work in one, or keep it low if you would rather never wait long for a prompt:

```toml
scan_timeout = 10
command_timeout = 1000
```

Git is the usual cost in big repositories. `git_status` has `ignore_submodules`, which stops changes inside submodules from counting, and `use_git_executable`, which computes status with the `git` binary instead of gitoxide. `git_metrics`, which counts added and deleted lines, is off by default, so leave it off unless you read those numbers. If you never read a module, set `disabled = true` or leave it out of your `format`.

A few commands help with diagnosis. `starship timings` prints how long each active module took on the current directory, which is the quickest way to find the slow one, and `starship explain` shows the description of each module, which tells you what each piece of the line is. Warnings and errors go to `~/.cache/starship/session_${STARSHIP_SESSION_KEY}.log`, one file per terminal session, and you can move that directory with `STARSHIP_CACHE`.

## A right-side prompt

`right_format` takes the same kind of format string as `format` and draws it on the right. It is empty by default. Moving the duration and clock there keeps the left side short:

```toml
format = '$directory$git_branch$git_status$character'
right_format = '$cmd_duration$time'

[time]
disabled = false
```

The format on the left lists modules explicitly instead of using `$all`, because `$all` already includes `cmd_duration` and `time`.

## Starship in Kaku

Kaku's shell setup (`kaku init`, also offered on first launch) installs Starship through Homebrew when it is missing, and starts it only inside Kaku, including tmux sessions started from Kaku. The managed `kaku.zsh` checks `TERM_PROGRAM=Kaku`, or `$TMUX` together with the `KAKU_SESSION` variable a Kaku shell exports, and the fish setup uses the same test. Other terminals keep the prompt you already had. To use Kaku's Starship in every terminal, add `export KAKU_PROMPT_EVERYWHERE=1` before the Kaku line in `.zshrc`, or `set -gx KAKU_PROMPT_EVERYWHERE 1` in `config.fish`. Icons render without installing a Nerd Font, because Kaku bundles Symbols Nerd Font Mono and appends it as a fallback to whatever font you set.

There is no separate Kaku prompt config. Kaku does not set `STARSHIP_CONFIG`, so Starship reads the normal `~/.config/starship.toml`, and Kaku copies its own file there only when none exists. If you already have one, it is left alone. The single exception is a file byte-identical to the one Kaku 0.10.0 to 0.22.0 shipped with its icons stripped, which is replaced with the current version, while an edited or symlinked file always stays. The copied file is an ordinary config you can edit: it uses a short explicit `format` instead of `$all`, sets `command_timeout = 2000` so a large repository's Git status has room, and turns on `ignore_submodules` for `git_status`.

## FAQ

### Why does my Starship prompt show boxes or question marks?

The terminal font has no glyphs for the Nerd Font symbols the modules use. Install a Nerd Font, add the symbols-only font as a fallback, or switch to the No Nerd Fonts or Plain Text Symbols preset.

### Where is the Starship config file?

`~/.config/starship.toml`. Starship does not create it, so make it with `mkdir -p ~/.config && touch ~/.config/starship.toml`, or point `STARSHIP_CONFIG` at another path.

### Why is my prompt slow or missing Git status in a big repository?

Git commands in large repositories can run past `command_timeout`, which defaults to 500 ms. Raise the timeout if you want the status anyway, set `ignore_submodules = true` under `[git_status]`, and disable modules you do not need.

### How do I show the prompt on the right?

Set `right_format`, for example `right_format = '$cmd_duration$time'`, and leave those modules out of the left `format`.

### Does Kaku overwrite my starship.toml?

No. Kaku writes `~/.config/starship.toml` only when there is none, or when it is an untouched copy of the file older Kaku versions shipped, so a config you wrote yourself is used as it is, inside Kaku and everywhere else.

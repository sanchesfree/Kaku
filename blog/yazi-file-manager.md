# Yazi on Mac: A Fast Terminal File Manager Setup

> Install Yazi and its preview tools on macOS, learn the keys that matter, add the y wrapper that changes directory on quit, and configure it.

Published 2026-10-15 · Tw93 · https://kaku.fun/blog/yazi-file-manager

To set up [Yazi](https://yazi-rs.github.io/) on a Mac, run `brew install yazi` along with the optional preview tools, start it with `yazi`, and press `q` to quit. Add the `y` shell wrapper from the Yazi docs so that quitting leaves your shell in the folder you were browsing. Everything else is three TOML files in `~/.config/yazi/`, and you only write the parts you want to change.

## Install Yazi and the preview tools

Yazi's only hard requirement is `file`, which macOS already has, for detecting file types. The rest are optional command-line tools that each switch on one feature. The [installation page](https://yazi-rs.github.io/docs/installation) gives one Homebrew line for all of them (checked October 2026, docs version 26.9.1):

```bash
brew update
brew install yazi ffmpeg-full sevenzip jq poppler fd ripgrep fzf zoxide resvg imagemagick-full font-symbols-only-nerd-font
brew link ffmpeg-full imagemagick-full -f --overwrite
```

Here is what each one adds:

| Package | What it enables |
|---|---|
| `ffmpeg-full` | Video thumbnails |
| `sevenzip` | Archive extraction and preview |
| `jq` | JSON preview |
| `poppler` | PDF preview |
| `fd` | File search by name |
| `ripgrep` | File search by content |
| `fzf` | Quick subtree navigation (0.53.0 or newer) |
| `zoxide` | Jumping to directories you visited before, needs `fzf` |
| `resvg` | SVG preview |
| `imagemagick-full` | Font, HEIC and JPEG XL preview (7.1.1 or newer) |
| `font-symbols-only-nerd-font` | The file-type icons |

You can install `yazi` on its own and add the others later. The docs say to upgrade these tools to their newest versions if a preview does not work, and `brew install yazi --HEAD` builds from the latest code if you want it. If the icons show up as boxes, font setup is covered in [Nerd Fonts on Mac](/blog/nerd-fonts-mac).

## The keys you need first

Run `yazi` in any directory. You get three columns: the parent directory, the current one, and a preview of whatever the cursor is on. Press `F1` or `~` for the help menu, and `q` to quit. The [quick start](https://yazi-rs.github.io/docs/quick-start) lists everything, and these are enough for the first day:

| Key | Action |
|---|---|
| `j` / `k` | Move the cursor down or up |
| `l` / `h` | Enter the hovered directory, or go back to the parent |
| `g` `g` / `G` | Jump to the top or bottom |
| `J` / `K` | Scroll the preview down or up by 5 units |
| `Space` | Toggle selection on the hovered item |
| `v` | Visual mode for selecting a range |
| `o` or `Enter` | Open selected files |
| `y` / `x` / `p` | Yank (copy), cut, paste |
| `d` / `D` | Move to the trash, or delete permanently |
| `a` | Create a file, or a directory if the name ends with `/` |
| `r` | Rename |
| `.` | Show or hide hidden files |
| `s` / `S` | Search by name with fd, or by content with ripgrep |
| `z` / `Z` | Jump with fzf, or with zoxide |
| `c` `c` | Copy the file path |
| `t` `t` | New tab in the current directory |

Keys written as two letters, like `g` `g`, are pressed one after the other. `d` sends files to the trash and `g` `t` opens the trash bin, so an accidental deletion is easy to undo, while `D` is permanent. If you already use fzf in your shell, `z` feels the same, and the zsh setup is covered in [fzf in zsh on Mac](/blog/fzf-zsh-mac).

## The y wrapper

A program started from your shell cannot change the shell's working directory, so when you quit `yazi` you land back where you started. Yazi works around this with `--cwd-file`: it writes the directory you quit in to a file, and a small shell function reads that file and runs `cd`. The quick start gives this version for Bash and Zsh:

```bash
function y() {
  local tmp cwd; tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
  command yazi "$@" --cwd-file="$tmp"
  IFS= read -r -d '' cwd < "$tmp"
  [ "$cwd" != "$PWD" ] && [ -d "$cwd" ] && builtin cd -- "$cwd" || builtin true
  command rm -f -- "$tmp"
}
```

Put it in `~/.zshrc`, open a new shell, and start with `y` instead of `yazi`. Press `q` and your shell is now in the directory you were looking at, and press `Q` when you want to quit without changing it. Fish users have their own version on the same page:

```fish
function y
  set tmp (mktemp -t "yazi-cwd.XXXXXX")
  command yazi $argv --cwd-file="$tmp"
  if read -z cwd < "$tmp"; and [ "$cwd" != "$PWD" ]; and test -d "$cwd"
    builtin cd -- "$cwd"
  end
  command rm -f -- "$tmp"
end
```

## Config files: yazi.toml, keymap.toml, theme.toml

Yazi reads [three configuration files](https://yazi-rs.github.io/docs/configuration/overview) from `~/.config/yazi/`:

- `yazi.toml` for general settings
- `keymap.toml` for keybindings
- `theme.toml` for colors

The defaults are built into the release, so you do not need to copy the whole file. Create the file and write only the options you want to change. To show hidden files by default:

```toml
# ~/.config/yazi/yazi.toml
[mgr]
show_hidden = true
```

Keybindings work a little differently. Writing `keymap = [...]` under `[mgr]` replaces the default map completely, which is rarely what you want. Use `prepend_keymap` or `append_keymap` to add your keys on top of the defaults:

```toml
# ~/.config/yazi/keymap.toml
[mgr]
prepend_keymap = [
  { on = "e", run = "open", desc = "Edit or open selected files" },
]
```

The full default files live on the `shipped` tag of the [Yazi repository](https://github.com/sxyazi/yazi/tree/shipped/yazi-config/preset), which is the place to look up a key name or option before you override it. To try a separate setup without touching your main one, point `YAZI_CONFIG_HOME` at another directory:

```bash
YAZI_CONFIG_HOME=~/.config/yazi-alt yazi
```

One thing to watch if you add editor schema hints at the top of these files: write them as a `#:schema` comment, not as a `$schema` key. Kaku's setup script notes that Yazi 26.5.6 and later refuse a `$schema` key and fail to start, so a file that used to work can stop Yazi after an upgrade:

```toml
#:schema https://yazi-rs.github.io/schemas/keymap.json
```

## Opening files

`o` and `Enter` open the selected files, and `O` opens them interactively so you can pick which opener to use. `Shift + Enter` does the same as `O` in terminals that support it. Openers are defined in `yazi.toml` under `[opener]`, and the rules that map file types to openers can be extended with `prepend_*` and `append_*` lists, the same way as keys. A common addition is an `edit` opener that sends text files to your editor and waits for it to close:

```toml
[opener]
edit = [
  { run = "${EDITOR:-vim} %s", desc = "edit", for = "unix", block = true },
]
```

`block = true` makes Yazi hand the terminal to the editor and come back when you quit it. To copy paths into another app, `c` `c` copies the full path, `c` `d` the directory, and `c` `f` the file name.

## Yazi in Kaku

[Kaku](/docs/features) configures Yazi as part of its shell setup but does not bundle the binary. `kaku init` asks before installing missing tools through Homebrew, Yazi among them, and only `yazi` itself, so the preview tools above are still yours to add. The shell integration defines the same `y` function for zsh and fish, and `Cmd + Shift + Y` types `y` into the current pane, so pressing `q` returns you to a shell already sitting in the folder you picked.

For each of these files missing from `~/.config/yazi/`, the setup writes a starting one: a `yazi.toml` with a wider preview column (`ratio = [3, 3, 10]`) and the `edit` opener shown above, a `keymap.toml` that binds `e` and `o` to open and makes `Enter` enter a directory, and, from 0.25.0, an `init.lua` that leaves a row between the path and the file columns. If you already have a `yazi.toml`, the zsh setup only adds the preview size (`max_width`, `max_height`) and the `edit` opener when they are missing, and other existing files are left alone. Kaku also installs two flavors, `kaku-dark` and `kaku-light`, and keeps a marked `[flavor]` block in `theme.toml` matched to the active scheme, Kaku Dark or Kaku Light, refreshing it each time Yazi launches. If you wrote your own `[flavor]` section, Kaku leaves it in place. It writes `#:schema` comments and rewrites old `$schema` keys in `theme.toml`, `keymap.toml` and `yazi.toml`, so the 26.5.6 problem above is already handled for you.

Image previews depend on the terminal being able to draw pixels. Kaku implements the iTerm2 inline image protocol and the Kitty graphics protocol, the latter enabled by default through `enable_kitty_graphics`. Inside an SSH pane, `Cmd + Shift + R` mounts the remote host's files under `~/Library/Caches/dev.kaku/sshfs` with sshfs and opens them in Yazi in a new tab; it needs macFUSE and sshfs installed. Lazygit sits next to it on `Cmd + Shift + G`, covered in [lazygit and delta](/blog/lazygit-and-delta).

## FAQ

### How do I make Yazi change my shell's directory when I quit?

Use the `y` wrapper from the quick start, which passes `--cwd-file` to `yazi` and runs `cd` after it exits. Start with `y`, press `q` to quit and change directory, or `Q` to quit without changing.

### Why do PDF, video or SVG previews not show?

Each one depends on a separate tool: `poppler` for PDF, `ffmpeg-full` for video thumbnails, `resvg` for SVG, `imagemagick-full` for HEIC and fonts. Install the one that is missing and upgrade it to the newest version if it is already there.

### Where does Yazi keep its config on a Mac?

In `~/.config/yazi/`, as `yazi.toml`, `keymap.toml` and `theme.toml`. Set `YAZI_CONFIG_HOME` to use a different directory.

### Yazi stopped starting after an upgrade. What should I check?

Look at the top of your three config files for a `$schema = ...` line. Yazi 26.5.6 and later reject that key, so change it to a `#:schema https://...` comment.

### Does Kaku install Yazi for me?

`kaku init` offers to install it through Homebrew in an interactive shell, or you can run `brew install yazi` yourself. Kaku then sets up the `y` wrapper, `Cmd + Shift + Y` and the theme that follows Kaku Dark or Kaku Light.

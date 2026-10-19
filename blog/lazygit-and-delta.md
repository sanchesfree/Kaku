# Lazygit and Delta: A Terminal Git Workflow on Mac

> Install lazygit and delta, wire delta into git and into lazygit's diff view, and the shortcuts that make reviewing an agent's changes quick.

Published 2026-09-24 · Tw93 · https://kaku.fun/blog/lazygit-and-delta

Lazygit and delta together give you a fast git workflow without leaving the terminal: lazygit is a full-screen git interface where staging a line, amending a commit or rebasing is one key away, and delta makes every diff readable, with syntax highlighting, line numbers and word-level changes. Install both with `brew install lazygit git-delta`, point git's pager at delta, and add one renderer line to lazygit's config so its diff view uses delta too. This post sets that up and covers the shortcuts that matter most when you are reviewing what an AI coding agent just changed. Checked with lazygit 0.66 and delta 0.20.1.

## Install

```bash
brew install lazygit git-delta
```

The Homebrew formula is `git-delta` (`delta` works as an alias), and the command it installs is `delta`.

## Make git use delta

Delta reads git's output and prints a nicer version of it, so it is wired in as git's pager:

```bash
git config --global core.pager delta
git config --global interactive.diffFilter 'delta --color-only'
git config --global merge.conflictStyle zdiff3
```

`core.pager` covers `git diff`, `git log -p` and `git show`. `interactive.diffFilter` colors the hunks in `git add -p`. `zdiff3` shows the common ancestor in merge conflicts, which makes most conflicts easier to read. Delta's own options go in a `[delta]` section of `~/.gitconfig`:

```ini
[delta]
    line-numbers = true
    side-by-side = true
```

Side-by-side needs a wide window, so leave it out if you usually work in a narrow split.

## Make lazygit use delta

Lazygit does not read `core.pager` for its own diff panel. It uses a list of diff renderers in its config file, which lives in the directory `lazygit --print-config-dir` prints:

```yaml
git:
  diffRenderers:
    - command: delta --dark --paging=never
```

Use `--light` instead of `--dark` with a light theme. `--paging=never` matters because lazygit does its own scrolling. You can list more than one renderer and cycle through them with `|` inside lazygit, for example delta and git's plain output.

![git diff and git log -p reach delta through core.pager, lazygit reaches it through diffRenderers, and delta's colored output shows up in a Kaku pane, where Cmd+Shift+G opens lazygit](https://kaku.fun/img/blog/lazygit-delta-pipeline.webp)

*Two entry points, one renderer.*

One delta option does not carry over: the `navigate` setting, which uses `n` and `N` to jump between files, only works when delta runs its own pager, so it does nothing inside lazygit.

## The shortcuts worth learning first

| Key | In | Does |
|---|---|---|
| `space` | Files | Stage or unstage a file |
| `enter` | Files | Open the file to stage single lines or hunks |
| `a` | Files | Stage or unstage everything |
| `c` | Files | Commit |
| `A` | Files | Amend the last commit |
| `d` | Files | Discard changes |
| `P` / `p` | Anywhere | Push / pull |
| `z` / `Z` | Anywhere | Undo / redo |
| `?` | Anywhere | Show every key for the current panel |

## Reviewing an agent's changes

After Claude Code or Codex edits a dozen files, the question is what exactly changed before you commit it. Lazygit is good at that:

1. Open the Files panel and go through each file with delta rendering the diff.
2. Press `enter` on a file and stage only the hunks you agree with. The rest stays in the working tree for the agent to redo.
3. Discard a file with `d` if the change is not worth keeping.
4. Commit what is left, and use `z` if you change your mind.

Staging hunk by hunk is the fastest way to keep the good half of an agent's work and send the rest back.

## Lazygit in Kaku

Kaku opens lazygit in the current pane with `Cmd + Shift + G`, using the directory you are in. If a repository has uncommitted changes and you have not used lazygit there yet, Kaku shows a one-time hint that the shortcut exists. Lazygit and delta are among the optional tools `kaku init` offers to install with Homebrew; the git and lazygit settings above are yours to add.

## FAQ

### Why does lazygit not use delta even though git does?

Lazygit renders its diff panel itself and only uses the renderers listed under `git.diffRenderers` in its own config. Add `- command: delta --dark --paging=never` there.

### Where is the lazygit config file on Mac?

Run `lazygit --print-config-dir`. On a Mac it is usually `~/Library/Application Support/lazygit` or `~/.config/lazygit`, and the command tells you which one your install reads. A repository can also have its own `.git/lazygit.yml`.

### How do I turn off side-by-side diffs in delta?

Remove `side-by-side = true` from the `[delta]` section of `~/.gitconfig`, or set it to `false`.

### Is the brew package called delta or git-delta?

The formula is `git-delta`, and `brew install delta` installs the same thing through an alias. Either way the command is `delta`.

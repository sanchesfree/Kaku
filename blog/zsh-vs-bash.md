# Zsh vs Bash on Mac: Which Shell Should You Use

> Why macOS moved to zsh, the differences you notice day to day, which shell to write scripts in, and how to switch with chsh or Terminal settings.

Published 2026-10-04 · Tw93 · https://kaku.fun/blog/zsh-vs-bash

Since macOS 10.15, zsh is the default login shell and interactive shell, and it is the default for every newly created user account (checked October 2026). bash was the default in macOS 10.14 and earlier, and `/bin/bash` is still a shell you can select. Use zsh for the shell you type in. For scripts, zsh is highly compatible with the Bourne shell (sh) and mostly compatible with bash, with some differences, so write portable scripts for sh, and use bash when the script depends on bash-only syntax.

## What changed in macOS 10.15

Apple documents the default and the ways to change it in [Use zsh as the default shell on Mac](https://support.apple.com/en-us/102360). From macOS 10.15, zsh is the default login shell and the default interactive shell, and it is the default for every user account created on that release or later. macOS 10.14 and earlier defaulted to bash. Those older releases can use zsh as the default too.

zsh is already on the system at `/bin/zsh`, and `/bin/bash` stays selectable. If you start bash while the account uses another shell, macOS prints a message that the default interactive shell is now zsh. Hide that message with a line in `~/.bash_profile` or `~/.profile`:

```bash
export BASH_SILENCE_DEPRECATION_WARNING=1
```

## Startup files, the prompt, and completion

`.zprofile` corresponds to `.bash_profile` and runs at login, including over SSH. `.zshrc` corresponds to `.bashrc` and runs for each new Terminal session. Environment variable exports can be copied from the bash file as written:

```bash
export MY_SETTING=1
```

A POSIX `.profile` can be sourced from `.zprofile`:

```bash
[[ -e ~/.profile ]] && emulate sh -c 'source ~/.profile'
```

zsh recognizes a different set of prompt specifiers than bash, and its color syntax does not need ANSI escape sequences. Apple's page converts this bash prompt from `.bash_profile`:

```bash
export PS1="\[\e[92;40m\]\h\[\e[m\]:\[\e[93m\]\W\[\e[m\] \\$ "
```

into this zsh prompt for `.zprofile` or `.zshrc`:

```bash
export PS1="%10F%m%f:%11F%1~%f \$ "
```

`man zsh` in Terminal is where Apple sends you for those specifiers, and for zsh's command-line completion system. For a `.zshrc` that loads history suggestions, syntax highlighting, extra completions, and a prompt on its own, see [Zsh without Oh My Zsh](/blog/zsh-without-oh-my-zsh).

## Scripts

On macOS 10.15 or later, you can test Bourne-compatible scripts by changing `/var/select/sh` to `/bin/bash`, `/bin/dash`, or `/bin/zsh`. If you point `/var/select/sh` at a shell other than bash, scripts that use bashisms (bash-only syntax) may not work properly.

For a single test, run zsh in sh emulation:

```bash
zsh --emulate sh
```

## How to switch shells

`chsh -s` changes the account's default login shell. Run it in Terminal, and pass a path listed in `/etc/shells`, such as `/bin/zsh`, `/bin/bash`, `/bin/csh`, `/bin/dash`, `/bin/ksh`, `/bin/sh`, or `/bin/tcsh`.

```bash
chsh -s /bin/zsh
```

To make bash the default again:

```bash
chsh -s /bin/bash
```

On macOS 13 or later, open System Settings from the Apple menu, click Users & Groups, Control-click your user name or picture in the list on the right, and choose Advanced Options. Enter your user name and password, choose a shell from the Login shell menu, and click OK. On earlier macOS, open System Preferences, click Users & Groups, click the lock, enter your user name and password, Control-click your user name on the left, choose Advanced Options, pick a shell from the Login shell menu, and click OK.

The Login shell menu changes the same account default as `chsh`. To use another shell only in new Terminal windows and tabs, leave that default in place. From the Terminal menu, choose Settings (or Preferences). On the General pane, select "Command (complete path)", and enter a path from `/etc/shells`, such as `/bin/zsh` or `/bin/bash`.

## If you use Kaku

Kaku's shell setup is built for zsh and fish. `kaku init` adds two lines to `~/.zshrc`, one for PATH and one that sources Kaku's shell integration, which loads zsh-autosuggestions, fast-syntax-highlighting, zsh-completions and zsh-z, and it offers to install Starship, Delta, Lazygit and Yazi through Homebrew. The Starship prompt and Smart Tab only start inside Kaku, so other terminals keep the prompt they already had. `kaku doctor` checks the zsh and fish integration.

On bash, Kaku only wraps `ssh` and `mosh` so they fall back to `xterm-256color` when a remote host has no `kaku` terminfo entry, the same wrapper zsh and fish get. If you would rather assemble the zsh pieces yourself, [Zsh without Oh My Zsh](/blog/zsh-without-oh-my-zsh) walks through the same setup in a `.zshrc` you own.

## FAQ

### Is bash still available on macOS?

Yes. `/bin/bash` is one of the shells in `/etc/shells`, and it was the default through macOS 10.14. Starting bash while the account default is another shell prints a message that the default interactive shell is now zsh. `export BASH_SILENCE_DEPRECATION_WARNING=1` in `~/.bash_profile` or `~/.profile` hides that message.

### How do I switch the default shell to zsh or back to bash?

Run `chsh -s /bin/zsh` or `chsh -s /bin/bash`. The path has to be listed in `/etc/shells`. On macOS 13 or later the same choice is under System Settings, Users & Groups, Advanced Options, Login shell. To change only new Terminal windows and tabs, set Terminal's General pane to "Command (complete path)" and leave the account default alone.

### Where do `.bash_profile` and `.bashrc` settings go?

Login settings, including ones that should apply over SSH, go in `.zprofile`, which corresponds to `.bash_profile`. Settings for each new Terminal session go in `.zshrc`, which corresponds to `.bashrc`. `export` lines can be copied as they are. The prompt uses zsh specifiers, so use the zsh `PS1` above in `.zprofile` or `.zshrc`, and see `man zsh` for the rest. A POSIX `.profile` can be sourced from `.zprofile` with `emulate sh`.

### How do I test a script against sh?

On macOS 10.15 or later, change `/var/select/sh` to `/bin/bash`, `/bin/dash`, or `/bin/zsh`. If that path points to a shell other than bash, scripts that use bashisms may not work properly. `zsh --emulate sh` runs zsh in sh emulation.

### Does Kaku set up bash the way it sets up zsh?

`kaku init` sets up zsh, fish, or both. The zsh plugins and Smart Tab belong to the zsh setup, and the Starship prompt is available to zsh and fish inside Kaku. The bash integration wraps `ssh` and `mosh` so they fall back to `xterm-256color` when the remote host has no `kaku` terminfo entry, and the zsh and fish integrations do the same.

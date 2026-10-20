# Setting Up Codex CLI on Mac: Install, Login and Config

> Install OpenAI's Codex CLI on macOS, sign in with ChatGPT or an API key, and set up config.toml, approvals, notifications and resuming sessions.

Published 2026-09-29 · Tw93 · https://kaku.fun/blog/codex-cli-setup

Setting up Codex CLI on a Mac takes three commands: install it with `brew install --cask codex`, sign in with `codex login`, then run `codex` inside a project. Common user settings live in `~/.codex/config.toml`, including the model, permissions and notifications. It was checked against Codex CLI 0.163.0 in October 2026.

## Install

Pick one of the three official ways:

```bash
# Homebrew
brew install --cask codex

# The install script
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# npm
npm install -g @openai/codex
```

Check it with `codex --version`, and update it later with the same tool you installed it with. If something looks wrong, `codex doctor` checks the installation, config, login and runtime in one go.

## Sign in

`codex login` opens a browser and signs you in with your ChatGPT account, which is the usual choice if your plan includes Codex. To use an API key instead, pipe it in rather than pasting it on the command line, so it does not land in your shell history:

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

On a machine without a browser, `codex login --device-auth` gives you a code to enter on another device. With file-based storage, credentials go in `auth.json` under `CODEX_HOME` (by default `~/.codex`); [`cli_auth_credentials_store`](https://learn.chatgpt.com/docs/config-file/config-reference) can also select the system keyring or memory-only storage. `codex login status` shows which account is active, and `codex logout` removes it.

## Where the settings come from

Codex reads its settings in layers, and a setting closer to the current run wins.

![Four layers of Codex settings, from command line flags at the top through project config and user config to built-in defaults](https://kaku.fun/img/blog/codex-config-layers.webp)

*A flag on the command line beats the project file, which beats your user file.*

- **Built-in defaults** apply when nothing else sets a value.
- **`~/.codex/config.toml`** is your user config and applies to every session.
- **`.codex/config.toml`** inside a repository overrides it for that project.
- **Flags** such as `-m`, `-s`, `-a` and `-c key=value` override everything for one run.

`-c` takes any key from the config file, with dots for nested tables, so `codex -c tui.notification_method=osc9` lets you test a setting before saving it to your config file. You can also use named profiles: `codex -p work` layers `~/.codex/work.config.toml` on top of the user config.

## The settings worth changing first

A small user config covers most needs:

```toml
model_reasoning_effort = "medium"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[tui]
notification_method = "osc9"
```

Leave `model` out to use the default, or set it to one of the names `/model` lists inside a session, since the list depends on your account. `/model` also switches models for the current session without editing the file.

The two settings that decide how much Codex does on its own are worth understanding before you change them:

| Setting | Values | What it means |
|---|---|---|
| `sandbox_mode` | `read-only`, `workspace-write`, `danger-full-access` | What commands Codex runs may touch. `workspace-write` allows writes inside the project and keeps the rest of the disk read-only |
| `approval_policy` | `on-request`, `never` | `on-request` lets the model ask before stepping outside the sandbox; `never` never asks and returns failures straight to the model |

`workspace-write` with `on-request` is a sensible start. `danger-full-access` with `never` removes both guards, which is meant for machines that are already isolated, not for your laptop.

## Notifications

By default, Codex rings the terminal bell when it finishes or needs approval, and only while the terminal is not focused. Whether that bell becomes a desktop notification depends on the terminal. Kaku turns a bell from a background window into a desktop notification, and with `notification_method = "osc9"` the notification carries Codex's own message instead of a generic alert. `tui.notification_condition = "always"` notifies even when the terminal is in the foreground.

If nothing shows up, the [notification guide](/blog/claude-code-notifications) covers the macOS permissions and tmux settings that can block them.

## Picking a session back up

Codex records every interactive session, so closing the terminal does not lose the conversation:

```bash
codex resume          # pick from recent sessions
codex resume --last   # continue the most recent one
codex fork --last     # branch off the most recent one, leaving it intact
```

The terminal side is separate. In Kaku, the tabs and splits you had open come back after a restart, and a pane that was running Codex keeps its last screen, so you can see where each session stopped before you resume it.

## Using your Codex login inside Kaku

Kaku has its own assistant for `#` command generation and `Cmd + L` chat. Instead of a second API key, it can reuse your existing Codex connection: run `kaku ai`, choose Kaku Assistant, and set Auth Type to `codex`. Kaku then reads the user-level Codex config, including a ChatGPT login or API key and the selected provider. The Codex entry on the same screen shows Codex's own model and login state.

## FAQ

### Is Codex CLI free?

The CLI is open source, but using it requires either a ChatGPT plan that includes Codex or an OpenAI API key billed per use.

### Where is the Codex config file on Mac?

`~/.codex/config.toml` for your user settings, and `.codex/config.toml` in a repository for project settings. Set `CODEX_HOME` to move the user directory somewhere else.

### How do I change the model in Codex CLI?

Use `/model` inside a session, `codex -m <model>` for one run, or set `model` in `~/.codex/config.toml` for every session.

### How do I continue a Codex session after closing the terminal?

Run `codex resume --last` in the same project, or `codex resume` to choose from a list.

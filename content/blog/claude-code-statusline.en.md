Set `statusLine` in `~/.claude/settings.json` to a shell command. Claude Code pipes the current session to that command as JSON on stdin, and prints the script's stdout at the bottom of the screen, in a row above the footer badges. `/statusline` can generate the script and write the setting. Checked October 2026 against the [status line docs](https://code.claude.com/docs/en/statusline).

## Set it up

`/statusline` writes a script under `~/.claude/` and updates your settings. Approve the file-edit prompts if it asks.

```text
/statusline show model name and context percentage with a progress bar
```

You can also edit `~/.claude/settings.json` or [project settings](https://code.claude.com/docs/en/settings#where-settings-live). Set `type` to `"command"`. The `command` field accepts a script path or an inline shell command, and `padding` adds extra characters of indentation, defaulting to `0`.

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2
  }
}
```

With [`jq`](https://jqlang.org/) on your `PATH`, an inline command requires no script file:

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

`refreshInterval` runs the command every N seconds, with a minimum of `1`. Setting `hideVimModeIndicator` to `true` hides the built-in `-- INSERT --` line when your script prints `vim.mode` (`NORMAL`, `INSERT`, `VISUAL`, or `VISUAL LINE`). The `vim` object exists only while vim mode is active.

Saving the file reloads settings and runs the command immediately. To remove the status line, run `/statusline delete`, `/statusline clear`, or `/statusline remove it`.

With a status line configured, Claude Code hides most footer hints, including `esc to interrupt`, `? for shortcuts`, and `hold space to speak`. It also hides the status row during the help menu and permission prompts. [ccstatusline](https://github.com/sirmalloc/ccstatusline) and [starship-claude](https://github.com/martinemde/starship-claude) provide pre-built configurations.

## What the JSON contains

| Field | What it is |
|---|---|
| `model.display_name`, `model.id` | Current model name and identifier |
| `workspace.current_dir` | Working directory. `cwd` matches it. Prefer `workspace.current_dir` |
| `workspace.project_dir` | Directory where Claude Code was launched |
| `context_window.used_percentage` | Context used. May be `null` early |
| `context_window.context_window_size` | Max tokens: 200000, or 1000000 with extended context |
| `cost.total_cost_usd` | Estimated session cost in USD |
| `cost.total_duration_ms` | Wall-clock milliseconds the session has been running |
| `session_id` | Stable id for this session |

[[figure:claude-code-statusline|Session JSON goes to the script on stdin, and the printed line is what shows under the input|The branch is not in that JSON. The script asks git for it.]]

`used_percentage` sums `input_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens`, excluding `output_tokens`. Both `total_input_tokens` and `total_output_tokens` are `0` before the first API response. `current_usage` is `null` before the first call and again after `/compact`, until the next call. Using `// 0` provides a fallback for a null percentage. If the row displays `--` after several messages, restart the session. `/context` can report a higher number because it estimates messages added since that response.

`cost.total_cost_usd` is a client-side list-price estimate, unless a [`modelPricing`](https://code.claude.com/docs/en/settings-reference#modelpricing) table applies, and can differ from the actual bill. `/clear` resets this total to $0. Before v2.1.211, it carried over. `total_duration_ms` accumulates across resumed sessions and excludes time when the session is not running. `total_api_duration_ms` measures API wait time. The script consumes no tokens.

No field contains the checked-out branch. `workspace.git_worktree` names a linked worktree from `git worktree add`, while `worktree.branch` exists only in a worktree session.

## Model, context, and git branch

The script prints the model, folder, context percentage, and git branch. Running `wc -l` on `git diff --cached --numstat` and `git diff --numstat` counts staged and modified tracked files. `\033[32m` formats a green `+`, `\033[33m` formats a yellow `~`, and `\033[0m` resets formatting. `echo -e` enables the escape sequences.

Cache git status for 5 seconds at `/tmp/statusline-git-cache-$SESSION_ID`. The `session_id` stays the same for the whole session, while `$$` changes on every run and would never hit the cache. Run `stat -c %Y` (Linux) before `stat -f %m` (macOS): on Linux, the macOS syntax prints a filesystem report before failing. Git commands run in the script's directory, as these examples do not `cd` to `workspace.current_dir`. If `git branch --show-current` returns empty, the branch is omitted.

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
SESSION_ID=$(echo "$input" | jq -r '.session_id')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

CACHE_FILE="/tmp/statusline-git-cache-$SESSION_ID"
CACHE_MAX_AGE=5

cache_is_stale() {
  [ ! -f "$CACHE_FILE" ] || \
  [ $(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0))) -gt $CACHE_MAX_AGE ]
}

if cache_is_stale; then
  if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    STAGED=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
    MODIFIED=$(git diff --numstat 2>/dev/null | wc -l | tr -d ' ')
    echo "$BRANCH|$STAGED|$MODIFIED" > "$CACHE_FILE"
  else
    echo "||" > "$CACHE_FILE"
  fi
fi

IFS='|' read -r BRANCH STAGED MODIFIED < "$CACHE_FILE"

if [ -n "$BRANCH" ]; then
  GIT_STATUS=""
  [ "$STAGED" -gt 0 ] && GIT_STATUS="${GREEN}+${STAGED}${RESET}"
  [ "$MODIFIED" -gt 0 ] && GIT_STATUS="${GIT_STATUS}${YELLOW}~${MODIFIED}${RESET}"
  echo -e "[$MODEL] ${DIR##*/} | ${PCT}% | $BRANCH $GIT_STATUS"
else
  echo "[$MODEL] ${DIR##*/} | ${PCT}%"
fi
```

`${DIR##*/}` extracts the folder name, and `cut -d. -f1` drops the decimal fraction. Save the script to `~/.claude/statusline.sh` and make it executable with `chmod +x`.

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/home/user/project"},"context_window":{"used_percentage":25},"session_id":"test-session-abc"}' | ./statusline.sh
```

This outputs `[Opus] project | 25%`, plus the branch if `git rev-parse --git-dir` succeeds in the script's directory. Terminal width comes from `$COLUMNS` and `$LINES`. `tput cols` cannot inspect the terminal because stdout is captured.

## Colors and icons

A common pattern colors the context percentage green under 70%, yellow from 70% through 89%, and red from 90% (`\033[31m`), with the model name in cyan (`\033[36m`). Each `echo` outputs a separate row, so two `echo` lines create a two-row status line. A 10-character bar can be built by padding with `printf -v` and replacing spaces with `▓` and `░`. These styles require a terminal with ANSI color support, and an emoji or Nerd Font icon renders only when an active font includes that glyph.

To print a clickable link, format an OSC 8 escape sequence (`\e]8;;URL\a`, the text label, and `\e]8;;\a`) with `printf '%b'`. On macOS, open the link with Cmd-click. iTerm2, Kitty, and WezTerm support OSC 8 hyperlinks, while Terminal.app does not. Set `FORCE_HYPERLINK=1` if the label is not clickable. SSH and tmux may strip escape sequences. When not in fullscreen, MCP errors, automatic updates, and low-context warnings can truncate this row.

## How often it runs

The status line runs at session start, including when resuming, and whenever:

- A new assistant message arrives
- `/compact` finishes
- The permission mode changes
- Vim mode toggles
- `statusLine.command` changes
- `refreshInterval` elapses, if set
- A rate-limit window in the last JSON reaches `resets_at`
- A warm prompt cache in that JSON reaches `expires_at`

Script execution is debounced by 300ms, though updating `command` bypasses debounce. A newer update cancels any in-flight script. Edits to the script file take effect on the next trigger, whereas saving settings runs the command immediately. Displaying the row requires an exit code of 0 and output on stdout. Running `claude --debug` logs stderr on every run and records the first exit code. Idle periods, including a coordinator waiting on subagents, pause these trigger events, which is what `refreshInterval` is for.

## Icons and plan usage in Kaku

Kaku renders Nerd Font icons without requiring a patched font. It bundles Symbols Nerd Font Mono as a fallback after your primary font, so status lines printing branch or folder glyphs render in both the default JetBrains Mono and any font configured in `kaku.lua`.

If plan usage is all you need on screen, `kaku ai` already displays it for Claude Code, Codex, Gemini CLI, Copilot CLI, and Kimi Code. Kaku modifies a tool's settings only when you edit them in that panel, and never installs a status line or hooks automatically.

## FAQ

### Why is the status line blank?

Ensure the script is executable, prints to stdout, and exits with code 0. Before workspace trust is accepted, `claude --debug` logs `Status line command skipped: workspace trust not accepted`. A `statusLine` runs a shell command under the [hook](/blog/claude-code-hooks) trust rule. Setting `disableAllHooks` to `true` outside managed settings permits only managed status lines, while `allowManagedHooksOnly` drops your custom command.

### Why does the percentage disagree with /context?

The status line reflects data from the most recent API response, whereas `/context` includes estimates for messages added since that response. `used_percentage` excludes `output_tokens`.

### Does the status line cost money?

No. The script spends no API tokens. `cost.total_cost_usd` is a list-price estimate, reset to $0 by `/clear`. Before v2.1.211 that total carried over.

### How do I show the 5-hour and 7-day limits?

claude.ai Pro and Max subscribers, as well as Claude apps gateways with a spend limit, receive `rate_limits` after the first API response. `five_hour.used_percentage` and `seven_day.used_percentage` range from 0 to 100, and `resets_at` is in Unix seconds. A missing window or one past `resets_at` is omitted from the JSON. Read the value with `jq -r '.rate_limits.five_hour.used_percentage // empty'`.

### Why does the branch sit still while a subagent works?

Trigger events pause while the main session is idle, including when a coordinator waits on subagents. Set `refreshInterval` to at least `1`, keeping the `session_id` cache in place so git does not run on every tick.

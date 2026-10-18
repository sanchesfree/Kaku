Set `statusLine` in `~/.claude/settings.json` to a shell command. Claude Code pipes the current session to that command as JSON on stdin, and prints the script's stdout at the bottom of the screen, in a row above the footer badges. `/statusline` can generate the script and write the setting. Checked October 2026 against the [status line docs](https://code.claude.com/docs/en/statusline).

## Set it up

`/statusline` writes a script under `~/.claude/` and updates your settings. Approve the file-edit prompts if it asks.

```text
/statusline show model name and context percentage with a progress bar
```

Or edit `~/.claude/settings.json`, or [project settings](https://code.claude.com/docs/en/settings#where-settings-live). `type` is `"command"`. `command` is a script path or an inline shell command. `padding` is extra characters of indentation. It defaults to `0`.

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2
  }
}
```

With [`jq`](https://jqlang.org/) on your `PATH`, this needs no script file:

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

`refreshInterval` also runs the command every N seconds, minimum `1`. `hideVimModeIndicator` set to `true` hides the built-in `-- INSERT --` line when the script prints `vim.mode` (`NORMAL`, `INSERT`, `VISUAL`, or `VISUAL LINE`). The `vim` object exists only while vim mode is on.

Saving the file reloads settings and runs the command. Remove the row with `/statusline delete`, `/statusline clear`, or `/statusline remove it`.

With a status line set, Claude Code hides most footer hints, including `esc to interrupt`, `? for shortcuts`, and `hold space to speak`, and hides the row during the help menu and permission prompts. [ccstatusline](https://github.com/sirmalloc/ccstatusline) and [starship-claude](https://github.com/martinemde/starship-claude) provide pre-built configurations.

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

`used_percentage` sums `input_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens`, and leaves out `output_tokens`. `total_input_tokens` and `total_output_tokens` are both `0` before the first API response. `current_usage` is `null` before the first call and again after `/compact`, until the next call. `// 0` covers a null percentage. A row that shows `--` after several messages needs a restart. `/context` can read higher because it estimates messages added since that response.

`cost.total_cost_usd` is a client-side list-price estimate, unless a [`modelPricing`](https://code.claude.com/docs/en/settings-reference#modelpricing) table applies, and it can differ from the bill. `/clear` resets it to $0. Before v2.1.211 it carried over. `total_duration_ms` accumulates across resumes and skips time the session is not running. `total_api_duration_ms` is API wait time. The script spends no tokens.

No field is the checked-out branch. `workspace.git_worktree` names a linked worktree from `git worktree add`. `worktree.branch` exists only in a worktree session.

## Model, context, and git branch

The script prints model, folder, context percentage, and branch. `wc -l` on `git diff --cached --numstat` and `git diff --numstat` counts tracked files, staged then modified. `\033[32m` is a green `+`, `\033[33m` a yellow `~`, `\033[0m` resets. `echo -e` applies them.

Cache git for 5 seconds at `/tmp/statusline-git-cache-$SESSION_ID`. `session_id` is stable per session. `$$` changes every run and never hits. Run `stat -c %Y` (Linux) before `stat -f %m` (macOS): on Linux the macOS form prints a filesystem report before failing. Git uses the script's directory. The examples do not `cd` to `workspace.current_dir`. Empty `git branch --show-current` omits the branch.

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

`${DIR##*/}` is the folder. `cut -d. -f1` drops a fraction. Save as `~/.claude/statusline.sh` and `chmod +x` it.

```bash
echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/home/user/project"},"context_window":{"used_percentage":25},"session_id":"test-session-abc"}' | ./statusline.sh
```

You get `[Opus] project | 25%`, plus a branch when `git rev-parse --git-dir` succeeds in the script's directory. Width comes from `$COLUMNS` and `$LINES`. `tput cols` cannot see the terminal, because stdout is captured.

## Colors and icons

A common pattern colors the context percentage green under 70%, yellow from 70% through 89% and red from 90% (`\033[31m`), with the model name in cyan (`\033[36m`). Each `echo` becomes its own row, so two `echo` lines give you a two-row status line. A 10-character bar is easy to build by padding with `printf -v` and swapping the spaces for `▓` and `░`. All of this needs a terminal with ANSI color, and an emoji or a Nerd Font icon only renders when one of the fonts in use has that glyph.

Print a clickable label as OSC 8, `\e]8;;URL\a` then the text then `\e]8;;\a`, with `printf '%b'`. Cmd-click on macOS. iTerm2, Kitty, and WezTerm support it. Terminal.app does not. Set `FORCE_HYPERLINK=1` when the label will not click. SSH and tmux may strip the sequence. Outside fullscreen, MCP errors, auto-updates, and the context-low warning can truncate this row.

## How often it runs

At session start, including a resume, then when:

- A new assistant message arrives
- `/compact` finishes
- The permission mode changes
- Vim mode toggles
- `statusLine.command` changes
- `refreshInterval` elapses, if set
- A rate-limit window in the last JSON reaches `resets_at`
- A warm prompt cache in that JSON reaches `expires_at`

Debounce is 300ms, skipped when `command` changes. A newer update cancels a running script. Script edits wait for the next trigger. Saving settings runs immediately. The row requires exit 0 and stdout. `claude --debug` logs stderr on every run and the first exit code. Idle time, including a coordinator waiting on subagents, pauses these events, which is what `refreshInterval` is for.

## Icons and plan usage in Kaku

Kaku draws Nerd Font icons without a patched font. It ships Symbols Nerd Font Mono and adds it as a fallback after whatever font you use, so a status line that prints branch or folder glyphs renders in the default JetBrains Mono and in any font you set in `kaku.lua`.

If plan usage is all you want on screen, `kaku ai` already shows it for Claude Code, Codex, Gemini CLI, Copilot CLI and Kimi Code. Kaku changes a tool's settings only when you edit them in that panel, and it never adds a status line or hooks on its own.

## FAQ

### Why is the status line blank?

Make the script executable, print to stdout, and exit 0. Before workspace trust, `claude --debug` logs `Status line command skipped: workspace trust not accepted`. A `statusLine` runs a shell command under the [hook](/blog/claude-code-hooks) trust rule. `disableAllHooks` set to `true` outside managed settings leaves only a managed status line. `allowManagedHooksOnly` drops yours.

### Why does the percentage disagree with /context?

The status line uses the last API response. `/context` estimates messages added since then. `used_percentage` leaves out `output_tokens`.

### Does the status line cost money?

No. The script spends no API tokens. `cost.total_cost_usd` is a list-price estimate, reset to $0 by `/clear`. Before v2.1.211 that total carried over.

### How do I show the 5-hour and 7-day limits?

claude.ai Pro and Max subscribers, and a Claude apps gateway with a spend limit, get `rate_limits` after the first API response. `five_hour.used_percentage` and `seven_day.used_percentage` run from 0 to 100. `resets_at` is Unix seconds. A missing window, or one past `resets_at`, is absent. Read it with `jq -r '.rate_limits.five_hour.used_percentage // empty'`.

### Why does the branch sit still while a subagent works?

Events pause while the main session is idle, including a coordinator waiting on subagents. Set `refreshInterval` to at least `1`, with the `session_id` cache so git does not run every tick.

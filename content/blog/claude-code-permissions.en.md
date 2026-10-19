Claude Code decides whether to ask you with two layers: a permission mode that sets the baseline, and allow, ask and deny rules in `settings.json` that override it for specific tools. `--dangerously-skip-permissions` switches on `bypassPermissions`, the mode that skips the checks, and Anthropic's docs say to use it only in a container or VM, since it offers no protection against prompt injection or unintended actions. For daily work, a middle ground of `acceptEdits` or auto mode, a short allow list, a few deny rules and a hook for the one command you never want is safer and still quiet.

## The permission modes

The [permission modes page](https://code.claude.com/docs/en/permission-modes), read on 19 October 2026, lists these modes by their config value:

| Mode | Runs without asking | Best for |
|---|---|---|
| `default` (shown as Manual) | Reads only | Reviewing every action, sensitive work |
| `acceptEdits` | Reads, file edits and common filesystem commands such as `mkdir`, `touch`, `mv`, `cp` | Iterating on code you review afterwards |
| `plan` | Reads, plus classifier-approved commands when auto mode is available; edits wait until you approve the plan | Exploring before changing anything |
| `auto` | Everything, with a classifier model reviewing actions in the background | Long tasks, fewer prompts |
| `dontAsk` | File reads inside your working directories and pre-approved tools; anything that would prompt is denied | CI and scripts |
| `bypassPermissions` | Everything | Isolated containers and VMs only |

Press `Shift+Tab` to cycle modes in the terminal. The status bar shows which one is active, for example `⏵⏵ accept edits on` or `⏸ plan mode on`. Two modes are not always in the cycle: `dontAsk` never is, and `bypassPermissions` only appears if you started with a flag or setting that enables it. You can also start a session in a mode with `claude --permission-mode plan`, or set `permissions.defaultMode` in a settings file.

One recent change matters if your memory of Claude Code is a few months old. With version 2.1.283 or later, auto mode is the built-in starting mode for interactive terminal and VS Code sessions, and the docs describe it as reducing prompts, not as a safety guarantee. Check the status bar before assuming a session is asking about everything.

## Allow, ask and deny rules

Rules live under `permissions` in `settings.json`, and `/permissions` shows every rule and which file it comes from. Allow rules let a tool run without approval, ask rules always prompt, and deny rules block. They are checked in the order deny, ask, allow, and the first match wins. A deny rule always beats a more specific allow rule, so you cannot carve an exception out of a deny.

A rule is `Tool` or `Tool(specifier)`. A bare `Bash` matches every shell command, and a specifier narrows it:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./secrets/**)",
      "Bash(rm *)"
    ]
  }
}
```

In a Bash rule, `*` matches any text, so put it after the subcommand. `Bash(git log *)` allows only `git log` commands, while `Bash(git *)` allows every git command. Compound commands are split at `&&`, `||`, `;`, pipes and newlines, and each part must match on its own, so `Bash(safe-cmd *)` does not allow `safe-cmd && other-cmd`. For files, `Read` and `Edit` rules use gitignore-style patterns: `//path` is absolute, `~/path` starts at your home directory, and `./path` is relative to the current directory. A rule written for `Write` is accepted but never consulted, so use `Edit`.

## How a call gets decided

The order matters when you combine rules, hooks and modes, so here is the path of one tool call.

[[figure:claude-code-permission-layers|A tool call passes a PreToolUse hook, then deny, ask and allow rules, then the permission mode when no rule matched, and an approved Bash command runs inside the sandbox; a hook exit 2 or a deny rule blocks it|A hook can stop a call before any rule is read, rules settle it next, and the mode only decides what no rule covered.]]

A PreToolUse hook runs first. If it exits with code 2, the call is blocked before any rule is looked at, even when an allow rule would have let it through. If the hook gets past, deny and ask rules are evaluated regardless of what the hook returned, so a hook returning allow cannot override a deny rule. Rules then settle the call, and when none matches, the mode's baseline decides. For Bash, the optional sandbox is a separate layer after approval: it restricts what an approved command can touch at the operating system level. The docs recommend using permissions and the sandbox together, since sandbox limits still hold if a prompt injection fools the model.

Permission rules are enforced by Claude Code, not by the model. The docs say instructions in your prompt or `CLAUDE.md` shape what Claude tries, but they do not change what Claude Code allows.

## What bypassPermissions actually risks

`bypassPermissions` turns off prompts and safety checks, including for writes to protected paths such as `.git`, `.claude`, `.zshrc` and `.mcp.json`. Deny rules still block in this mode, and allow rules have no effect, since everything is allowed. A few things still prompt even here: ask rules, `rm` and `rmdir` aimed at a critical path such as `/` or your home directory, and tools that need your input.

The docs warn that this mode offers no protection against prompt injection, meaning text in a file or web page that Claude reads and then obeys. Their guidance is to use it only in isolated environments such as containers, VMs or dev containers without internet access. The flag is `claude --dangerously-skip-permissions`, equivalent to `--permission-mode bypassPermissions`. On first use of an interactive session you must accept a warning dialog, and on Linux and macOS it refuses to start as root or under `sudo` unless a recognized sandbox is detected. The [sandbox environments page](https://code.claude.com/docs/en/sandbox-environments) compares the built-in sandboxed Bash tool, a sandbox runtime, dev containers and VMs, and the permission modes page says that if you want few prompts without that exposure, auto mode keeps background safety checks.

Administrators can set `permissions.disableBypassPermissionsMode` to `"disable"` in managed settings, and you can set it in your own settings to lock yourself out of the mode.

## A safer middle ground

A setup that keeps most prompts away without turning off the checks:

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git commit *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./secrets/**)",
      "Bash(rm *)",
      "Bash(git push --force *)"
    ]
  }
}
```

Put it in `.claude/settings.json` for a project, or in `~/.claude/settings.json` for every session. `acceptEdits` auto-approves edits and `rm` inside the working directory, which is why the deny rule on `Bash(rm *)` is there. The docs note a rule can miss a command written another way, for example a push as `git -C . push` is not matched by `Bash(git push *)`. Treat rules as guard rails for common cases, not as a security boundary, and add a hook or the Bash sandbox for what must never happen.

## Hooks that block commands

A hook is a script that Claude Code runs before a tool call. Exit code 2 blocks the call, and whatever the script writes to stderr goes back to Claude as the reason. The docs' own example protects files, and this is a variant for commands:

```bash
#!/bin/bash
# .claude/hooks/block-danger.sh
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ "$CMD" == *"git push --force"* || "$CMD" == *"rm -rf"* ]]; then
  echo "Blocked: $CMD matches a protected pattern" >&2
  exit 2
fi
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-danger.sh" }
        ]
      }
    ]
  }
}
```

Run `chmod +x .claude/hooks/block-danger.sh`, then ask Claude to run one of the blocked commands. It should be refused, and Claude gets your message as the reason. The docs suggest this pattern when you want to allow all Bash commands except a few: add `Bash` to the allow list and have a hook reject the exceptions. A string match like this is easy to get around with a different spelling, so for anything that can destroy data, pair it with a deny rule. More on hook events and settings is in [Claude Code hooks](/blog/claude-code-hooks).

## Knowing when a prompt is waiting

Fewer prompts is the goal, but the ones that remain stall a session if you are in another window. Claude Code 2.1.295 or later reports to Kaku whether it is working, waiting on you or done, so Kaku 0.25.0 or later sends a notification with no setting while Kaku is in the background. Older versions and other terminals need a channel configured, which [Claude Code notifications](/blog/claude-code-notifications) covers. If you also run several agents side by side, [git worktrees](/blog/claude-code-git-worktrees) keep their edits apart.

## FAQ

### Is --dangerously-skip-permissions safe?

Not on your normal machine. The docs restrict it to isolated environments and say it gives no protection against prompt injection. Use auto mode or the middle ground above for local work.

### How do I turn permission prompts off for one command only?

Add an allow rule for that command, such as `Bash(npm test *)`, or choose "Yes, and don't ask again" on the prompt. For Bash commands that saves a rule to `.claude/settings.local.json` in the repository root.

### Why does Claude still ask in bypass mode?

No mode auto-approves ask rules, `rm` or `rmdir` aimed at a critical path, or tools that need your input, so those still prompt in bypass mode.

### Can CLAUDE.md block a command?

No. It shapes what Claude tries, but only rules, modes and hooks change what Claude Code allows.

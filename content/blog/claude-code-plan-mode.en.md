Plan mode lets Claude Code read the repo and write a plan, and blocks edits to your source until you approve that plan, except in an interactive terminal session that already has bypass permissions available. Cycle to it with `Shift + Tab`, prefix one prompt with `/plan`, or start with `claude --permission-mode plan`. Approving the plan exits plan mode and continues in the permission mode specified by that option.

## What plan mode does and does not allow

[Common workflows](https://code.claude.com/docs/en/common-workflows) uses plan mode to review a change before it touches disk. The rules below are from [permission modes](https://code.claude.com/docs/en/iam). In an interactive terminal with bypass permissions available, Claude is still instructed to plan without editing, but any file edit or shell command it attempts during planning runs without a prompt. An ask rule still prompts, and so does `rm` or `rmdir` on a critical path, such as the filesystem root, your home directory, or the working directory.

Shell commands during planning follow the first matching case. Checked October 2026:

- Bypass permissions available, in an interactive terminal: neither the classifier nor a prompt applies to planning commands.
- Auto mode available and `useAutoModeDuringPlan` on, the default: the classifier reviews shell commands other than critical-path removals. Approved commands run, and rejected ones are blocked.
- Auto mode unavailable, or `useAutoModeDuringPlan` off: commands outside the built-in read-only set prompt, including when sandbox auto-allow is on.

With auto mode available, the mode table lists plan mode as reads plus classifier-approved commands. Availability depends on the Claude Code version, the model, and organization settings. Protected paths, including `.git`, `.claude`, and `.zshrc`, are not auto-approved: they go to the classifier when auto mode is available during planning, and prompt when it is not. Plan files under `~/.claude/plans/`, or the `plansDirectory` you set, are exempt.

## Turning it on

`Shift + Tab` cycles permission modes, one per press. From `auto`, one press selects Manual (`default`), the next `acceptEdits`, and the next `plan`. The status bar shows `manual mode on`, `accept edits on`, or `plan mode on`.

Optional modes slot in after `plan`, `bypassPermissions` first and `auto` last. `dontAsk` is outside the cycle. On Windows, when the Node or Bun runtime has not enabled VT input mode, `Alt + M` cycles instead. Another `Shift + Tab` leaves plan mode without approving.

```bash
claude --permission-mode plan
```

The same flag works with `-p`. To start in plan mode by default, save this in the project's `.claude/settings.json` for terminal sessions there, or in `~/.claude/settings.json` for every terminal session on the machine:

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

A project or managed value outranks the user file. `auto` and `bypassPermissions` do not take effect from `.claude/settings.json` or `.claude/settings.local.json`, but `plan` does. The VS Code extension ignores that project file for its starting mode. Set `claudeCode.initialPermissionMode` to `plan` in VS Code user settings instead.

From Claude Code v2.1.283, interactive terminal sessions start in auto mode. Before that, auto is the built-in start on Pro, Max, and Team plans when the session fetches feature flags, from v2.1.228 on macOS, Linux, and WSL and from v2.1.233 on native Windows. Other built-in cases start in Manual. A flag or `permissions.defaultMode` overrides that. If auto is selected and unavailable, the session starts in Manual. The first session after an install or upgrade can differ, before feature flags arrive.

After you approve a plan, pressing `Shift + Tab` or starting a prompt with `/plan` enters plan mode again.

## A good plan prompt

Name the change, what must stay the same, and what the plan should list.

```text
/plan Add a null check in src/auth/user.ts before the profile lookup.
Keep the current error type. List every file you would change, the test command you would run, and anything you would leave alone.
```

`@src/auth/user.ts` includes that file when it fits within the Read tool limit, 25,000 tokens by default. A text file larger than 256KB is not included. `Ctrl + J`, or a backslash followed by Enter, inserts a newline in any terminal, and the [terminal comparison](/blog/best-terminal-for-claude-code) lists where `Shift + Enter` works without setup.

## Approving and editing the plan

When the plan is ready, Claude asks how to proceed.

"Yes, and use auto mode" approves the plan and continues in auto mode. If auto mode is not available, the option reads "Yes, auto-accept edits". If the session started with bypass permissions, it reads "Yes, and switch to BYPASS PERMISSIONS (no further prompts) for this session". "Yes, manually approve edits" approves the plan and lets you review each edit. "No, keep planning" stays in plan mode so you can say what to change.

Approving exits plan mode and switches to the permission mode described by that option. `Ctrl + G` opens the proposed plan in your default text editor before Claude proceeds.

## When to skip it

Use plan mode for a change you want to read before it touches disk, or to explore a codebase before changing it.

In Manual mode, reads run without a prompt. The status bar shows `manual mode on`. Start with `claude --permission-mode default`, or `manual`, which the CLI accepts as an alias.

`acceptEdits` fits edits you will review with `git diff`. From Manual mode, pressing `Shift + Tab` once enters it, or start with `claude --permission-mode acceptEdits`. The status bar shows `accept edits on`. It auto-approves file edits, plus `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, and `sed`, inside the working directory or `additionalDirectories`, including commands with a prefix such as `LANG=C` or a wrapper such as `timeout`. Other shell commands, protected-path writes, and critical-path `rm` or `rmdir` still prompt.

Auto mode fits a long task where you trust the direction. It runs the work under background safety checks and reduces routine prompts. It does not guarantee safety.

## Plan mode vs thinking effort

Plan mode controls which actions can run. Extended thinking and the effort level change how deeply Claude reasons through a request.

`Option + T` on macOS, or `Alt + T` on Windows and Linux, toggles extended thinking. It has no effect on Opus 5.5, Sonnet 5.5, Haiku 5.5, or the Fable models, which always use extended thinking. On macOS it works without configuring Option as Meta.

`/effort` changes the effort level. Claude Code applies it as soon as you send it. Once you confirm the cache warning, if one is shown, the new level applies to the next request in the current turn.

## Shift + Tab in Kaku

Kaku's default terminal shortcuts do not include `Shift + Tab`. It is not on the [keybindings](/docs/keybindings) page, so in a pane the shortcut reaches Claude Code.

If the status bar never changes, open `~/.config/kaku/kaku.lua` and check `config.keys`. Insert into that table rather than assigning a new one, as assigning a new table replaces the defaults. A `Tab` entry with a Shift modifier intercepts the shortcut before Claude Code sees it. Any other terminal that swallows `Shift + Tab` needs the same check.

The AI chat panel is separate. `Cmd + L` opens it, and when Simple Model and Deep Model differ, `Shift + Tab` there switches between them, as [Features](/docs/features) describes. That switch does not cycle Claude Code's permission modes.

## FAQ

### How many Shift + Tab presses reach plan mode?

Three from auto mode, two from Manual mode. Stop when the status bar shows `plan mode on`. `claude --permission-mode plan`, or a prompt starting with `/plan`, skips the presses.

### Can Claude edit files while plan mode is on?

Edits stay blocked until you approve, except in an interactive terminal that already has bypass permissions. Ask rules and critical-path `rm` or `rmdir` still prompt. Other shell commands follow the three cases above.

### How do I change the plan before Claude starts editing?

Press `Ctrl + G` to open the proposed plan in your default text editor. "No, keep planning" stays in plan mode. Another `Shift + Tab` leaves without approving.

### Does a higher effort level replace plan mode?

`Option + T` toggles extended thinking, and `/effort` changes the effort level for the next request. Approving the plan is what exits plan mode and starts the edits.

### Why does Shift + Tab do nothing?

In Kaku, look for `Tab` with Shift under `config.keys` in `~/.config/kaku/kaku.lua`. The AI chat panel uses the same shortcut to switch Simple Model and Deep Model when the two differ. From auto mode, the first press shows `manual mode on`.

A [Claude Code skill](https://code.claude.com/docs/en/skills) is a folder with a `SKILL.md` file: YAML frontmatter, the instructions, and any scripts or reference files beside it. Claude matches the `description` against your task and loads the body when that description matches, or when you type `/skill-name`. `name` sets the command and defaults to the folder name. Personal skills live at `~/.claude/skills/<name>/SKILL.md` for every project on this machine, and project skills live at `.claude/skills/<name>/SKILL.md` for sessions in that repository.

## Skill, CLAUDE.md, slash command, subagent

`CLAUDE.md` is always-loaded guidance. A skill holds a procedure, such as a checklist you would paste again, or a `CLAUDE.md` section that has turned into steps.

`.claude/commands/deploy.md` still creates `/deploy`. Custom commands have been merged into skills, so `.claude/skills/deploy/SKILL.md` creates the same command. A [slash command](https://code.claude.com/docs/en/slash-commands) file accepts the same frontmatter except `name` and `paths`. A skill adds supporting files, and Claude can load it when the description matches.

A [subagent](https://code.claude.com/docs/en/sub-agents) has its own context window, system prompt, tools, and permissions, and returns a summary. Files live in `~/.claude/agents/` or `.claude/agents/`. Claude delegates from each `description`. Custom descriptions, built-ins excluded, warn at startup past 15,000 tokens (checked October 2026). `context: fork` runs the skill body as the task, and that subagent does not see the conversation. Omit `agent` and the type is `general-purpose`.

| | Path | Loaded up front | Runs when |
|---|---|---|---|
| `CLAUDE.md` | Project memory | The file | Stays loaded |
| Skill | `~/.claude/skills/` or `.claude/skills/` | Name and description | A match, or `/name` |
| Command file | `.claude/commands/deploy.md` | Same as a skill | `/deploy` |
| Subagent | `~/.claude/agents/` or `.claude/agents/` | Its `description` | Claude delegates, or you name it |

`disable-model-invocation: true` leaves the description out of context. You still run the skill with `/name`.

## Anatomy of SKILL.md

The opening `---` must be the first line. Fields are optional, lowercase, and hyphenated, except `when_to_use`. `description` is what Claude matches. An unknown field is ignored. If the YAML does not parse, the skill loads with no fields, so `/name` works and nothing matches on its own.

```yaml
---
name: summarize-changes
description: Summarize uncommitted changes and flag risks. Use when asked what changed.
allowed-tools: Bash(git diff *)
---

!`git diff HEAD`

Summarize the diff in a few bullets. If it is empty, say so.
```

Save it as `~/.claude/skills/summarize-changes/SKILL.md`.

`` !`git diff HEAD` `` runs first, and the output replaces the line. `!` must start the line or follow whitespace. A failed command aborts the invocation. Outside auto mode, so does a command your rules do not allow. The Bash timeout is 2 minutes. `allowed-tools` grants `Bash(git diff *)` for that turn only. The text stays. `user-invocable: false` hides the menu entry and still lets Claude load the skill. With `disable-model-invocation: true`, Claude Code blocks Claude's attempt to run the skill.

## Write a description Claude can match

Say what it does and when to use it, with the use case first. `when_to_use` appends trigger phrases to `description`. Omit `description` and the first non-empty markdown line is used.

Together they are cut at 1,536 characters, which `skillListingMaxDescChars` sets. Names and descriptions are sent every turn, budgeted at 1% of the context window (`skillListingBudgetFraction`, for example `0.02`, or `SLASH_COMMAND_TOOL_CHAR_BUDGET` for a fixed count). Overflow drops the least-used descriptions and keeps the names. Checked October 2026.

`paths` limits automatic loading to globs, in the path-specific rule format. If a skill never fires, the description is missing your words, the YAML failed, or model invocation is off. Ask `What skills are available?`. `/doctor` estimates listing cost. `/skill-doctor` on v2.1.252 or later reports cost and use, skipping bundled and enterprise skills, and an interactive session opens it on the `/plugin` Stats tab.

## Scripts and reference files

Keep `SKILL.md` under 500 lines. Once invoked, the text stays in the conversation and is not read from disk again. After auto-compaction, each skill can keep the first 5,000 tokens of its latest run, from a shared 25,000 token budget that fills newest first (checked October 2026).

Point `SKILL.md` at a reference file and Claude reads that file when the instructions say to. A script is executed, not loaded into the prompt. `${CLAUDE_SKILL_DIR}` is the `SKILL.md` directory. Use it in the body and in `allowed-tools`, as in `Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)`, so the grant matches the command. Workspace trust does not gate the field, including `claude -p` in a folder you have never trusted.

## Invoke a skill by name

`/fix-issue 123` at the start of the message runs the skill. `$ARGUMENTS` is `123`, and `$0` is the first argument. With no placeholder, Claude Code appends `ARGUMENTS:` plus the text you typed. In `go ahead and /deploy to staging`, nothing runs directly. The name is permission for that reply.

At the prompt, `/write-tests /fix-issue 123` loads both, and `123` goes to each. That expansion is the first skill plus up to five, and it stops on a token that is not an inline user-invocable skill. `claude -p` and the Agent SDK load only the first.

## Share skills with a plugin

Commit `.claude/skills/` and sessions in that repository load it, including a cloud session that clones the repo. A [plugin](https://code.claude.com/docs/en/plugins) installs skills, subagents, hooks, or MCP servers together. Its manifest is `.claude-plugin/plugin.json`, and its skill runs as `/plugin-name:skill-name`.

A marketplace is a repository with `.claude-plugin/marketplace.json`. Claude Code adds Anthropic's official marketplace on the first interactive terminal session. From `/plugin`, install on the Discover tab, or by name:

```text
/plugin install skill-creator@claude-plugins-official
```

User scope is you, in every project on this computer. Project scope is the committed `.claude/settings.json`, and each collaborator still installs the plugin. Local scope is you, in this repository. The plugin then loads in every session. For a skill Claude can invoke, the name and description are in context every turn and count toward usage. The body loads when the skill runs. Official-marketplace plugins show a Context cost on the Marketplaces tab before install (checked October 2026). `skillOverrides` does not affect plugin skills. Disable one with `/plugin` or `claude plugin disable`.

## Common mistakes

Repeating `CLAUDE.md` in a description spends the listing on every turn. Leave the facts in `CLAUDE.md`. `/doctor` flags a local file that duplicates a checked-in one, and offers to move always-loaded guidance into skills. A long description is cut at 1,536 characters, and once the 1% budget fills, the least-used descriptions go first.

When `/name` works and Claude never selects the skill, the description missed the listing. `claude --debug` shows a YAML error. `claude plugin validate ~/.claude/skills` finds frontmatter that does not parse (v2.1.233 or later). Outside a plugin, `<`, a zero-width space, or a leading or trailing space in the folder name keeps the skill from loading.

A rule for every edit belongs in a hook. `hooks` in frontmatter starts when the skill runs and lasts the session. In the body, write a standing instruction such as "Run the tests after every edit", because later turns do not re-read the file. After compaction, invoke the skill again. Only the start of it is kept.

## Open a pane for a long job

[Kaku's CLI](https://kaku.fun/docs/cli) drives the multiplexer from a script or another tool. A skill can open a pane for a long build, test, or log:

```bash
kaku cli split-pane -- bash -c "echo hello"
```

With no command, `kaku cli split-pane` splits the current pane. `kaku cli --help` lists every subcommand.

## FAQ

### Where do I put a skill I want in every project?

`~/.claude/skills/<skill-name>/SKILL.md`. Cowork and cloud sessions skip that path and load skills from your claude.ai account. A cloud session also loads project skills committed in the repo. Look for a missing folder in `~/.claude/skills/.trash/`.

### Why does `/name` work when Claude never uses the skill?

Automatic matching needs the description. Broken YAML leaves it empty, and `disable-model-invocation: true` omits it on purpose. Ask `What skills are available?`, or run `/skill-doctor` on v2.1.252 or later.

### Should this be a skill or a subagent?

A skill runs in the main conversation. A subagent returns a summary from its own context, and `context: fork` makes the skill body that task.

### How do I stop Claude from deploying on its own?

Set `disable-model-invocation: true`, then run `/deploy` yourself. `Skill(deploy)` in deny rules blocks the Skill tool. In `skillOverrides`, `"deploy": "user-invocable-only"` keeps `/deploy` in the menu, and `"off"` hides it.

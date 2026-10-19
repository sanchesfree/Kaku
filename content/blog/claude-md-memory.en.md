`CLAUDE.md` is a plain Markdown file that Claude Code reads at the start of every session, so you stop retyping the same build commands and house rules. Put project rules in `./CLAUDE.md` and commit it, put personal preferences in `~/.claude/CLAUDE.md`, and keep each file under about 200 lines, because every line is paid for in context on every turn. Run `/init` to get a first draft, then cut it down to what Claude cannot work out from the code.

## The files Claude Code reads

Claude Code has two memory systems, and they are easy to mix up. [CLAUDE.md files](https://code.claude.com/docs/en/memory) are instructions you write. Auto memory is notes Claude writes about your corrections and preferences, stored in `~/.claude/projects/<project>/memory/`, with the first 200 lines or 25KB of its `MEMORY.md` index loaded each session. This post is about the first kind, with a short note on the second near the end.

CLAUDE.md files can live in four places. The docs list them from broadest to most specific, and a project instruction lands in context after a user instruction:

| Scope | Location | Shared with |
|---|---|---|
| Managed policy | `/Library/Application Support/ClaudeCode/CLAUDE.md` on macOS | Everyone on the machine, set by IT |
| User | `~/.claude/CLAUDE.md` | Only you, all projects |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | The team, through git |
| Local | `./CLAUDE.local.md` | Only you, this project (add to `.gitignore`) |

The managed file cannot be excluded by individual settings, which is why companies use it for policy. Most people only touch the middle two.

## How the files load

Claude Code does not pick one file. It concatenates all of them into context, so they add up instead of overriding each other. It loads `CLAUDE.md` and `CLAUDE.local.md` from your working directory and every directory above it, ordered from the filesystem root down, so the file closest to where you launched Claude is read last. Inside one directory, `CLAUDE.local.md` comes after `CLAUDE.md`, which puts your personal notes at the end.

Files in subdirectories below your working directory are different. They are not loaded at launch. Claude Code loads one the first time Claude reads, writes or edits a file in that subdirectory. A `packages/api/CLAUDE.md` therefore costs nothing until Claude actually works in `packages/api`. Large monorepos show the opposite problem, an ancestor file written by another team that loads whether you want it or not. List it in `claudeMdExcludes` in `.claude/settings.local.json`, as an absolute path or a glob such as `**/monorepo/CLAUDE.md`, and Claude Code skips it; only the managed policy file cannot be excluded.

[[figure:claude-md-load-order|Managed, user, ancestor and working-directory CLAUDE.md files load at launch in that order and are concatenated into context, while a subdirectory CLAUDE.md loads only when Claude touches a file there|Everything is concatenated into context, the file nearest your working directory is read last, and subdirectory files wait until Claude works there.]]

Two details matter in practice. The content arrives as a user message after the system prompt, not as part of the system prompt, so Claude tries to follow it but nothing enforces it. And block-level HTML comments (`<!-- note for maintainers -->`) are stripped before injection, so you can leave notes for humans without spending tokens on them.

## Imports and the rules folder

A CLAUDE.md can pull in other files with `@path` syntax. Relative paths resolve from the file that contains the import, and imports can nest up to four hops deep:

```markdown
See @README for the project overview and @package.json for npm scripts.

# Workflow
- git workflow @docs/git-instructions.md
```

Imports help you organize a long file, but they do not save context, because imported files load at launch with the file that references them. A path inside backticks stays literal text and is not imported. If an import points outside your working directory, such as `@~/.claude/my-project-instructions.md`, Claude Code asks for approval the first time it meets it in a project.

To genuinely cut cost, use `.claude/rules/`. Each Markdown file there covers one topic, and a file with `paths` frontmatter loads only when Claude works on matching files:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API rules
- Every endpoint validates its input.
```

Rules without `paths` load at launch like the main file. The [skills guide](/blog/claude-code-skills) covers the other half of this split: a multi-step procedure that only matters sometimes belongs in a skill, which loads only when you invoke it or Claude judges it relevant.

## Create one with /init and /memory

Run `/init` inside a project and Claude analyzes the codebase and writes a CLAUDE.md with the build commands, test instructions and conventions it finds. If a file exists, it suggests improvements instead of overwriting it. Treat the output as a draft: delete anything Claude would have found by reading the code, and add what it could not know. `/init` also reads Cursor rules in `.cursor/rules/` and Copilot rules in `.github/copilot-instructions.md`. Setting `CLAUDE_CODE_NEW_INIT=1` first switches it to a multi-phase flow that asks which artifacts to create.

`/memory` lists every memory file for your user and project scopes, including CLAUDE.md entries for files that do not exist yet, and opens any of them in your editor. It also holds the auto memory toggle. To see what actually loaded, run `/context` and read the list under Memory files.

## What belongs in it

The docs say to write down what you would otherwise re-explain: build commands, conventions, project layout and "always do X" rules. Good triggers for a new line are Claude repeating a mistake, a code review catching something it should have known, or you typing the same correction twice. Make each line checkable. "Use 2-space indentation" works; "format code properly" does not.

Here is a small file in that spirit:

```markdown
# Build and test
- Install: `pnpm install`
- Test one file: `pnpm vitest run path/to/file.test.ts`
- Typecheck before finishing: `pnpm tsc --noEmit`

# Conventions
- API handlers live in `src/api/handlers/`
- Use named exports, never default exports

# Gotchas
- `pnpm test` needs a local Redis on port 6379
- Never edit `src/generated/`; run `pnpm codegen` instead
```

What does not belong: secrets, because the file is committed and sent to the model; long reference documents that most tasks never need; anything the code already says, such as directory listings and dependency lists; and rules that must hold every time. For that last case the docs point to a [hook](/blog/claude-code-hooks), since a hook runs as a shell command regardless of what Claude decides. A rule like "never run `rm -rf`" in CLAUDE.md is a request, not a guard.

## Keeping it short

The size advice is concrete. Target under 200 lines per file, because longer files consume more context and reduce how well Claude follows them. Claude Code loads a file of up to 4 MiB, so the limit is about adherence rather than the loader. If a file is over the recommended length you see a warning at startup and in `/status`. Contradictions are the other failure: if two files disagree, Claude may pick one arbitrarily, so prune across the user file, the project file, nested files and the rules folder together. Running `/doctor prompt-audit` asks Claude to look for outdated and conflicting instructions and propose edits without changing anything until you approve.

After `/compact`, the project-root CLAUDE.md is re-read from disk and injected again. An instruction that existed only in conversation is gone, so if you said it twice, add it to the file.

## AGENTS.md and Codex

Codex reads `AGENTS.md` instead. It builds a chain of `~/.codex/AGENTS.override.md` if that exists, otherwise `~/.codex/AGENTS.md`, then one file per directory from the project root down to your working directory, concatenated with later files winning, up to 32 KiB by default. Claude Code reads `AGENTS.md` directly since v2.1.277, but only when no `CLAUDE.md` or `CLAUDE.local.md` sits in your working directory or above it. With both present, it reads your `CLAUDE.md` files only.

To keep one source of truth, put this in `CLAUDE.md`:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

A symlink (`ln -s AGENTS.md CLAUDE.md`) also works, but Claude's edit tools refuse to write through it, and on Windows a committed symlink can check out as a one-line text file. Details on how the two tools compare are in [Codex vs Claude Code](/blog/codex-vs-claude-code), and [Codex CLI setup](/blog/codex-cli-setup) covers its side.

## Using it in Kaku

Kaku does not touch your instruction files. `kaku ai` edits the settings of tools such as Claude Code, keeps fields you wrote yourself, and the [AI coding docs](/docs/ai-coding) say it never adds hooks or instructions to your agents on its own. What Kaku does give you is the surrounding workflow: `Cmd + Click` opens a file path that Claude prints, in the editor named by `file_link_editor`, so you can open the CLAUDE.md path it reports. `Cmd + D` splits a pane, which makes it easy to keep an editor on `CLAUDE.md` next to a running session and check it with `/context`.

## FAQ

### Where do I put personal preferences that should not be committed?

In `./CLAUDE.local.md` at the project root, added to `.gitignore`. It loads after `CLAUDE.md` in the same directory. In a project that relies on `AGENTS.md`, a `CLAUDE.local.md` stops Claude from reading `AGENTS.md` unless you set Project instructions to `claude-md-and-agents-md` in `/config`.

### Why does Claude ignore my CLAUDE.md?

Check `/context` for the file under Memory files first. A subdirectory CLAUDE.md never appears in that list, because it loads on demand; when it loads, a `Loaded` line with its path shows in the terminal. Then look for vague wording and for two files that contradict each other. A rule about commits or pull requests also competes with the git guidance Claude Code adds on its own, so set `includeGitInstructions` to `false` to remove that and use the `attribution` setting for the attribution text. If the rule must always run, use a hook.

### Does a bigger CLAUDE.md make Claude smarter about my project?

No. Past roughly 200 lines the docs say adherence drops and context cost rises. Move path-specific material to `.claude/rules/` and procedures to skills.

### Is CLAUDE.md the same as auto memory?

No. You write CLAUDE.md. Claude writes auto memory, which lives under `~/.claude/projects/<project>/memory/`, is machine-local, and loads only the first 200 lines or 25KB of `MEMORY.md`.

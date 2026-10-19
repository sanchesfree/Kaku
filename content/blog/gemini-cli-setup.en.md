Gemini CLI installs on a Mac with `npm install -g @google/gemini-cli` or `brew install gemini-cli`, and you start it by running `gemini` in a project folder. The catch in 2026 is sign-in: Google announced that on June 18, 2026 Gemini CLI and the Gemini Code Assist IDE extensions would stop serving requests for Google AI Pro and Ultra, and for people using them free of charge through Gemini Code Assist for individuals, and points those users to Antigravity CLI. Organizations on a Code Assist Standard or Enterprise license keep access, and Gemini CLI stays usable with paid Gemini and Gemini Enterprise Agent Platform API keys.

## What changed in 2026

The [Gemini CLI README](https://github.com/google-gemini/gemini-cli) now opens with a note that for unpaid tier and Google One users it was replaced by Antigravity CLI on June 18, 2026, and that it is not optimized for the latest Gemini models. Google's [announcement](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli) lays out the split. Consumers on Google AI Pro, Ultra or the free Code Assist tier lose access. Organizations on Gemini Code Assist Standard or Enterprise keep it, and Gemini CLI stays usable with paid Gemini and Gemini Enterprise Agent Platform API keys.

This matters because many older tutorials still say "sign in with Google and get a free daily quota", and for personal accounts that flow ended on June 18, 2026. If you are a new individual user, start with Antigravity CLI. If you have a paid API key or an organization account, or you maintain scripts built on `gemini`, read on.

## Install on a Mac

The docs recommend macOS 15 or later, Node.js 20.0.0 or later, and 4 GB of RAM for light use. The README lists these options:

```bash
# Try it without installing
npx @google/gemini-cli

# Global install with npm
npm install -g @google/gemini-cli

# Global install with Homebrew
brew install gemini-cli
```

MacPorts (`sudo port install gemini-cli`) also works. Check with `gemini --version`. Releases come in three channels: `latest` is the weekly stable build, `preview` is published each Tuesday and may contain regressions, and `nightly` is built daily from main. Pin one with `npm install -g @google/gemini-cli@preview`.

## Signing in

Run `gemini` and pick a method from the prompt, or change it later with `/auth`. The README documents three:

| Method | How | Best for |
|---|---|---|
| Sign in with Google | Browser login, credentials cached locally | Organization accounts with a Code Assist license; set `GOOGLE_CLOUD_PROJECT` |
| Gemini API key | `export GEMINI_API_KEY="..."` from Google AI Studio | Model control, usage-based billing |
| Vertex AI | `GOOGLE_GENAI_USE_VERTEXAI=true` with a key, or `gcloud auth application-default login` | Enterprise teams |

For Vertex AI you also set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`. Headless runs use an API key or Vertex AI. Put keys in your shell profile rather than in a repository, and treat them as credentials.

On limits, a paid API key's quota depends on your pricing tier, listed on the [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) page. Inside a session, `/stats model` shows token counts and quota information for the models you use.

## How it loads context

Gemini CLI builds its context from `GEMINI.md` files, the equivalent of `CLAUDE.md`. It concatenates every file it finds and sends them with each prompt, in three tiers. The global file is `~/.gemini/GEMINI.md`. Workspace files are found in your workspace directories and their parents. Just-in-time files are picked up when a tool touches a file or directory, scanning that directory and its ancestors up to a trusted root.

```markdown
# Project: my-api

- Use 2 spaces for indentation.
- Run `pnpm test` before finishing.

@./docs/style-guide.md
```

`@file.md` imports split a long file apart. `/init` generates a starting `GEMINI.md` from the current directory, `/memory show` prints the concatenated context the model receives, and `/memory list` lists the files in use. The footer shows how many context files loaded. If your repository already has an `AGENTS.md`, set `context.fileName` in `settings.json` to `["AGENTS.md", "GEMINI.md"]` so Gemini CLI reads it too. The same trade-offs about length apply as for Claude Code's [`CLAUDE.md`](/blog/claude-md-memory).

## settings.json, slash commands and MCP

Settings live in `~/.gemini/settings.json` for you and `.gemini/settings.json` inside a project. `/settings` edits them interactively. Useful slash commands from the command reference include `/auth`, `/model`, `/memory`, `/mcp`, `/stats`, `/permissions`, `/plan`, `/resume`, `/rewind`, `/skills` and `/hooks`.

MCP servers go under `mcpServers`, using Stdio, SSE or streamable HTTP transports:

```json
{
  "mcpServers": {
    "github": {
      "command": "path/to/server",
      "args": ["--arg1", "value1"],
      "env": { "API_KEY": "$MY_API_TOKEN" },
      "trust": false
    }
  }
}
```

`gemini mcp add <name> <commandOrUrl>` writes the entry for you, and `/mcp list` shows what connected. Leave `trust` at false, since true skips every tool confirmation for that server. The [MCP servers guide for Claude Code](/blog/claude-code-mcp-servers) covers the same idea from the other side.

## Sandboxing

Sandboxing isolates shell commands and file changes from the rest of your Mac. Turn it on with `gemini -s`, the `GEMINI_SANDBOX` environment variable (`true`, `docker`, `podman` or `sandbox-exec`) or `"tools": { "sandbox": "docker" }` in settings. On macOS the built-in method is Seatbelt through `sandbox-exec`, with a default `permissive-open` profile that confines writes to the project directory while allowing reads and network. Docker and Podman mount your working directory at the same absolute path inside the container.

## Compared with Claude Code and Codex

| | Gemini CLI | Claude Code | Codex CLI |
|---|---|---|---|
| Install | npm or Homebrew | native installer or Homebrew cask | install script, npm or Homebrew |
| Context file | `GEMINI.md` | `CLAUDE.md` | `AGENTS.md` |
| Settings | `~/.gemini/settings.json` | `~/.claude/settings.json` | `~/.codex/config.toml` |
| Sandbox and approvals | Seatbelt, Docker, Podman | `allow`, `ask`, `deny` rules | `sandbox_mode` |
| Consumer subscription sign-in | Ended June 18, 2026 | Pro, Max, Team, Enterprise | ChatGPT Plus and up |

Gemini CLI is open source under Apache 2.0, and it documents Seatbelt, Docker and Podman sandboxes. Its weakness today is direction: its own README says that for the best coding experience with Gemini models you should use Antigravity CLI. For setup steps on the others, see [install Claude Code on Mac](/blog/install-claude-code-mac), [Codex CLI setup](/blog/codex-cli-setup) and [Codex vs Claude Code](/blog/codex-vs-claude-code).

## Running it in Kaku

`kaku ai` opens the AI settings panel, which lists Gemini CLI next to Claude Code, Codex, Copilot CLI and Kimi Code. In Kaku 0.25.0 the panel reads `~/.gemini/settings.json` to show the selected model and the signed-in auth type, and changing the model there writes only the `model.name` field. Gemini CLI has no separate login command, so Kaku's re-sign-in action simply launches `gemini`. Kaku only edits a tool's settings when you change them in the panel. Splits (`Cmd + D`) put Gemini CLI beside a shell or another agent. Kaku's notification docs cover Claude Code and Codex; Gemini CLI is not listed there.

## FAQ

### Is Gemini CLI still free?

Not for individuals. Google's announcement ended free use through Gemini Code Assist for individuals on June 18, 2026, and the README note covers unpaid tier users too. Gemini CLI remains accessible with paid Gemini and Gemini Enterprise Agent Platform API keys.

### Do I need Node.js if I use Homebrew?

The docs list Node.js 20.0.0 or later as the runtime requirement. The Homebrew formula depends on `node` and installs it for you, so check `gemini --version` after installing.

### Where does Gemini CLI store its settings?

`~/.gemini/settings.json` for user settings and `.gemini/settings.json` in a project.

### Can it read my AGENTS.md?

Yes, by adding it to `context.fileName` in `settings.json`.

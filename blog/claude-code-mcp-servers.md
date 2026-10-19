# Claude Code MCP Servers: Add, Scope and Approve Them

> Add Claude Code MCP servers over HTTP or stdio, choose local, project, or user scope, and keep tokens out of a committed .mcp.json.

Published 2026-10-19 · Tw93 · https://kaku.fun/blog/claude-code-mcp-servers

Add a server with `claude mcp add`, then approve it before Claude calls its tools. A remote service is an HTTP URL. A program on your machine is a stdio command placed after `--`. Local and user servers stay in `~/.claude.json` on your machine, and a project `.mcp.json` is committed with the repo, so a token belongs in an environment variable rather than in that file.

The commands follow Claude Code's [MCP docs](https://code.claude.com/docs/en/mcp), checked in October 2026. [MCP](https://modelcontextprotocol.io/) is the open protocol those servers speak.

## How Claude Code talks to a server

Claude Code is the MCP host. It opens one client per server, and that client keeps the connection. The messages are JSON-RPC. After it connects, Claude Code asks what the server offers, including `tools/list`, `prompts/list` and `resources/list`. Tools are functions Claude can call, resources are data you attach with `@`, and prompts show up as `/servername:promptname (MCP)`.

Stdio starts a process on your machine and uses its standard input and output. Claude Code sets `CLAUDE_PROJECT_DIR` in that process to the project root. HTTP is the transport the docs recommend for a remote service. In JSON, `streamable-http` is an alias for `http`. An entry with a `url` and no `type` is read as stdio and skipped.

![Claude Code opens one MCP client per server, and that client talks to a local process over stdin and stdout or to a remote server over HTTP, both of which answer tools/list](https://kaku.fun/img/blog/claude-code-mcp-servers.webp)

*Each server gets its own client, which uses stdio or HTTP to fetch the tool list.*

## Add an HTTP server and a stdio server

[GitHub's remote MCP server](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server) is `https://api.githubcopilot.com/mcp/`. Claude Code's example passes a personal access token as a header. The command stores the entry and does not check the token, so a placeholder is accepted and fails later:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

`Added` means the entry was written. `/mcp` shows whether it connected, and a bad token fails with a status such as 401. Keep this header on a local or user server. A committed file should use `${GITHUB_PAT}`.

Sentry is the docs' no-header example. Sign in from `/mcp`, or with `claude mcp login sentry`, before a `claude -p` run. The same name at the same scope fails with `MCP server sentry already exists in local config`.

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

The docs' Airtable example is stdio. Keep another option between `--env` and the name, and put the process after `--`:

```bash
claude mcp add --env AIRTABLE_API_KEY=YOUR_KEY --transport stdio airtable \
  -- npx -y airtable-mcp-server
```

Without `--`, a flag such as `--port` is parsed as a Claude Code option. Names can contain only letters, numbers, hyphens and underscores.

## Local, project and user scope

Leave `--scope` off and the server is local. Local is not `.claude/settings.local.json`. It is an entry under one project path in `~/.claude.json`, so another checkout does not see it.

| Scope | Loads in | Shared | Stored in |
|---|---|---|---|
| `local` (default) | This project, for you | No | `~/.claude.json`, under that project's path |
| `project` | This project | Yes, if you commit it | `.mcp.json` in the project root |
| `user` | All your projects | No | `~/.claude.json` |

`--scope user` or `--scope project` picks the scope, as in `claude mcp add --transport http sentry --scope user https://mcp.sentry.dev/mcp`. A server defined in more than one place connects once, using the whole entry from the highest source: local, then project, then user, then a plugin, then a claude.ai connector. Scopes are matched by name, plugins and connectors by URL or command. `managedMcpServers` ranks above that list on Claude Code v2.1.259 or later. The desktop app's Code tab loads the user stdio entry when `.mcp.json` uses the same name.

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    }
  }
}
```

`${VAR}` and `${VAR:-default}` expand in `command`, `args`, `env`, `url` and `headers`. With no default, the server still loads and the literal `${VAR}` text is sent. `claude mcp list` names the missing variable and shows the name, not the secret. `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK`, `HTTPS_PROXY` and `NPM_TOKEN` are blanked in a remote URL or header, default included, which usually returns 401. Copy the value into a name of your own.

## List, approve and remove

```bash
claude mcp list
claude mcp get github
claude mcp remove github
```

`Failed to connect` means that server did not connect, while the list command itself succeeds. `claude mcp get` repeats the text on an `Issue:` line, with secrets and the expanded URL removed. `Connection error` prints no detail. `Needs authentication` still needs a login.

A `.mcp.json` server stays at `Pending approval` until you run `claude` and accept it. `claude mcp reset-project-choices` clears those answers. `claude -p`, the Agent SDK and cloud sessions load project servers with no prompt unless you block them. A committed `enableAllProjectMcpServers` or `enabledMcpjsonServers` is ignored until the workspace is trusted. `disabledMcpjsonServers` blocks a project server in every mode. Turning one off in `/mcp` writes `disabledMcpServers` instead, keeps the config, and stops the connection.

Removing a remote server also deletes the OAuth tokens and client registration stored for it. When one name points at different endpoints in two scopes, pass `--scope` so the other entry stays.

## When a tool call needs approval

Approving the server does not approve its tools. Manual mode, the default, prompts the first time each tool is used. The name is `mcp__<server>__<tool>`, and a dot or space in the server name becomes `_`, so `list_issues` on `github` is `mcp__github__list_issues`. `mcp__github` and `mcp__github__*` match every tool from that server. An allow rule may use `*` only after `mcp__<server>__`. `mcp__*` as an allow rule is skipped. As a deny rule it removes every MCP tool from context. Deny is checked before ask, and ask before allow.

```json
{
  "permissions": {
    "allow": ["mcp__github__*"]
  }
}
```

User rules go in `~/.claude/settings.json`. Project rules go in `.claude/settings.json`. `/permissions` shows which file each rule came from. `acceptEdits` covers file edits and common filesystem commands, and does not auto-approve MCP tools. `bypassPermissions` skips ordinary MCP prompts along with most other prompts. A tool whose `tools/list` entry sets `_meta["anthropic/requiresUserInteraction"]` to `true` still asks every time, with no "don't ask again", including in `bypassPermissions`.

A [subagent](/blog/claude-code-subagents) `tools` field, a [skill](/blog/claude-code-skills) `allowed-tools` list and a [hook](/blog/claude-code-hooks) matcher need that full name.

## When a server will not start

A 401 on a header you wrote does not fall through to OAuth. Fix the header. For Sentry, finish login with `/mcp` or `claude mcp login sentry`.

If a stdio process exits immediately, run the command after `--` in a shell. Claude Code does not reconnect stdio. A dropped remote server is retried, and an authentication failure is not. `/mcp reconnect all` retries failed rows on Claude Code v2.1.284 or later.

`MCP_TIMEOUT=10000 claude` allows 10 seconds to start. A server `"timeout"`, in milliseconds, limits each tool call, and a value below 1000 is ignored. `claude mcp add` rejects the reserved names `workspace`, `claude-in-chrome`, `computer-use`, `Claude Preview` and `Claude Browser`.

## What a long tool list costs

Tool search is on by default for current Claude models. The session starts with names and server instructions, and loads a definition when Claude searches. There is no per-server cap. `ENABLE_TOOL_SEARCH=false`, an `ANTHROPIC_BASE_URL` that points to a non-Anthropic host, and models earlier than Opus 4 and Sonnet 4 load every definition up front. `"alwaysLoad": true` does that for one server.

Claude Code warns above 10,000 tokens. Past the default cap of 25,000, the text is saved under `tool-results` in `~/.claude/projects/`, and the conversation keeps that path. `MAX_MCP_OUTPUT_TOKENS` raises the cap.

## In a Kaku tab

Kaku 0.25.0 does not add MCP servers. `kaku ai` edits Claude Code's Model in `~/.claude/settings.json` as `model`. Base URL and API Key appear only when that file already has `env.ANTHROPIC_BASE_URL` or a token, and save as `env.ANTHROPIC_BASE_URL` and `env.ANTHROPIC_AUTH_TOKEN`. Auth is shown and not edited. The panel does not touch `~/.claude.json` or `.mcp.json`, and it does not add hooks or instructions on its own. [AI coding in Kaku](/docs/ai-coding) describes the panel.

`ANTHROPIC_AUTH_TOKEN` will not expand in a remote header, so copy that key into another variable before `.mcp.json` references it. claude.ai connectors load only for a subscription login, not when `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or `apiKeyHelper` is the active credential. `/status` shows which one is active.

`Cmd + T` opens a tab, `Cmd + D` or `Cmd + Shift + D` puts a shell beside it, and `Cmd + Shift + Enter` zooms the pane. Closing asks first. Ending the session signals a stdio server with `SIGINT`, `SIGTERM` 100 milliseconds later, then `SIGKILL` after another 400. `Cmd + Click` opens file paths Claude Code prints. Claude Code 2.1.295 or later reports working, waiting and done to Kaku 0.25.0 with no extra setting. Leave `preferredNotifChannel` at `auto`.

## When a server is the wrong tool

Claude Code can already read the repo, edit files and run a shell, so a filesystem server pointed at the same checkout mostly adds another process. A reused checklist is a [skill](/blog/claude-code-skills). A command that must be blocked is a [hook](/blog/claude-code-hooks). MCP is the connection to some other system, such as GitHub or Sentry. Instructions from another client are still a URL, a command after `--`, or one `mcpServers` entry passed to `claude mcp add-json`.

## FAQ

### Can I import servers from Claude Desktop?

On macOS and WSL, `claude mcp add-from-claude-desktop` reads that config and lets you pick. A name that is not just letters, numbers, hyphens and underscores is skipped. A duplicate is saved as `server_1` or a similar suffix.

### Why does /mcp list a tool Claude never calls?

A full name longer than 128 characters is left out of the request. The API would reject the whole request if that tool were included. `/mcp` shows the full name when you select the tool.

### Can a server stop and ask me for input?

Elicitation opens a dialog on its own. Form mode shows the server's fields. URL mode asks whether to open a browser.

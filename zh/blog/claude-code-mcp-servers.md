# 配置 Claude Code 的 MCP 服务器

> 用 claude mcp add 接 HTTP 或 stdio，分清 local、project、user，密钥放环境变量。

发布于 2026-10-19 · Tw93 · https://kaku.fun/zh/blog/claude-code-mcp-servers

用 `claude mcp add` 把服务器加进来，在 Claude 调用它的工具之前先批准。远程服务填一个 HTTP 地址，本机程序是放在 `--` 后面的 stdio 命令。local 和 user 写在这台机器的 `~/.claude.json` 里，项目用的 `.mcp.json` 会跟着仓库提交，token 放在环境变量里，不要写进那个文件。

下面的命令以 Claude Code 的 [MCP 文档](https://code.claude.com/docs/en/mcp) 为准，2026 年 10 月核对过。[MCP](https://modelcontextprotocol.io/) 是这些服务器使用的开放协议。

## 服务器是怎么连上的

Claude Code 在这条链路里是 MCP 的 host，它给每个服务器单独开一个 client，连接由这个 client 维持，两边交换 JSON-RPC。连上之后 Claude Code 会问服务器提供什么，其中包括 `tools/list`、`prompts/list` 和 `resources/list`。工具是 Claude 可以调用的函数，资源是你用 `@` 附上去的数据，提示词出现在 `/` 菜单里，形式是 `/servername:promptname (MCP)`。

stdio 在本机起一个进程，走这个进程的标准输入和标准输出，Claude Code 会把 `CLAUDE_PROJECT_DIR` 设成项目根目录。远程服务在文档里推荐走 HTTP，JSON 里的 `streamable-http` 是 `http` 的别名，只有 `url`、没有 `type` 的条目会被当成 stdio，然后跳过。

![Claude Code 为每个服务器开一个 MCP 客户端，客户端通过 stdin 和 stdout 连本地进程，或者通过 HTTP 连远程服务器，两者都回答 tools/list](https://kaku.fun/img/blog/claude-code-mcp-servers.webp)

*每个服务器单独配一个客户端，客户端用 stdio 或 HTTP 去取工具列表。*

## 添加 HTTP 和 stdio

[GitHub 的远程 MCP 服务器](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server) 地址是 `https://api.githubcopilot.com/mcp/`。Claude Code 文档里的例子用 header 传个人访问令牌，这条命令只把配置写进去，不检查令牌，占位符也能保存，真正连的时候才会失败。

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

成功时打印的一行以 `Added` 开头。进会话后看 `/mcp` 是否连上，令牌不对会失败，状态里带 HTTP 状态码，比如 401。这个 header 存在保存下来的条目里，适合 local 或 user，要提交的文件改用 `${GITHUB_PAT}`。

Sentry 是文档里不带 header 的例子。在 `claude -p` 之前先登录，可以在 `/mcp` 里走浏览器，也可以在 shell 里跑 `claude mcp login sentry`。同一个范围里再加同名服务器，会报 `MCP server sentry already exists in local config`。

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

文档里的 Airtable 例子是 stdio。`--env` 和服务器名之间要再放一个选项，进程本身连同它自己的参数放在 `--` 后面。

```bash
claude mcp add --env AIRTABLE_API_KEY=YOUR_KEY --transport stdio airtable \
  -- npx -y airtable-mcp-server
```

少了 `--`，`--port` 这种参数会被 Claude Code 当成自己的选项。名字只能包含字母、数字、连字符和下划线。

## local、project 和 user

不写 `--scope` 就是 local。它按项目路径记在 `~/.claude.json` 里，换一个检出就看不到，和项目目录里的 `.claude/settings.local.json` 各管各的。

| 范围 | 在哪加载 | 共享 | 存在哪 |
|---|---|---|---|
| `local`（默认） | 只在这个项目，只对你 | 不共享 | `~/.claude.json`，挂在该项目路径下 |
| `project` | 这个项目 | 提交后共享 | 项目根目录的 `.mcp.json` |
| `user` | 你的全部项目 | 不共享 | `~/.claude.json` |

`--scope user` 或 `--scope project` 指定范围，比如 `claude mcp add --transport http sentry --scope user https://mcp.sentry.dev/mcp`。同一台服务器在几处都定义了，只连一次，用优先级最高的那一整条配置，不把几个范围的字段拼在一起，顺序是 local，然后 project，然后 user，然后插件，然后 claude.ai 的 connector。三个范围之间按名字判重，插件和 connector 按 URL 或命令判重。Claude Code v2.1.259 及以后，组织下发的 `managedMcpServers` 排在这张名单之上。桌面应用的 Code 标签里，同名的 stdio 如果 user 和 `.mcp.json` 都有，加载的是 user 那条。

提交进仓库的 GitHub 服务器把令牌留在环境变量里。

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

`${VAR}` 和 `${VAR:-default}` 可以写在 `command`、`args`、`env`、`url` 和 `headers` 里。没有默认值时服务器照样加载，发出去的是字面量 `${VAR}`，`claude mcp list` 会点出变量名，列表和 `/mcp` 显示这个名字，不显示解开之后的密钥。`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK`、`HTTPS_PROXY` 和 `NPM_TOKEN` 写进远程 URL 或 header 时会被当成空。连 `:-default` 也不生效，对方多半回 401。要给服务器用，先抄到一个你自己起的变量名里。

## 查看、批准和删除

```bash
claude mcp list
claude mcp get github
claude mcp remove github
```

`Failed to connect` 表示那一台服务器没有连上，list 命令自己是成功的。`claude mcp get` 把同一段说明打在 `Issue:` 那一行，密钥和展开后的 URL 不会出现。`Connection error` 不附细节，因为异常文本里可能带着 URL。`Needs authentication` 还差登录。

`.mcp.json` 里的服务器会停在 `Pending approval`，直到你在这个目录里跑 `claude` 并接受它。`claude mcp reset-project-choices` 清掉这些选择。`claude -p`、Agent SDK 和云端会话没有这道提示，项目服务器会直接加载，除非你另行拦住。提交在仓库里的 `enableAllProjectMcpServers` 或 `enabledMcpjsonServers` 在工作区被信任之前不起作用。`disabledMcpjsonServers` 在任何权限模式下都拒绝这台项目服务器。在 `/mcp` 里把一台关掉，写的是另一份名单 `disabledMcpServers`，配置还在，只是不再连接。

删掉一台远程服务器时，Claude Code 也会删掉为它存的 OAuth 令牌和客户端注册。同一个名字在两个范围里指向不同地址时，给 `claude mcp remove` 加上 `--scope`，另一条才会留下来。

## 工具调用还要再批一次

批准服务器和批准它的工具是两件事。默认的 Manual 模式会在每个工具第一次使用时提问。工具全名是 `mcp__<server>__<tool>`，服务器名里的点和空格会变成 `_`，注册成 `github` 的 `list_issues` 就是 `mcp__github__list_issues`。`mcp__github` 和 `mcp__github__*` 都匹配这台服务器的全部工具。allow 规则里的 `*` 只能出现在 `mcp__<server>__` 后面，写成 `mcp__*` 的 allow 会被跳过，什么都不批准。同样的 `mcp__*` 作为 deny，会把所有 MCP 工具从 Claude 能看到的上下文里拿掉。先看 deny，再看 ask，最后才是 allow。

```json
{
  "permissions": {
    "allow": ["mcp__github__*"]
  }
}
```

每台机器都用的规则放在 `~/.claude/settings.json`，只给这个项目的放在 `.claude/settings.json`。`/permissions` 会标出每条规则来自哪个文件。`acceptEdits` 自动放行的是文件修改和常见的文件系统命令，不包括 MCP 工具。`bypassPermissions` 会跳过普通的 MCP 提问，同时也会跳过大多数别的提问。工具在 `tools/list` 里把 `_meta["anthropic/requiresUserInteraction"]` 设为 `true` 时，每次调用仍要提问，没有不再询问这一项。`bypassPermissions` 里也一样。

[subagent](/zh/blog/claude-code-subagents) 的 `tools`、[skill](/zh/blog/claude-code-skills) 的 `allowed-tools` 和 [hook](/zh/blog/claude-code-hooks) 的 matcher 都要写这个全名。

## 服务器起不来的时候

你自己写的 header 返回 401 时，不会改走 OAuth，改 header。Sentry 则是登录没做完，用 `/mcp` 或 `claude mcp login sentry`。

stdio 进程马上退出的话，把 `--` 后面的命令拿到普通 shell 里跑一遍，看它自己的报错。Claude Code 不会自动重连 stdio。远程服务器掉线会重试，认证失败不会。`/mcp reconnect all` 在 Claude Code v2.1.284 及以后会重试失败的那些行。

`MCP_TIMEOUT=10000 claude` 给启动留 10 秒。服务器上的 `"timeout"` 以毫秒计，限制的是每一次工具调用，小于 1000 的值会被忽略。`claude mcp add` 拒绝这些保留名，`workspace`、`claude-in-chrome`、`computer-use`、`Claude Preview` 和 `Claude Browser`。

## 工具一多，上下文怎么算

当前的 Claude 模型默认开着 tool search。会话开始时先加载工具名和服务器说明，Claude 去搜的时候才加载完整定义，没有按服务器计算的工具数量上限。`ENABLE_TOOL_SEARCH=false`、指向非 Anthropic 主机的 `ANTHROPIC_BASE_URL`，以及早于 Opus 4 和 Sonnet 4 的模型，会一开始就把全部定义放进提示词。`"alwaysLoad": true` 让某一台服务器也这样加载。

单次结果超过 10000 token 会警告，默认上限是 25000 token，超过之后写到 `~/.claude/projects/` 下的 `tool-results`，对话里留下文件路径。`MAX_MCP_OUTPUT_TOKENS` 提高的是这个上限，警告线不动。

## 在 Kaku 里跑

Kaku 0.25.0 不会替你添加 MCP 服务器。`kaku ai` 改的是 `~/.claude/settings.json` 里 Claude Code 的 Model，写成 `model`。Base URL 和 API Key 只有在文件里已经有 `env.ANTHROPIC_BASE_URL` 或令牌时才出现，保存为 `env.ANTHROPIC_BASE_URL` 和 `env.ANTHROPIC_AUTH_TOKEN`。Auth 只显示、不能在这里改。这个面板不碰 `~/.claude.json` 和 `.mcp.json`，也不会自己往 agent 里加 hook 或指令。面板做什么写在 [Kaku 里的 AI 编程](/zh/docs/ai-coding)。

`ANTHROPIC_AUTH_TOKEN` 不会被展开进远程 MCP 的 header，从 `kaku ai` 存下来的密钥要先抄到别的变量名，`.mcp.json` 才能引用。claude.ai 的 connector 只在订阅登录下加载，`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN` 或 `apiKeyHelper` 是当前凭证时不会去拉。`/status` 能看到现在用的是哪一种。

`Cmd + T` 开一个标签，`Cmd + D` 或 `Cmd + Shift + D` 在旁边放一个 shell，`Cmd + Shift + Enter` 放大当前窗格。关掉窗格之前会先问一句。会话结束时，stdio 服务器会收到 `SIGINT`，100 毫秒后如果还在就收到 `SIGTERM`，再过 400 毫秒是 `SIGKILL`。Claude Code 打印出来的文件路径可以用 `Cmd + Click` 打开。Claude Code 2.1.295 及以后会把正在干活、正在等你、已经做完报告给 Kaku 0.25.0，不用额外设置，`preferredNotifChannel` 保持 `auto`。

## 什么时候不必接一台服务器

Claude Code 自己就能读仓库、改文件、跑 shell，再把一个文件系统服务器指到同一份检出，多出来的主要是一个进程。[skill](/zh/blog/claude-code-skills) 适合一份要反复用的检查清单，必须拦住某条命令时用 [hook](/zh/blog/claude-code-hooks)。MCP 管的是连到别的系统，比如 GitHub 或 Sentry。别的客户端写的安装说明，落到 Claude Code 上仍是三种样子，一个 URL，一条放在 `--` 后面的启动命令，或者去掉外层包装之后交给 `claude mcp add-json` 的一条 `mcpServers` 配置。

## 常见问题

### 能把 Claude Desktop 里的服务器导入过来吗？

在 macOS 和 WSL 上，`claude mcp add-from-claude-desktop` 会读那份配置并让你挑选。名字里只要出现字母、数字、连字符、下划线以外的字符就会被跳过。重名的会存成 `server_1` 这样的后缀。

### /mcp 里列着，Claude 却调不到，是什么原因？

全名超过 128 个字符的工具不会放进请求，放进去的话 API 会把整次请求拒绝掉。在 `/mcp` 里选中这个工具可以看到全名。

### 服务器会中途停下来问我填表吗？

会。elicitation 自己弹出对话框，不用额外配置。Form 模式是服务器定义的字段，URL 模式会问要不要打开浏览器。

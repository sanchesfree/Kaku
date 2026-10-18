Codex CLI 和 Claude Code 都是跑在终端里的 coding agent，都会读仓库、改文件、在你的机器上跑命令，区别在账号和价格，在沙箱和授权提示怎么工作，也在配置文件上，Codex 用 TOML，Claude Code 用 JSON。两边都有 skills、hooks 和 MCP，很多人干脆两个都装着。

## 对比

2026 年 10 月核对过，对照的是 [Codex CLI](https://developers.openai.com/codex/cli) 页面、[配置参考](https://developers.openai.com/codex/config-reference)、[Codex 价格页](https://developers.openai.com/codex/pricing)，以及 Claude Code 的[概述](https://code.claude.com/docs/en/overview)、[设置](https://code.claude.com/docs/en/settings)和 [hooks 指南](https://code.claude.com/docs/en/hooks)。

| | Codex CLI | Claude Code |
|---|---|---|
| 安装 | macOS/Linux 用 `curl -fsSL https://chatgpt.com/codex/install.sh \| sh`，页面上还有 Windows、npm 和 Homebrew 几个标签 | `curl -fsSL https://claude.ai/install.sh \| bash`，或者 `brew install --cask claude-code` |
| 登录 | 跑 `codex`，再选 Sign in with ChatGPT 或别的方式 | `claude` 会让你登录，有一个已批准的 `ANTHROPIC_API_KEY` 就跳过这一步 |
| 配置文件 | `~/.codex/config.toml`，受信任的项目里还有 `.codex/config.toml` | `~/.claude/settings.json`、`.claude/settings.json`、`.claude/settings.local.json` |
| 沙箱和授权 | `sandbox_mode` 有 `read-only`、`workspace-write`、`danger-full-access`，`approval_policy` 是 `on-request` 或 `never`，`/permissions` 显示当前沙箱 | `allow`、`ask`、`deny`，用 `Shift + Tab`、`/plan` 或 `--permission-mode plan` 进 plan mode，`auto` 和 `bypassPermissions` 来自用户设置或托管设置，或者 `--permission-mode` |
| 模型 | `model`，比如 `gpt-6.1-sol`，`/model` 设置模型和推理强度 | `/model` 在会话中途切换，`--model` 只管这一次会话，设置页上的例子是 `claude-sonnet-5`、`claude-opus-5-5` |
| MCP | `codex mcp` | 服务器存在 `~/.claude.json` |
| Hooks | `hooks.json` 或 `[hooks]`，要打开 `features.hooks` | 设置文件里的 `hooks`，`/hooks` 列出来 |
| 通知 | `tui.notification_method` 可以是 `auto`（默认）、`osc9`、`bel`，触发条件默认是 `unfocused` | `~/.claude/settings.json` 里的 `preferredNotifChannel`，或者一个 `Notification` hook |
| 接着上次 | `codex resume` | `claude --continue` 或 `claude --resume`，`claude --teleport` 把网页或手机上的任务拉进终端（需要 claude.ai 订阅） |

原生安装的 Claude Code 会自己更新，Homebrew 装的不会，`claude-code` 是稳定版 cask，大概落后一周，`claude-code@latest` 才是最新的。`claude` 进了 `PATH` 之后，`claude --version` 会打印版本号，设置文件是严格的 JSON。

项目里的 `.codex/config.toml` 只有在你信任这个项目之后才加载，而且它设不了通知，所以 `notification_method` 只能留在 `~/.codex/config.toml`。`approval_policy = "untrusted"` 不支持，`on-failure` 已经废弃，文档还说不要把权限 profile（`:read-only`、`:workspace`、`:danger-full-access`）和 `sandbox_mode` 混在一起用。

```toml
model = "gpt-6.1-sol"
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

Claude Code 放行 lint 和测试、同时挡住 `.env` 的例子，写在 `~/.claude/settings.json` 里：

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

`/status` 能确认加载了什么，`.claude/settings.json` 提交进仓库给整个团队用，个人的覆盖放在 `.claude/settings.local.json`，这几个文件里的 `permissions.allow` 会合并。`ANTHROPIC_MODEL` 覆盖 `model`，`--model` 在这一次会话里又同时覆盖这两者。

## 账号和价格

按 OpenAI 的[价格页](https://developers.openai.com/codex/pricing)，每个 ChatGPT 方案都包含 Codex，不过 Free 和 Go 只列了桌面 App，CLI、IDE 扩展和网页从 Plus 起才有，用 OpenAI 的 API key 也行，按 API 价格计费，不含 GitHub 代码审查和 Slack 这类云端功能。

Plus 和 Pro 用完包含的额度还可以再买，额度用完时正在跑的那一轮允许跑完，前提是用量合理，各档价格和每个模型的用量上限都在[价格页](https://developers.openai.com/codex/pricing)上。

Claude Code 用的是 [Claude 订阅](https://claude.com/pricing)（Pro、Max、Team 或 Enterprise），或者按用量计费的 [Anthropic Console](https://platform.claude.com/) 账号。终端、VS Code 和 JetBrains 也支持第三方提供方，桌面 App 要付费订阅，更多在 [code.claude.com](https://code.claude.com/)。

## 各自适合干什么

`codex exec` 是给脚本和 CI 用的非交互命令，`/review` 检查未提交的改动、某一次提交或者一个基准分支，不动工作区。`/init` 会写出 `AGENTS.md`，skills 存可以重复用的指令，plugins 接外部工具。

Claude Code 这些事都从 `claude` 这一条命令进去，`claude -p` 接一次性的提示词，也接管道：

```bash
git diff main --name-only | claude -p "review these changed files for security issues"
```

项目根目录的 [`CLAUDE.md`](https://code.claude.com/docs/en/memory) 每次会话开始都会读，skills 是 `/review-pr` 这类大家共用的命令。返回 deny 的 `PreToolUse` hook 在 `bypassPermissions` 模式下、加了 `--dangerously-skip-permissions` 时照样能挡住工具。Claude Code 还会跑 prompt hook 和 agent hook，Codex 跑的是 command hook 和 MCP tool hook，prompt 和 agent 这两类处理器解析完就跳过不跑。

[plan mode](/zh/blog/claude-code-plan-mode) 让 Claude Code 在你批准之前不改文件，[hook](/zh/blog/claude-code-hooks) 在任何模式下都能挡住一次工具调用。

## 一个仓库，两个 agent

共用的指令可以放在 `AGENTS.md`，Codex 用 `/init` 生成它，仓库里已经有这份文件的话，Claude Code 可以拿它代替 `CLAUDE.md`，你自己加的 `CLAUDE.md` 在 Claude Code 会话开始时照样会加载。`model_instructions_file` 替换的是 Codex 的内置指令，不是 `AGENTS.md`。

两个都可以改同一份检出，Claude Code 在 `--worktree`、`isolation: "worktree"` 和后台会话（`WorktreeCreate`）这几种情况下会开一个 git worktree。清理写在 [git worktrees](/zh/blog/claude-code-git-worktrees) 那篇，Codex CLI 没有对应的参数。安装可以看 [Codex CLI 配置](/zh/blog/codex-cli-setup)和[安装 Claude Code](/zh/blog/install-claude-code-mac)。

## 在 Kaku 里并排

[Kaku](https://kaku.fun/zh/docs/ai-coding) 把这两个 CLI 当普通程序来跑，`kaku ai` 能配置 Claude Code、Codex 和其他外部工具，显示套餐用量，只在你在那里改了某项设置时才写这一项，不会自己去加 hooks 或指令。

`Cmd + D` 左右分屏，`Cmd + Shift + D` 上下分屏，`Cmd + Shift + Enter` 把你正在看的窗格放大。前台正跑着 Claude Code、Codex 或其他要跑很久的程序时，关窗格或标签会先问一声。重启之后，这些窗格留着最后一屏。

Codex 在 Kaku 里不用设通知，它会响终端铃声，Kaku 在后台时会把铃声变成一条通知。想看到 Codex 自己写的文字，就在 `~/.codex/config.toml` 里设好方式：

```toml
[tui]
notification_method = "osc9"
```

`auto` 是默认值，`osc9` 带一行文字，`bel` 就是铃声，`tui.notification_condition` 是 `unfocused`，除非你设成 `always`。

Kaku 0.25.0 及以上配 Claude Code 2.1.295 及以上不用任何设置，更早的版本要在 `~/.claude/settings.json` 里设 `"preferredNotifChannel": "ghostty"`，原因写在 [Claude Code 通知](/zh/blog/claude-code-notifications)那篇。还是什么都没有的话，点 Kaku > Notification Settings，在系统设置里打开允许通知。

## 常见问题

### 能不能在一个仓库里同时跑两个？

能，共用的指令放进 `AGENTS.md`，Codex 用 `/init` 写出它，Claude Code 可以拿它代替 `CLAUDE.md`。两个不该改同一批文件时，Claude Code 会话用 `--worktree` 启动，在 Kaku 里 `Cmd + D` 就能把两个 CLI 放进相邻的窗格。

### 哪个更便宜？

每个 ChatGPT 方案都包含 Codex，但 Free 和 Go 只列了桌面 App，CLI 从每月 $20 的 Plus 起才有，用 OpenAI 的 API key 也行，Claude Code 要 Pro、Max、Team 或 Enterprise 订阅，或者一个 Console 账号，具体以 [Codex 价格页](https://developers.openai.com/codex/pricing)和 [claude.com/pricing](https://claude.com/pricing) 上的为准，用之前再看一眼。

### 为什么只有一个会提醒我？

在 Kaku 里窗口处于后台时，Codex 的铃声本来就会变成通知。Kaku 0.25.0 及以上配 Claude Code 2.1.295 及以上不用任何设置，更早的版本要设 `"preferredNotifChannel": "ghostty"`，原因写在 [Claude Code 通知](/zh/blog/claude-code-notifications)那篇，Kaku 还要打开允许通知。

### 两个都有 hooks 和 MCP 吗？

都有，Codex 用 `features.hooks` 配 `hooks.json` 或 `[hooks]`，服务器用 `codex mcp` 管。Claude Code 用 `settings.json` 里的 `hooks` 对象，MCP 服务器存在 `~/.claude.json`，两边共有的事件名包括 `PreToolUse`、`PostToolUse`、`SessionStart` 和 `Stop`。

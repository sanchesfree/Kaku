Cursor 是一个编辑器，coding agent 装在里面，Claude Code 是一个 agent，终端和 IDE 扩展里都能跑，它读仓库、改文件、跑命令，改出来的还是普通项目文件，Cursor 或其他编辑器都能打开。怎么选，看你想在哪读 diff，也看你想同时跑几个会话。

## 各自怎么工作

[Cursor](https://cursor.com/docs) 的文档把它写成 AI 编辑器，也写成 coding agent，你用它看懂一个仓库，用 Plan Mode 规划功能、把功能做出来，修 bug，合并前看 diff、跑检查，插件、skills、MCP 和 rules 都从同一个地方加。

[Claude Code](https://code.claude.com/docs/en/overview) 跑在终端、IDE 扩展、桌面 App 和浏览器里，这几处共用一个引擎，所以项目里的 `CLAUDE.md`、设置和 MCP 服务器在每一处都生效。到项目目录里这样启动。

```bash
cd your-project
claude
```

它改文件、跑命令，也用 git 做暂存、写提交说明、开分支、提 pull request。项目根目录的 `CLAUDE.md` 每次会话开始都会读，已经有 `AGENTS.md` 的话，就用那份代替。

## 钱花在哪

[Cursor 的价格页](https://cursor.com/pricing) 列了 Free、Plus、Premium、Super 和 Ultra，另外还有 Teams 和 Enterprise，价目以这一页上的数字为准，2026 年 10 月核对过。Cursor 的用量和 Grok 那边的 Chat、Imagine、Voice、Bot 放在同一个池子里，每周刷新，更高的档位池子更大，包含的额度用完还可以再买一笔。Free 的 agent 请求有限，聊天请求也有限，Plus 只含 Grok 模型。Premium 及以上含 Grok 的用量，第三方模型按 API 标价另计，不在这份包含的额度里，并且有花费上限。Cloud agents 和 Bugbot 的代码审查从 Premium 起才有，agent 每个方案都有，Free 也有。

Claude Code 用的是 [Claude 订阅](https://claude.com/pricing)（Pro、Max、Team 或 Enterprise），或者按用量计费的 [Anthropic Console](https://platform.claude.com/) 账号，Amazon Bedrock、Google Cloud 的 Agent Platform 和 Microsoft Foundry 上也能用。登录怎么做写在[在 Mac 上安装 Claude Code](/zh/blog/install-claude-code-mac) 那篇。claude.ai 的方案里，`/usage` 显示当前会话和这一周，用 API key 或第三方登录时，显示的是这一次会话的费用和 token，更多价格在 [code.claude.com](https://code.claude.com)。

## 上下文和模型

Cursor 给每个模型标了默认上下文，很多还有更高的上限，这张表会随着新模型上线一直变，具体数字以[模型页面](https://cursor.com/docs)上的为准。

文档里没写固定的上下文窗口大小，扩展里能看到窗口填了多少，Claude 需要时会自己压缩，想现在就压就跑 `/compact`。`@` 引用目录时只放进文件列表，不放内容。点一下模型名字就能换，Claude Code v2.1.284 及以后，只打 `/model` 也会弹出模型列表。

## 并行和长会话

git worktree 会在另一个目录里把仓库再检出一份，用的是另一条分支，所以 `claude --worktree feature-auth` 能让两个 Claude Code 任务不改同一批文件，再开一个终端就换一个名字，怎么设置、会报哪些错写在 [worktree 那篇](/zh/blog/claude-code-git-worktrees)。

**Open in New Tab**（Mac 上是 `Cmd + Shift + Esc`）或 **Open in New Window** 开的是另一段对话，历史和上下文各自一份。

```bash
claude --continue
claude --resume
```

`--continue` 重新打开这个目录里最新的一次会话，没有的话就打印 `No conversation found to continue` 然后退出。`--resume`，或者会话里的 `/resume`，让你自己挑。

在 [claude.ai/code](https://claude.ai/code) 上可以在浏览器里跑耗时长的任务，一次可以开好几个，你本地没有的仓库也包括在内。桌面 App 把会话并排显示，需要付费订阅。Routines 在云上跑，电脑关着也行，在网页上建，在桌面 App 里建，或者用 `/schedule`。

## 改动怎么审

Cursor 审改动留在编辑器里，你在里面看 diff、跑检查，合并前把问题看出来。

Claude Code 的 [plan mode](/zh/blog/claude-code-plan-mode) 只读仓库，你批准之前什么都不写，用 `Shift + Tab`、`/plan` 或 `--permission-mode plan` 都能进去。

扩展里有几种权限模式，Edit 直接写文件，不再问你，Auto 先让一个分类器把大部分动作过一遍，Manual 停在并排的 diff 上，等你接受、拒绝，或者改了再用。**Accept this change** 和 **Reject this change** 按 hunk 一步步过，从 Claude Code v2.1.275 起才有，改动超过 100 处的 diff 打开时没有这两个按钮。

`claude "commit my changes with a descriptive message"` 会做这次提交，之后用 `git diff` 看，也可以在 [lazygit](/zh/blog/lazygit-and-delta) 里看。扩展里从一条消息出发，可以把对话分叉出去，把文件倒回去，也可以两样一起做。

## 在 Cursor 里用 Claude Code

[概述](https://code.claude.com/docs/en/overview)里，Cursor 用 `cursor:extension/anthropic.claude-code` 装扩展，VS Code 用 `vscode:extension/anthropic.claude-code`，装好之后，**Open in New Tab** 在 Command Palette（`Cmd + Shift + P`）里。具体写在 [IDE 集成](https://code.claude.com/docs/en/ide-integrations)，终端里的步骤来自 [VS Code 指南](https://code.claude.com/docs/en/vs-code)。

用 Command 和反引号打开集成终端，然后跑 `claude`，这样 CLI 会把 diff 和诊断放到这个编辑器里显示。扩展不会把 `claude` 放进 `PATH`，所以终端里要另有一份独立的 CLI，`/ide` 把外面的终端接到 VS Code。`claude --resume` 接着面板里的那段聊天。这段要是还在别处开着，面板会说两份可能会把消息混在一起，关掉另一份，或者选 **Open here anyway**。

## 在 Kaku 里并排

在 [Kaku](https://kaku.fun/zh/docs/ai-coding) 里，`Cmd + D` 左右分屏，`Cmd + Shift + D` 上下分屏，Claude Code 可以挨着一个 shell，也可以挨着 Codex，`Cmd + Shift + Enter` 把你正在看的窗格放大。关掉窗格或标签时，如果前台正跑着 Claude Code、Codex 或其他要跑很久的程序，会先问一声。

`restore_previous_session` 默认开着，启动时会重新打开上次的标签和窗格，窗口、标签或窗格一开一关，一分钟内会把布局存下来，所以崩溃或强制退出也能把那份布局带回来。重启之后，原来跑着 Claude Code 或 Codex 的窗格留着最后一屏，Claude Code 用 `claude --resume` 接上，另一个窗格里的 Codex 怎么接上写在 [Codex CLI 那篇](/zh/blog/codex-cli-setup)。

`Cmd + Click` 能打开 `src/main.rs:42:7` 这种路径，程序正占着鼠标时也点得开，[给 Claude Code 选终端](/zh/blog/best-terminal-for-claude-code)那篇讲过为什么这一点要紧，在 `~/.config/kaku/kaku.lua` 里把它指到 Cursor：

```lua
config.file_link_editor = "cursor --goto"
```

`Cmd + Shift + G` 在这个窗格里打开 lazygit，Kaku 会在 `PATH` 里找这个可执行文件，也会到常见的 Homebrew 目录里找。

## 常见问题

### 能不能在 Cursor 里跑 Claude Code？

能，用 `cursor:extension/anthropic.claude-code`，或者在集成终端里跑 `claude`，`claude --resume` 接着面板里的聊天，扩展本身不会把 `claude` 装上。

### 怎么让两个 Claude Code 会话不改同一批文件？

`claude --worktree feature-auth` 会在自己的分支上再检出一份，下一个终端要用另一个名字，设置和报错写在 [worktree 那篇](/zh/blog/claude-code-git-worktrees)。

### 怎么接上之前的 Claude Code 会话？

`claude --continue` 接的是这个目录里最新的一次会话，`claude --resume` 或 `/resume` 会打开选择，这段聊天要是还在别处开着，扩展会提醒你。

### Cursor 的订阅包含 Claude 和 GPT 模型吗？

Plus 只有 Grok 模型，从 Premium 起能用 Claude 和 GPT 这类第三方模型，按 API 标价另算，加在月费之外。Claude Code 另算，走 Pro、Max、Team、Enterprise、Console，或者 Bedrock 这类提供方。

### 重启之后 Kaku 还留着什么？

留下的是标签和分屏，恢复默认开着，布局一变，一分钟内就会存下来，崩溃之后也一样，跑着 Claude Code 或 Codex 的窗格留着最后一屏，那个程序还在前台时，关掉它仍然会先问一声。

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

[Cursor 的价格页](https://cursor.com/pricing) 列了 Free、Plus、Premium、Super 和 Ultra，另外还有 Teams 和 Enterprise，价目以这一页上的数字为准，2026 年 10 月核对过。Cursor 和 Grok 的 Chat、Imagine、Voice、Bot 共用一个用量池，每周刷新，更高的档位池子更大，包含的额度用完还可以再买一笔。Free 的 agent 请求有限，聊天请求也有限，Plus 只含 Grok 模型。Premium 及以上含 Grok 的用量，第三方模型按 API 标价另计，不在这份包含的额度里，并且有花费上限。Cloud agents 和 Bugbot 的代码审查从 Premium 起才有，agent 每个方案都有，Free 也有。

概述页没有印 Claude Code 的价格，多数地方要一份 [Claude 订阅](https://claude.com/pricing)，或者一个 [Anthropic Console](https://platform.claude.com/) 账号。[扩展](https://code.claude.com/docs/en/vs-code)接受 Pro、Max、Team 或 Enterprise，也接受 Console，不用 API key，终端、VS Code 和 JetBrains 还支持 Amazon Bedrock、Google Cloud's Agent Platform 和 Microsoft Foundry。claude.ai 的方案里，`/usage` 显示当前会话和这一周，用 API key 或第三方登录时，显示的是这一次会话的费用和 token，更多价格在 [code.claude.com](https://code.claude.com)。

## 上下文和模型

Cursor 给每个模型标了默认上下文，很多还有更高的上限，这张表会随着新模型上线一直变，具体数字以[模型页面](https://cursor.com/docs)上的为准，2026 年 10 月核对过。

Claude Code 这几页没有写下一个固定的窗口大小，扩展里能看到窗口填了多少，Claude 需要时会自己压缩，想现在就压就跑 `/compact`。`@` 引用的文件会放进来，不超过 Read 工具的默认值 25,000 token，文本文件超过 256KB 会跳过，引用一个目录时只有一份列表。点一下模型名字就能换，Claude Code v2.1.284 及以后，只打 `/model` 也会打开这个选择。

## 并行和长会话

git worktree 是另一份检出，也是另一条分支，这样两个 Claude Code 任务就不会改同一批文件，仓库里得先有一次提交。

```bash
claude --worktree feature-auth
```

另一个终端换一个名字，这条命令写在[常见工作流](https://code.claude.com/docs/en/common-workflows)，一次提交都没有的话会失败，报 `Failed to resolve base branch "HEAD": git rev-parse failed`。

**Open in New Tab**（Mac 上是 `Cmd+Shift+Esc`）或 **Open in New Window** 开的是另一段对话，历史和上下文各自一份。

```bash
claude --continue
claude --resume
```

`--continue` 重新打开这个目录里最新的一次会话，没有的话就打印 `No conversation found to continue` 然后退出。`--resume`，或者会话里的 `/resume`，让你自己挑。

[claude.ai/code](https://claude.ai/code) 跑长时间的浏览器任务，一次可以开好几个，你本地没有的仓库也包括在内。桌面 App 把会话并排显示，需要付费订阅。Routines 在云上跑，电脑关着也行，在网页上建，在桌面 App 里建，或者用 `/schedule`。

2026 年 10 月核对过，Cursor 的 cloud agents 从 Premium 起才有。

## 改动怎么审

Cursor 审改动留在编辑器里，你在里面看 diff、跑检查，合并前把问题看出来。

`claude --permission-mode plan` 读仓库，你批准之前什么都不写，`Shift+Tab` 进的是同一个模式，状态栏会显示 plan mode 开着。扩展里计划以 Markdown 打开，可以直接在上面写评论，Claude Code v2.1.280 及以后，`/plan` 会切到这个模式。

Edit 会自动写文件，不再问你，Auto 有一个分类器，大部分动作先由它看过。Manual 停在并排的 diff 上，你接受、拒绝，或者改正这条提议。**Accept this change** 和 **Reject this change** 按 hunk 一步步过，从 Claude Code v2.1.275 起才有，改动超过 100 处的 diff 打开时没有这两个按钮。

`claude "commit my changes with a descriptive message"` 会做这次提交，之后用 `git diff` 看，也可以在 [lazygit](/zh/blog/lazygit-and-delta) 里看。扩展里从一条消息出发，可以把对话分叉出去，把文件倒回去，也可以两样一起做。

## 在 Cursor 里用 Claude Code

[概述](https://code.claude.com/docs/en/overview)里，Cursor 用 `cursor:extension/anthropic.claude-code` 装扩展，VS Code 用 `vscode:extension/anthropic.claude-code`，装好之后，**Open in New Tab** 在 Command Palette（`Cmd+Shift+P`）里。具体写在 [IDE 集成](https://code.claude.com/docs/en/ide-integrations)，终端里的步骤来自 [VS Code 指南](https://code.claude.com/docs/en/vs-code)。

用 Command 和反引号打开集成终端，然后跑 `claude`，CLI 用这个编辑器看 diff 和诊断。扩展不会把 `claude` 放进 `PATH`，所以终端里要另有一份独立的 CLI，`/ide` 把外面的终端接到 VS Code。`claude --resume` 接着面板里的那段聊天，这段要是还在别处开着，面板会说两份可能会把消息混在一起，关掉另一份，或者选 **Open here anyway**。

## 在 Kaku 里并排

在 [Kaku](https://kaku.fun/zh/docs/ai-coding) 里，`Cmd + D` 垂直分屏，`Cmd + Shift + D` 水平分屏，Claude Code 可以挨着一个 shell，也可以挨着 Codex，`Cmd + Shift + Enter` 把你正在看的窗格放大。关掉窗格或标签时，如果前台正跑着 Claude Code、Codex 或其他要跑很久的程序，会先问一声。

`restore_previous_session` 默认开着，启动时会重新打开上次的标签和窗格，窗口、标签或窗格一开一关，一分钟内会把布局存下来，所以崩溃或强制退出也能把那份布局带回来。重启之后，原来跑着 Claude Code 或 Codex 的窗格留着最后一屏，Claude Code 用 `claude --resume` 接上，另一个窗格里的 Codex 写在 [Codex CLI 那篇](/zh/blog/codex-cli-setup)。

`Cmd + Click` 能打开 `src/main.rs:42:7` 这种路径，程序正占着鼠标时也点得开，在 `~/.config/kaku/kaku.lua` 里把它指到 Cursor：

```lua
config.file_link_editor = "cursor --goto"
```

`Cmd + Shift + G` 在这个窗格里打开 lazygit，Kaku 会在 `PATH` 里找这个可执行文件，也会到常见的 Homebrew 目录里找。

## 常见问题

### 能不能在 Cursor 里跑 Claude Code？

能，用 `cursor:extension/anthropic.claude-code`，或者在集成终端里跑 `claude`，`claude --resume` 接着面板里的聊天，扩展本身不会把 `claude` 装上。

### 怎么让两个 Claude Code 会话不改同一批文件？

`claude --worktree feature-auth` 会在自己的分支上再检出一份，仓库得先有一次提交，下一个终端要用另一个名字。

### 怎么接上之前的 Claude Code 会话？

`claude --continue` 接的是这个目录里最新的一次会话，`claude --resume` 或 `/resume` 会打开选择，这段聊天要是还在别处开着，扩展会提醒你。

### Cursor 的订阅包含 Claude 和 GPT 模型吗？

2026 年 10 月核对过，Plus 只有 Grok 模型，从 Premium 起，文档首页上 Claude 和 GPT 那几行这类第三方模型按 API 标价计，加在月费之外。Claude Code 是另一笔账，Pro、Max、Team、Enterprise、Console，或者 Bedrock 这类提供方。

### 重启之后 Kaku 还留着什么？

留下的是标签和分屏，恢复默认开着，布局一变，一分钟内就会存下来，崩溃之后也一样，跑着 Claude Code 或 Codex 的窗格留着最后一屏，那个程序还在前台时，关掉它仍然会先问一声。

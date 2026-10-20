一个 [Claude Code skill](https://code.claude.com/docs/en/skills) 是带 `SKILL.md` 的文件夹，Claude 拿 `description` 和当前任务对，对上了才加载正文，你打 `/skill-name` 时也会加载。文件以 YAML frontmatter 开头，后面是说明，脚本和参考文件放在同一层，`name` 决定命令名，不写就用文件夹名。个人 skill 放在 `~/.claude/skills/<name>/SKILL.md`，这台机器上每个项目都能用，项目 skill 放在 `.claude/skills/<name>/SKILL.md`，只跟着这个仓库的会话走。

## 怎么区分 skill、CLAUDE.md、斜杠命令和 subagent

`CLAUDE.md` 是每次都会加载的说明，skill 放的是一套做法，比如一份你会反复粘贴的检查清单，或者 `CLAUDE.md` 里已经写成步骤的那一节。

自定义命令已经并进了 skill，原来的 `.claude/commands/deploy.md` 还能用，照样生成 `/deploy`，换成 `.claude/skills/deploy/SKILL.md` 生成的也是同一条命令。一份 [斜杠命令](https://code.claude.com/docs/en/slash-commands) 文件能写同一套 frontmatter，只是没有 `name` 和 `paths`，skill 另外可以带上旁边的文件，`description` 和任务对上时 Claude 自己也会加载它。

一个 [subagent](https://code.claude.com/docs/en/sub-agents) 有自己的上下文窗口、系统提示、工具和权限，做完只交回一段摘要，文件放在 `~/.claude/agents/` 或 `.claude/agents/`，Claude 按各自的 `description` 把任务分出去。自定义 subagent 的 `description` 加起来超过 15,000 token，启动时会警告，内置的不算在内。写上 `context: fork` 之后，skill 正文就变成那个 subagent 的任务，它看不到当前对话，不写 `agent` 时类型是 `general-purpose`。

| | 路径 | 预先加载 | 什么时候跑 |
|---|---|---|---|
| `CLAUDE.md` | 项目记忆 | 整个文件 | 一直留着 |
| Skill | `~/.claude/skills/` 或 `.claude/skills/` | 名字和 `description` | 对上了，或 `/name` |
| 命令文件 | `.claude/commands/deploy.md` | 和 skill 一样 | `/deploy` |
| Subagent | `~/.claude/agents/` 或 `.claude/agents/` | 它的 `description` | Claude 分派，或你点名 |

`disable-model-invocation: true` 不把 `description` 放进上下文，自动匹配看不到它，你自己打 `/name` 仍然可以跑这个 skill。

## SKILL.md 里有什么

开头的 `---` 必须是文件第一行，字段都可选，名字用小写加连字符，只有 `when_to_use` 用的是下划线。Claude 拿来对任务的是 `description`，不认识的字段会被忽略。YAML 解析失败时 skill 照样加载，只是字段全空，`/name` 还能用，没有字段就不会自己去匹配。

```yaml
---
name: summarize-changes
description: Summarize uncommitted changes and flag risks. Use when asked what changed.
allowed-tools: Bash(git diff *)
---

!`git diff HEAD`

Summarize the diff in a few bullets. If it is empty, say so.
```

要给这台机器上的每个项目用，就把上面这份存成 `~/.claude/skills/summarize-changes/SKILL.md`。

`` !`git diff HEAD` `` 会先跑，输出替换这一行，`!` 必须在行首，或者紧跟空白，命令失败就中止这次调用，不在 auto 模式时，你的规则不允许的命令同样会中止，Bash 超时是 2 分钟。

`allowed-tools` 只在这一轮放行 `Bash(git diff *)`，skill 正文则一直留在对话里。`user-invocable: false` 会把菜单项藏起来，Claude 按 `description` 仍然可以加载这个 skill，另设 `disable-model-invocation: true` 时，Claude Code 会拦住它自己发起的调用。

## 写一条对得上的 description

先写它做什么、什么时候用，场景放在前面，`when_to_use` 会把触发短语接在 `description` 后面，没写 `description` 就用正文第一行非空的 markdown 代替。`description` 和 `when_to_use` 加在一起，到 1,536 个字符就截断，这个上限由 `skillListingMaxDescChars` 设定。名字和 `description` 每一轮都会送出去，预算是上下文窗口的 1%，`skillListingBudgetFraction` 用来改这个比例，比如 `0.02`，要固定字符数就用 `SLASH_COMMAND_TOOL_CHAR_BUDGET`。超出预算之后，先丢掉用得最少的 `description`，名字还留着。2026 年 10 月核对过。

`paths` 的写法和按路径生效的规则一样是 glob，只有碰到匹配的文件时才会自动加载。一个 skill 一直不自己出现，多半是 `description` 里没有你会说的那些词，YAML 没有解析成功，或者模型调用被关掉了。问 `What skills are available?` 能看到当前列出来的 skill，`/doctor` 会估算这份列表的开销。`/skill-doctor` 从 v2.1.252 起还会报开销和用过的情况，内置的和企业的 skill 除外，交互会话里它开在 `/plugin` 的 Stats 标签上。

## 脚本和参考文件

`SKILL.md` 保持在 500 行以内，调用过一次，这段文字就留在对话里，不会再从磁盘读，自动压缩之后，每个 skill 可以留下最近一次运行开头的 5,000 token，从共用的 25,000 token 里取，新的先占。

`SKILL.md` 指向一份参考文件时，不会跟正文一起读进来，要等说明写了去读，Claude 才会去读那个文件，脚本是拿去执行的，不会塞进提示词。`${CLAUDE_SKILL_DIR}` 就是 `SKILL.md` 所在的目录，正文和 `allowed-tools` 里都写它，比如 `Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)`，这样授权才能和要跑的命令对上。工作区信任管不到 `allowed-tools` 这个字段，在从未信任过的文件夹里跑 `claude -p` 也一样。

## 用名字调用

消息开头的 `/fix-issue 123` 会跑这个 skill，`$ARGUMENTS` 是 `123`，`$0` 是第一个参数，正文里没有占位符时，Claude Code 会接上 `ARGUMENTS:` 和你打的那段文字。写成 `go ahead and /deploy to staging` 这种夹在句子里的样子，不会直接跑，这个名字只表示当前这条回复允许用它。

在提示符里打 `/write-tests /fix-issue 123`，两个都会加载，`123` 分给每一个，最多展开第一个 skill 加后面五个，从左往右认，遇到第一个不是行内运行、用户可直接调用的 skill 名就停下，`claude -p` 和 Agent SDK 只加载第一个。

## 用 plugin 分享

把 `.claude/skills/` 提交进仓库，这个仓库里的会话都会加载，克隆了仓库的云端会话也算。要连 subagent、hook 或 MCP server 一起装，就做成一个 [plugin](https://code.claude.com/docs/en/plugins)，清单是 `.claude-plugin/plugin.json`，里面的 skill 以 `/plugin-name:skill-name` 运行。

marketplace 是带 `.claude-plugin/marketplace.json` 的仓库，Claude Code 在第一次交互式终端会话里，会把 Anthropic 的官方 marketplace 加进来，之后从 `/plugin` 的 Discover 标签安装，也可以直接写名字：

```text
/plugin install skill-creator@claude-plugins-official
```

User scope 装给你自己，这台电脑上每个项目都能用，Project scope 写进已经提交的 `.claude/settings.json`，但每个协作者还是要自己装一次。Local scope 也只给你自己，而且只限这个仓库，装好之后每次会话都会加载。Claude 自己能调用的 skill，名字和 `description` 每一轮都在上下文里，也计入用量，正文要等 skill 跑起来才加载，官方 marketplace 的 plugin 在安装之前，Marketplaces 标签上会显示 Context cost。`skillOverrides` 不影响 plugin 里的 skill，要关掉某一个，用 `/plugin`，或者跑 `claude plugin disable`。

## 常见写错

在 `description` 里把 `CLAUDE.md` 再写一遍，每一轮都在花这份列表的预算，事实放在 `CLAUDE.md` 里，`/doctor` 会指出和已提交文件重复的本地文件，并提议把总会加载的说明挪进 skill。`description` 写到 1,536 个字符就被截断，1% 的预算装满之后，用得最少的 `description` 先被丢掉，名字仍然留着。

`/name` 能用，Claude 却从不选这个 skill，是 `description` 没进那份列表，`claude --debug` 会打出 YAML 错误，`claude plugin validate ~/.claude/skills` 能找到解析不了的 frontmatter，这要 v2.1.233 或更新。不在 plugin 里时，文件夹名里有 `<`、零宽空格，或者首尾空格，这个 skill 就加载不了。

每次改动都要执行的规则写成 [hook](/zh/blog/claude-code-hooks)，frontmatter 里的 `hooks` 从 skill 跑起来那一刻生效，一直持续到会话结束。正文里的说明要写成一直生效的样子，比如写 `Run the tests after every edit`，不要只写 `Run the tests`，因为后面的轮次不会再读这个文件。压缩之后要再调用一次，也只留得住开头那一段。

## 给耗时任务开一个窗格

[Kaku 的 CLI](/zh/docs/cli) 能从脚本或别的工具里控制 Kaku 的标签和窗格，一个 skill 可以给很长的构建、测试或日志开一个窗格：

```bash
kaku cli split-pane -- bash -c "echo hello"
```

不带命令时，`kaku cli split-pane` 拆分的是当前窗格，`kaku cli --help` 列出每一个子命令。

## 常见问题

### 想在每个项目里都用的 skill 放在哪？

放在 `~/.claude/skills/<skill-name>/SKILL.md`，Cowork 和云端会话不读这条路径，它们加载的是你 claude.ai 账号里的 skill，云端会话还会加载仓库里已经提交的项目 skill，文件夹不见了，就到 `~/.claude/skills/.trash/` 里找。

### 为什么 `/name` 能用，Claude 却从不选这个 skill？

自动匹配要有 `description`，YAML 坏了它就是空的，`disable-model-invocation: true` 故意不放进上下文，问 `What skills are available?`，或者在 v2.1.252 及以后跑 `/skill-doctor`。

### 该写成 skill 还是 subagent？

skill 跑在当前这场对话里，用的是同一份上下文，subagent 另开一份上下文，做完只交回一段摘要，`context: fork` 会把 skill 正文变成那个任务。

### 怎么不让 Claude 自己去部署？

写上 `disable-model-invocation: true`，部署留给自己打 `/deploy`。权限里的 deny 规则写上 `Skill(deploy)`，会拦住 Skill 工具，`skillOverrides` 写成 `"deploy": "user-invocable-only"` 时 `/deploy` 还留在菜单里，写成 `"off"` 就把它藏起来。

`CLAUDE.md` 就是一个普通的 Markdown 文件，Claude Code 每次开会话都会先读它，省得你一遍遍重打构建命令和项目约定。项目规则放在 `./CLAUDE.md` 并提交进仓库，个人偏好放在 `~/.claude/CLAUDE.md`，每个文件控制在 200 行左右，因为每一行都要在每一轮对话里占上下文。先跑 `/init` 生成一份草稿，再删到只剩 Claude 读代码也看不出来的内容。

## Claude Code 会读哪些文件

Claude Code 有两套记忆，很容易混在一起。[CLAUDE.md 文件](https://code.claude.com/docs/en/memory)是你自己写的指令，auto memory 则是 Claude 根据你的纠正和偏好给自己记的笔记，存在 `~/.claude/projects/<project>/memory/`，每次会话只加载 `MEMORY.md` 索引的前 200 行或 25KB。这篇主要讲前一种，后一种在文末带一句。

CLAUDE.md 可以放在四个位置，文档按从宽到窄的顺序列出，项目指令在上下文里排在用户指令之后：

| 范围 | 位置 | 谁能看到 |
|---|---|---|
| 托管策略 | macOS 上是 `/Library/Application Support/ClaudeCode/CLAUDE.md` | 这台机器上的所有人，由 IT 部署 |
| 用户 | `~/.claude/CLAUDE.md` | 只有你，所有项目 |
| 项目 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队，通过 git 共享 |
| 本地 | `./CLAUDE.local.md` | 只有你，当前项目，要加进 `.gitignore` |

托管那份不能被个人设置排除，公司拿它放统一规范，大多数人只会用到中间两个。

## 这些文件怎么加载

Claude Code 不会从中挑一个，而是把它们全部拼进上下文，所以是叠加而不是覆盖。它会从工作目录一路往上，把每一层的 `CLAUDE.md` 和 `CLAUDE.local.md` 都读进来，顺序是从文件系统根目录往下排，离你启动 Claude 的位置最近的那份最后读到，同一个目录里 `CLAUDE.local.md` 排在 `CLAUDE.md` 后面，所以你的个人备注在最末尾。

工作目录下面的子目录就不一样了，它们不会在启动时加载，Claude 第一次读、写或编辑那个子目录里的文件时才会把对应的 CLAUDE.md 读进来，所以 `packages/api/CLAUDE.md` 在 Claude 真正去改 `packages/api` 之前不占任何上下文。

[[figure:claude-md-load-order|托管策略、用户、上级目录和工作目录的 CLAUDE.md 在启动时按顺序拼进上下文，子目录里的 CLAUDE.md 要等 Claude 碰到那里的文件才加载|所有文件是拼接进上下文的，离工作目录最近的最后读到，子目录里的文件要等 Claude 去那里干活时才加载。]]

实际用起来有两点要记住。这些内容是作为系统提示词之后的一条用户消息送进去的，不是系统提示词本身，Claude 会尽量照做，但没有任何东西在强制执行。另外块级的 HTML 注释（`<!-- 给维护者的备注 -->`）在注入前会被去掉，可以放心给人类读者留备注，不会花 token。

## 引用其他文件和 rules 目录

CLAUDE.md 里可以用 `@path` 引入别的文件，相对路径是相对于写了这个引用的文件来解析，引用可以嵌套，最多四层：

```markdown
项目概览见 @README，可用的 npm 脚本见 @package.json。

# 工作流
- git 流程 @docs/git-instructions.md
```

引用方便你把一份长文件拆开整理，但并不省上下文，被引用的文件会跟着引用它的文件一起在启动时加载。放在反引号里的路径只是普通文字，不会被引入。如果引用指向工作目录之外，比如 `@~/.claude/my-project-instructions.md`，Claude Code 在一个项目里第一次遇到时会弹出审批。

真想省上下文要用 `.claude/rules/`，每个 Markdown 文件讲一个主题，带 `paths` 前置字段的规则只有在 Claude 处理匹配的文件时才加载：

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API 规则
- 每个接口都要校验输入。
```

没写 `paths` 的规则和主文件一样在启动时加载。另一半分工在 [skill 那篇](/zh/blog/claude-code-skills)里，只在偶尔需要时才用到的多步流程适合做成 skill，只在你调用或 Claude 判断用得上时才加载。

## 用 /init 和 /memory 创建和查看

在项目里跑 `/init`，Claude 会分析代码库，把它发现的构建命令、测试说明和约定写成一份 CLAUDE.md，已经有文件的话它会给出改进建议，不会直接覆盖。把输出当草稿，Claude 读代码就能知道的删掉，它不可能知道的补上。`/init` 还会读取 `.cursor/rules/` 里的 Cursor 规则和 `.github/copilot-instructions.md` 里的 Copilot 规则。先设置 `CLAUDE_CODE_NEW_INIT=1` 的话，它会换成多阶段流程，先问你要创建哪些东西。

`/memory` 会列出用户和项目范围内所有的记忆文件，包括还不存在的 CLAUDE.md 条目，选中就在编辑器里打开，auto memory 的开关也在这里。想确认到底加载了什么，跑 `/context`，看 Memory files 下面的列表。

## 该写什么

文档的说法是，写下那些你否则要反复解释的东西，构建命令、约定、项目结构和「一律这样做」的规则。适合新增一行的时机有三种，Claude 重复犯同一个错，代码评审里指出了它本该知道的事，或者你把同一句纠正打了第二遍。每一行都要能检验，「用 2 个空格缩进」可以，「代码格式要规范」不行。

下面是一份按这个思路写的小文件：

```markdown
# 构建与测试
- 安装：`pnpm install`
- 跑单个测试：`pnpm vitest run path/to/file.test.ts`
- 收尾前类型检查：`pnpm tsc --noEmit`

# 约定
- API handler 放在 `src/api/handlers/`
- 一律用具名导出，不用默认导出

# 坑
- `pnpm test` 需要本地 6379 端口有 Redis
- 不要手改 `src/generated/`，改了要跑 `pnpm codegen`
```

不该写的有这几类，密钥，因为这个文件要提交进仓库，还会送给模型；大多数任务用不到的长篇参考文档；代码本身已经说明的东西，比如目录清单和依赖列表；还有每次都必须成立的规则，最后这种文档建议用 [hook](/zh/blog/claude-code-hooks)，hook 是当作 shell 命令执行的，不看 Claude 怎么决定。在 CLAUDE.md 里写「不要执行 `rm -rf`」只是请求，不是护栏。

## 保持简短

文档给的体量建议很具体，每个文件控制在 200 行以内，更长的文件占更多上下文，也会降低 Claude 遵守的程度。Claude Code 能加载最大 4 MiB 的文件，所以这个限制说的是遵守程度而不是加载器。文件超过推荐长度，启动时和 `/status` 里都会看到警告。另一个问题是互相矛盾，两个文件说法不一致时 Claude 可能随便挑一个，所以用户文件、项目文件、子目录文件和 rules 目录要放在一起清理。`/doctor prompt-audit` 会让 Claude 去找过时和冲突的指令并给出修改建议，你批准之前不会改任何文件。

`/compact` 之后，项目根目录的 CLAUDE.md 会重新从磁盘读取并注入，只在对话里说过的指令就没了，所以同一件事说过两遍，就该写进文件。

## AGENTS.md 和 Codex

Codex 读的是 `AGENTS.md`。它先读 `~/.codex/AGENTS.override.md`，没有的话读 `~/.codex/AGENTS.md`，再从项目根目录往下到工作目录，每个目录取一个文件，拼接起来后面的优先，默认上限 32 KiB。Claude Code 从 v2.1.277 起可以直接读 `AGENTS.md`，但只有工作目录及其上层没有 `CLAUDE.md` 或 `CLAUDE.local.md` 时才读，两者都有就只读 `CLAUDE.md`。

想保持单一来源，可以在 `CLAUDE.md` 里这样写：

```markdown
@AGENTS.md

## Claude Code

`src/billing/` 下的改动先用 plan mode。
```

用软链接（`ln -s AGENTS.md CLAUDE.md`）也行，但 Claude 的编辑工具不会通过软链接写入，在 Windows 上提交进仓库的软链接还可能被检出成一行文字。两个工具的整体对比在 [Codex 和 Claude Code](/zh/blog/codex-vs-claude-code)，Codex 这一侧的配置在 [Codex CLI 安装](/zh/blog/codex-cli-setup)。

## 在 Kaku 里用

Kaku 不会动你的指令文件。`kaku ai` 修改的是 Claude Code 这类工具的设置，保留你自己写的字段，[AI 编程文档](/zh/docs/ai-coding)里也写明它不会自己给你的 agent 加 hook 或指令。Kaku 能帮上忙的是周边的工作流，`Cmd + Click` 可以打开 Claude 打印出来的文件路径，用 `file_link_editor` 指定的编辑器，所以 Claude 报出 CLAUDE.md 的路径时能直接点开。`Cmd + D` 分屏，可以把编辑 `CLAUDE.md` 的窗格放在运行中的会话旁边，用 `/context` 对照检查。

## 常见问题

### 不想提交的个人偏好放哪里

放在项目根目录的 `./CLAUDE.local.md`，并加进 `.gitignore`，它在同一目录里排在 `CLAUDE.md` 之后加载。在依赖 `AGENTS.md` 的项目里，只要有 `CLAUDE.local.md`，Claude 就不再读 `AGENTS.md`，除非你在 `/config` 里把 Project instructions 设成 `claude-md-and-agents-md`。

### Claude 为什么不听我的 CLAUDE.md

先用 `/context` 看文件有没有出现在 Memory files 下面，子目录里的 CLAUDE.md 是按需加载的，不会出现在这个列表里，加载时终端会打出一行带路径的 `Loaded`。然后检查措辞是不是太含糊，有没有两个文件互相矛盾，必须每次执行的规则就改用 hook。

### CLAUDE.md 写得越长 Claude 越懂我的项目吗

不是。文档说超过大约 200 行，遵守程度会下降，上下文成本会上升。只跟某些路径有关的内容放 `.claude/rules/`，流程放 skill。

### CLAUDE.md 和 auto memory 是一回事吗

不是。CLAUDE.md 是你写的，auto memory 是 Claude 自己写的，在 `~/.claude/projects/<project>/memory/` 里，只存在这台机器上，`MEMORY.md` 只加载前 200 行或 25KB。

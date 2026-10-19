# Claude Code 的 plan mode 什么时候用、怎么用

> plan mode 允许做什么，怎么用 Shift+Tab、/plan 或命令行参数打开，怎么审和改计划，以及什么时候不用它。

发布于 2026-09-23 · Tw93 · https://kaku.fun/zh/blog/claude-code-plan-mode

plan mode 让 Claude Code 读仓库、写一份计划，在你批准之前不改源码，已经能用 bypass permissions 的交互式终端是例外。可以按 `Shift + Tab` 切过去，也可以只在一条提示词前面加上 `/plan`，或者用 `claude --permission-mode plan` 启动。批准这份计划会退出 plan mode，接着按你点的那一项对应的权限模式继续。

## plan mode 允许什么、拦住什么

[常见工作流](https://code.claude.com/docs/zh-CN/common-workflows)里，plan mode 用来在改动写进磁盘之前先看一遍，规则以[权限模式](https://code.claude.com/docs/en/permission-modes)为准。交互式终端里已经能用 bypass permissions 时，Claude 收到的指令仍然是只写计划、不改文件，可它在规划期间一旦真的改文件或跑 shell，就不会再问。ask 规则还是会问，关键路径上的 `rm` 或 `rmdir` 也一样，文件系统根目录、你的主目录、当前工作目录都算关键路径。

规划期间的 shell 命令按下面的顺序，命中第一条就照那一条办，2026 年 10 月核对过。

- **交互式终端里已经能用 bypass permissions**，规划阶段的命令不走分类器，也不弹确认。
- **auto mode 可用，并且 `useAutoModeDuringPlan` 开着，这是默认**，除了关键路径上的删除，其余 shell 命令交给分类器，放行的就执行，拒绝的就拦住。
- **auto mode 不可用，或者 `useAutoModeDuringPlan` 关着**，内置只读集合以外的命令都会问，sandbox auto-allow 开着也一样。

auto mode 可用时，权限模式那张表里，plan mode 这一行能做的是读文件，外加分类器放行的命令，能不能用取决于 Claude Code 的版本、当前模型，还有组织的设置。`.git`、`.claude`、`.zshrc` 这些受保护路径不会自动放行，规划期间 auto mode 可用就交给分类器，不可用就问你。`~/.claude/plans/` 下的计划文件，或者你设的 `plansDirectory`，不在这条限制里。

## 怎么进入 plan mode

`Shift + Tab` 每按一次换一个权限模式，从 auto 开始，第一下到 Manual，配置里写的是 `default`，再按到 `acceptEdits`，再按到 `plan`。状态栏对应显示 `manual mode on`、`accept edits on` 或 `plan mode on`。可选模式接在 `plan` 后面，先是 `bypassPermissions`，`auto` 排在最后，`dontAsk` 不在这个循环里。Windows 上 Node 或 Bun 运行时没打开 VT input mode 时，改用 `Alt + M` 切换。在 plan mode 里再按一次 `Shift + Tab` 会离开，计划不算批准。

```bash
claude --permission-mode plan
```

同一个参数跟 `-p` 一起用也行，终端会话要默认进入 plan mode 时，写进项目的 `.claude/settings.json`，只影响这个项目里的终端会话，写进 `~/.claude/settings.json`，这台机器上每个终端会话都这样：

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

项目或托管设置里的值优先于用户文件 `~/.claude/settings.json`，`auto` 和 `bypassPermissions` 写在项目的 `.claude/settings.json` 或 `.claude/settings.local.json` 里不会生效，`plan` 会。VS Code 扩展决定起始模式时不看项目里的 `.claude/settings.json`，要在 VS Code 的用户设置里把 `claudeCode.initialPermissionMode` 设成 `plan`。

Claude Code v2.1.283 起，交互式终端会话一开始就是 auto mode。更早的版本里，Pro、Max 和 Team 的会话取到 feature flag 时也从 auto 起步，前提是 macOS、Linux 和 WSL 上不低于 v2.1.228，原生 Windows 不低于 v2.1.233，其他情况都从 Manual 开始。命令行参数或 `permissions.defaultMode` 会盖过这个起点，选了 auto 但当时不可用，会话就从 Manual 开始。刚安装或刚升级后的第一次会话，feature flag 还没到，起点可能不一样。

计划批准之后，再按 `Shift + Tab`，或者发一条以 `/plan` 开头的提示词，会再进一次 plan mode。

## 一条写清楚的 plan 提示词

要改哪一处、哪些行为必须保持原样、计划里列出会动哪些文件和准备跑的测试、还有哪些地方不动，都写在提示词里。

```text
/plan Add a null check in src/auth/user.ts before the profile lookup.
Keep the current error type. List every file you would change, the test command you would run, and anything you would leave alone.
```

`@src/auth/user.ts` 会把这个文件的内容带上，只要没超过 Read 工具的上限，默认 25,000 token，文本文件大于 256KB 就不会带上。任何终端里按 `Ctrl + J` 都会插入换行，先打一个 `\` 再按回车也一样，哪些终端不用设置就能用 `Shift + Enter` 换行，[终端对比](/zh/blog/best-terminal-for-claude-code)那篇列过。

## 批准，或者接着改计划

计划写好以后，Claude 会问下一步怎么走，`Yes, and use auto mode` 是批准并继续用 auto mode，auto mode 不可用时这一项写成 `Yes, auto-accept edits`。会话启动时就带了 bypass permissions，这一项写成 `Yes, and switch to BYPASS PERMISSIONS (no further prompts) for this session`。`Yes, manually approve edits` 同样是批准，每一处修改你自己看，`No, keep planning` 留在 plan mode，你可以接着说计划要改哪里。批准会退出 plan mode，切到这一项对应的权限模式，`Ctrl + G` 在 Claude 往下做之前，用你的默认文本编辑器打开它给出的计划。

## 什么时候不用 plan mode

想在写进磁盘之前先读一遍改动，或者先把代码库看清楚再改，用 plan mode。Manual 模式下读文件不会问，状态栏显示 `manual mode on`，用 `claude --permission-mode default` 启动，`manual` 是 CLI 接受的别名。

`acceptEdits` 适合准备用 `git diff` 再看一遍的修改，从 Manual 按一次 `Shift + Tab` 就进去，也可以 `claude --permission-mode acceptEdits` 启动，状态栏显示 `accept edits on`。它会自动批准文件修改，以及工作目录或 `additionalDirectories` 里的 `mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp` 和 `sed`，前面带 `LANG=C` 这样的前缀，或者套一层 `timeout`，也算。其他 shell 命令、受保护路径上的写入，还有关键路径上的 `rm` 或 `rmdir`，仍然会问。

任务比较长、方向也信得过的时候用 auto mode，它在后台做安全检查，日常的确认会少一些，但不保证安全。

## plan mode 和 effort

plan mode 决定哪些动作能跑，扩展思考和 effort（思考强度）决定一条请求想多深。macOS 按 `Option + T`，Windows 和 Linux 按 `Alt + T`，用来开关扩展思考，macOS 不用把 Option 配成 Meta 也能用。Opus 5.5、Sonnet 5.5、Haiku 5.5 和 Fable 这几个模型不受这个开关影响，它们一直开着扩展思考。`/effort` 改的是 effort，一发出去就生效，要是弹出缓存警告，确认之后，新的档位从这一轮的下一条请求开始用。

## Kaku 里的 Shift + Tab

Kaku 默认的终端快捷键里没有 `Shift + Tab`，[快捷键](/zh/docs/keybindings)那一页也没列，所以在窗格里这个键会送到 Claude Code。状态栏一直不变的话，打开 `~/.config/kaku/kaku.lua` 看 `config.keys`，往这张表里插入，直接赋一张新表会把默认快捷键换掉。要是里面有一条绑了 Shift 的 `Tab`，这个键在 Claude Code 看到之前就被吞掉了，别的终端把 `Shift + Tab` 吞掉，也是查同一处。

AI 聊天面板是分开的，`Cmd + L` 打开它，Simple Model 和 Deep Model 不一样时，在那个面板里按 `Shift + Tab` 是在两个模型之间切换，[功能特性](/zh/docs/features)里写了，这个切换不碰 Claude Code 的权限模式。

## 常见问题

### 按几次 Shift + Tab 才到 plan mode？

从 auto mode 按三次，从 Manual 按两次，状态栏出现 `plan mode on` 就停，`claude --permission-mode plan`，或者一条以 `/plan` 开头的提示词，不用按。

### plan mode 开着时，Claude 能改文件吗？

批准之前不会改文件，已经能用 bypass permissions 的交互式终端除外，ask 规则和关键路径上的 `rm` 或 `rmdir` 还是会问，其他 shell 命令按上面三种情况走。

### 开始改文件之前，怎么改这份计划？

按 `Ctrl + G`，用你的默认文本编辑器打开它给出的计划，选 `No, keep planning` 会留在 plan mode，再按一次 `Shift + Tab` 会离开，不算批准。

### 把 effort 调高，能代替 plan mode 吗？

`Option + T` 开关扩展思考，`/effort` 改的是下一条请求的 effort，退出 plan mode、开始改文件，靠的是你批准了这份计划。

### 为什么 Shift + Tab 没有反应？

在 Kaku 里，先到 `~/.config/kaku/kaku.lua` 的 `config.keys` 下面找有没有绑了 Shift 的 `Tab`。还要看是在哪里按的，AI 聊天面板里 Simple Model 和 Deep Model 不同时，这个键是在两个模型之间切换。另外从 auto mode 按第一下，状态栏显示的是 `manual mode on`，不是没反应。

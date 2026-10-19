Claude Code 用两层来决定要不要问你，一层是定下基线的权限模式，另一层是 `settings.json` 里针对具体工具的 allow、ask、deny 规则，规则会盖过模式。`--dangerously-skip-permissions` 打开的是跳过检查的 `bypassPermissions` 模式，Anthropic 的文档说只该在容器或虚拟机里用，因为它对提示词注入和误操作没有任何保护。日常工作更稳的做法是中间路线，用 `acceptEdits` 或 auto 模式，配一小份 allow 列表、几条 deny 规则，再加一个 hook 拦住你绝不想让它跑的那条命令，这样仍然安静。

## 权限模式

[权限模式文档](https://code.claude.com/docs/en/permission-modes)（2026 年 10 月 19 日读的）按配置值列出这些模式：

| 模式 | 不用问就能做的事 | 适合 |
|---|---|---|
| `default`（显示为 Manual） | 只读 | 逐个审查，敏感工作 |
| `acceptEdits` | 读、改文件，以及 `mkdir`、`touch`、`mv`、`cp` 这类常见文件系统命令 | 事后再审查代码的迭代 |
| `plan` | 读，auto 模式可用时还包括分类器批准的命令，编辑要等你批准方案 | 改动之前先摸清代码库 |
| `auto` | 全部，由一个分类器模型在后台审查动作 | 长任务，少打断 |
| `dontAsk` | 工作目录里的文件读取和预先批准的工具，会弹提示的一律拒绝 | CI 和脚本 |
| `bypassPermissions` | 全部 | 只限隔离的容器和虚拟机 |

终端里按 `Shift+Tab` 循环切换模式，状态栏会显示当前是哪个，比如 `⏵⏵ accept edits on` 或 `⏸ plan mode on`。有两个模式不一定在循环里，`dontAsk` 永远不在，`bypassPermissions` 只有在你用对应的标志或设置启动时才会出现。也可以用 `claude --permission-mode plan` 启动，或者在设置文件里写 `permissions.defaultMode`。

如果你对 Claude Code 的印象还停在几个月前，有一个变化要留意，2.1.283 或更新的版本里，auto 模式是交互式终端和 VS Code 会话的内置起始模式，文档把它描述成减少提示，而不是安全保证，所以别默认一个会话什么都会问，先看一眼状态栏。

## allow、ask、deny 规则

规则写在 `settings.json` 的 `permissions` 下，`/permissions` 会列出所有规则以及每条来自哪个文件。allow 规则让工具不用批准就能跑，ask 规则每次都弹提示，deny 规则直接拦住，检查顺序是 deny、ask、allow，第一个命中的算数，所以 deny 总是压过更具体的 allow，没法在 deny 里再开例外。

规则的写法是 `Tool` 或 `Tool(specifier)`，裸的 `Bash` 匹配所有 shell 命令，括号里的限定词把范围收窄：

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./secrets/**)",
      "Bash(rm *)"
    ]
  }
}
```

Bash 规则里的 `*` 匹配任意文本，要放在子命令后面，`Bash(git log *)` 只放行 `git log`，而 `Bash(git *)` 放行所有 git 命令。复合命令会在 `&&`、`||`、`;`、管道和换行处拆开，每一段都得各自匹配，所以 `Bash(safe-cmd *)` 不会放行 `safe-cmd && other-cmd`。文件方面，`Read` 和 `Edit` 规则用 gitignore 风格的模式，`//path` 是绝对路径，`~/path` 从家目录算起，`./path` 相对当前目录，写给 `Write` 的规则会被接受但从不被查询，所以要写 `Edit`。

## 一次调用是怎么被决定的

规则、hook 和模式组合起来时顺序很重要，下面是一次工具调用的路径。

[[figure:claude-code-permission-layers|工具调用先过 PreToolUse hook，再过 deny、ask、allow 规则，规则都没命中才看权限模式，放行的 Bash 命令在沙盒里运行，hook 返回 2 或命中 deny 规则就会被拦下|hook 能在任何规则被读到之前拦下调用，接着由规则决定，模式只处理规则没覆盖到的部分。]]

PreToolUse hook 先跑，如果它以退出码 2 结束，调用在看任何规则之前就被拦下，哪怕有 allow 规则本来会放行。hook 放过去之后，不管它返回了什么，deny 和 ask 规则照样会被评估，所以 hook 返回 allow 也压不过 deny 规则。规则定不了的时候由模式的基线决定。对 Bash 来说，可选的沙箱是批准之后的另一层，在操作系统层面限制已批准的命令能碰什么，文档建议权限和沙箱一起用，因为提示词注入骗过模型之后，沙箱的限制仍然有效。

权限规则是由 Claude Code 执行的，不是由模型执行的，文档说你在提示词或 `CLAUDE.md` 里写的指令会影响 Claude 想做什么，但不会改变 Claude Code 允许什么。

## bypassPermissions 到底冒什么险

`bypassPermissions` 关掉提示和安全检查，包括对 `.git`、`.claude`、`.zshrc`、`.mcp.json` 这类受保护路径的写入。deny 规则在这个模式下仍然拦截，allow 规则则没有作用，因为一切本来就被允许。有几样即使在这里也仍会提示，ask 规则、指向 `/` 或家目录这类关键路径的 `rm` 和 `rmdir`，以及需要你输入的工具。

文档警告说，这个模式对提示词注入没有任何保护，也就是 Claude 读到的文件或网页里的文字被它当成指令执行。官方的建议是只在隔离环境里用，比如容器、虚拟机，或者没有网络的 dev container。标志是 `claude --dangerously-skip-permissions`，等价于 `--permission-mode bypassPermissions`，交互式会话第一次用要接受一个警告对话框，在 Linux 和 macOS 上以 root 或 `sudo` 运行时会拒绝启动，除非检测到受认可的沙箱。[沙箱环境页面](https://code.claude.com/docs/en/sandbox-environments)比较了内置的沙箱 Bash 工具、沙箱运行时、dev container 和虚拟机，权限模式页面则说，想要少提示又不想承担这种风险，auto 模式保留了后台安全检查。

管理员可以在托管设置里把 `permissions.disableBypassPermissionsMode` 设成 `"disable"`，你也可以在自己的设置里设，把自己锁在这个模式之外。

## 更稳的中间路线

一份让大部分提示消失、又不关掉检查的配置：

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git commit *)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./secrets/**)",
      "Bash(rm *)",
      "Bash(git push --force *)"
    ]
  }
}
```

项目里放进 `.claude/settings.json`，所有会话通用就放 `~/.claude/settings.json`。`acceptEdits` 会自动批准工作目录里的编辑和 `rm`，`Bash(rm *)` 的 deny 规则就是为此加的。文档提到规则可能漏掉换了写法的命令，比如写成 `git -C . push` 的推送，`Bash(git push *)` 就匹配不到，所以把规则当成常见情况的护栏，别当安全边界，真正绝不能发生的事再加 hook 或 Bash 沙箱。

## 用 hook 拦命令

hook 是 Claude Code 在工具调用之前运行的一个脚本，退出码 2 会拦住调用，脚本写到 stderr 的内容会作为理由回到 Claude 手里。文档自带的例子保护的是文件，下面是针对命令的变体：

```bash
#!/bin/bash
# .claude/hooks/block-danger.sh
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ "$CMD" == *"git push --force"* || "$CMD" == *"rm -rf"* ]]; then
  echo "Blocked: $CMD matches a protected pattern" >&2
  exit 2
fi
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-danger.sh" }
        ]
      }
    ]
  }
}
```

先 `chmod +x .claude/hooks/block-danger.sh`，再让 Claude 跑一条被拦的命令，应该会被拒绝，Claude 会收到你写的消息作为理由。想放行除了几条之外的所有 Bash 命令时，文档推荐的就是这个写法，把 `Bash` 加进 allow 列表，再让 hook 拒绝例外。这种字符串匹配换个写法就能绕过，所以凡是可能毁数据的，都和 deny 规则配合用，hook 的事件和设置见 [Claude Code hooks](/zh/blog/claude-code-hooks)。

## 知道有提示在等你

少弹提示是目标，但剩下的那些提示在你切到别的窗口时会让会话停住。Claude Code 2.1.295 或更新的版本会把正在干活、等你还是已完成告诉 Kaku，所以 Kaku 0.25.0 或更新的版本在 Kaku 处于后台时无需任何设置就会发通知，更旧的版本和其他终端要配置通知渠道，见 [Claude Code 通知](/zh/blog/claude-code-notifications)。如果你同时并排跑几个 agent，[git worktree](/zh/blog/claude-code-git-worktrees) 能把它们的改动隔开。

## 常见问题

### --dangerously-skip-permissions 安全吗

在平时用的机器上不安全，文档把它限制在隔离环境里，并说它对提示词注入没有保护，本地工作用 auto 模式或上面的中间路线。

### 怎么只对一条命令关掉提示

给它加一条 allow 规则，比如 `Bash(npm test *)`，或者在提示上选 Yes, and don't ask again，Bash 命令会把规则存进仓库根目录的 `.claude/settings.local.json`。

### 为什么 bypass 模式下 Claude 还会问

没有哪个模式会自动批准 ask 规则、指向关键路径的 `rm` 或 `rmdir`，以及需要你输入的工具，所以 bypass 模式下它们照样会提示。

### CLAUDE.md 能拦住命令吗

不能，它只影响 Claude 想做什么，真正改变 Claude Code 允许什么的是规则、模式和 hook。

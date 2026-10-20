# 在 Mac 上配好 Codex CLI：安装、登录和配置

> 在 macOS 上安装 OpenAI 的 Codex CLI，用 ChatGPT 账号或 API key 登录，再配好 config.toml、审批、通知和会话恢复。

发布于 2026-09-29 · Tw93 · https://kaku.fun/zh/blog/codex-cli-setup

在 Mac 上配好 Codex CLI 只要三条命令，`brew install --cask codex` 装上，`codex login` 登录，再进到项目目录里跑 `codex`。常用的用户设置在 `~/.codex/config.toml` 里，用哪个模型，不用问你就能做多少事，需要你的时候怎么提醒你，都能在这里配置。内容按 2026 年 10 月的 Codex CLI 0.163.0 核对过。

## 安装

官方给了三种装法，挑一个就行：

```bash
# Homebrew
brew install --cask codex

# 安装脚本
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# npm
npm install -g @openai/codex
```

装完用 `codex --version` 确认版本，以后升级直接用当初安装它的那个工具。哪里看着不对就跑 `codex doctor`，它会把安装、配置、登录和运行环境一起查一遍。

## 登录

`codex login` 会打开浏览器，用 ChatGPT 账号登录，套餐里带 Codex 的话这是最省事的。想用 API key 的话，别直接贴在命令行里，不然会留在 shell 历史里，从环境变量用管道传进去：

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

没有浏览器的机器上用 `codex login --device-auth`，它会给一个代码，拿到另一台设备上输入。使用文件存储时，凭据存在 `CODEX_HOME` 下的 `auth.json`，默认就是 `~/.codex/auth.json`，也可以通过 [`cli_auth_credentials_store`](https://learn.chatgpt.com/docs/config-file/config-reference) 选择系统钥匙串或只存在内存里。`codex login status` 可以看当前是哪个账号，`codex logout` 退出。

## 设置从哪里来

Codex 的设置是一层层叠起来的，离这一次运行越近的那层优先。

![Codex 设置的四层，从上到下是命令行参数、项目配置、用户配置和内置默认值](https://kaku.fun/img/blog/codex-config-layers.webp)

*命令行参数压过项目配置，项目配置压过用户配置。*

- **内置默认值**，其他地方都没设的时候才用。
- **`~/.codex/config.toml`** 是用户配置，对每个会话都生效。
- **仓库里的 `.codex/config.toml`** 只对这个项目生效，会覆盖用户配置。
- **命令行参数**，比如 `-m`、`-s`、`-a` 和 `-c key=value`，只管这一次运行，优先级最高。

`-c` 能接配置文件里的任意一个键，嵌套的表用点号连起来，所以 `codex -c tui.notification_method=osc9` 可以先试一下某个设置，满意了再写进文件。另外还有命名的 profile，`codex -p work` 会把 `~/.codex/work.config.toml` 叠在用户配置上面。

## 最值得先改的几个设置

一份很短的用户配置就够大多数人用了：

```toml
model_reasoning_effort = "medium"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[tui]
notification_method = "osc9"
```

`model` 不写就用默认的，要写的话填会话里 `/model` 列出来的名字，这个列表跟账号有关，`/model` 也能直接切换当前会话的模型，不用改文件。

决定 Codex 能自己做多少事的是下面两个设置，改之前值得先弄明白：

| 设置 | 可选值 | 含义 |
|---|---|---|
| `sandbox_mode` | `read-only`、`workspace-write`、`danger-full-access` | Codex 执行的命令能碰到哪里，`workspace-write` 允许在项目里写，磁盘其他地方只读 |
| `approval_policy` | `on-request`、`never` | `on-request` 让模型在越出沙箱前先问你，`never` 从不问，失败直接交还给模型 |

先用 `workspace-write` 配 `on-request` 比较稳妥，`danger-full-access` 配 `never` 等于两道防线都拆了，那是给本来就隔离好的机器用的，不是给你天天用的笔记本。

## 通知

Codex 默认在做完或者等你批准时响一下终端铃声，而且只在终端没获得焦点时响，这一声能不能变成桌面通知要看终端。Kaku 会把后台窗口里的铃声变成通知，设成 `notification_method = "osc9"` 之后，通知里显示的是 Codex 自己写的消息，而不是笼统的一句。`tui.notification_condition = "always"` 则是终端在前台也提醒。

如果什么都没收到，可以看这篇[通知指南](/zh/blog/claude-code-notifications)，里面讲了会挡住通知的 macOS 权限和 tmux 设置。

## 接着上次的会话

Codex 会把每个交互式会话都记下来，关掉终端也不会丢：

```bash
codex resume          # 从最近的会话里挑一个
codex resume --last   # 直接接上最近一次
codex fork --last     # 从最近一次分叉出去，原来那个不动
```

终端这一侧是另一回事，在 Kaku 里重启之后，原来开着的标签和分屏会回来，之前跑着 Codex 的窗格还会保留最后一屏，接上之前能先看到每个会话停在哪里。

## 在 Kaku 里用同一个 Codex 登录

Kaku 自带的助手负责 `#` 生成命令和 `Cmd + L` 对话，它不需要你再准备一个 API key，可以直接跟着现有的 Codex 连接走。运行 `kaku ai`，选 Kaku Assistant，把 Auth Type 设成 `codex`，Kaku 就会去读用户级的 Codex 配置，包括 ChatGPT 登录或 API key，以及选中的服务商。同一个界面里的 Codex 那一项也能看到 Codex 自己的模型和登录状态。

## 常见问题

### Codex CLI 免费吗？

CLI 本身是开源的，但要用起来，需要套餐里带 Codex 的 ChatGPT 账号，或者按用量计费的 OpenAI API key。

### Mac 上 Codex 的配置文件在哪？

用户设置在 `~/.codex/config.toml`，项目设置在仓库里的 `.codex/config.toml`，想把用户目录放到别处就设 `CODEX_HOME`。

### Codex CLI 怎么换模型？

会话里用 `/model`，只换一次就用 `codex -m <模型名>`，想每次都用就在 `~/.codex/config.toml` 里设 `model`。

### 关掉终端之后怎么接着 Codex 的会话？

在同一个项目里跑 `codex resume --last`，或者用 `codex resume` 从列表里挑。

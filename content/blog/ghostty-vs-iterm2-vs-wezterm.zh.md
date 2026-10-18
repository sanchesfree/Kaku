Ghostty、iTerm2 和 WezTerm 都是好终端，三者真正的区别在配置方式上，iTerm2 是一个设置窗口，功能比另外两个都多，Ghostty 是一个原生的快 App 加一份 `key = value` 的文本文件，WezTerm 则是一段能自己算出配置的 Lua 脚本。离不开 `tmux -CC` 或 trigger 就选 iTerm2，想要快、配一次就不管就选 Ghostty，想给终端写程序就选 WezTerm，下面按分屏、图片、通知、发版节奏和 AI 编程工具逐项对比，版本按 2026-10-17 核对，iTerm2 3.7.6，Ghostty 1.3.1，WezTerm 是 20240203 加上之后的 nightly，Warp、Kitty、Alacritty 和 Terminal.app 放在[Mac 终端怎么选](/zh/blog/best-terminal-for-mac)里讲。

[[figure:terminal-config-models|iTerm2 用设置窗口配置并存成 plist，Ghostty 用一行行 key = value 的文本文件，WezTerm 用可热重载的 Lua 脚本|配置方式对日常使用的影响，比任何一个单独的功能都大。]]

## 配置

**iTerm2** 所有东西都在设置窗口里，存成一个 property list，profile 能让一个 App 装下好几套配置，几乎每个行为都能在某处找到一个勾选框。这种深度是它的长处，可想在几台机器之间同步，就得导出 profile，或者让 iTerm2 从一个文件夹里读保存的偏好设置。

**Ghostty** 读的是 `~/.config/ghostty/config.ghostty`，1.2.3 之前叫 `config`，就是一串设置：

```ini
font-family = JetBrains Mono
font-size = 15
macos-option-as-alt = true
```

`Cmd + Shift + ,` 重新加载，`ghostty +show-config --default --docs` 会把所有选项连同说明一起打印出来，三个里面它最好读，也最好放进 dotfiles。

**WezTerm** 会执行 `~/.wezterm.lua`，用它返回的那张表：

```lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()
config.font = wezterm.font 'JetBrains Mono'
config.font_size = 15
return config
```

因为它是程序，配置里可以按系统外观挑配色，可以根据事件拼状态栏，也可以定义执行 Lua 的快捷键，保存后自动重新加载。代价是写错一个字就是一个 Lua 报错，而不是被忽略的一行。

## 分屏、标签和 tmux

三个都有标签和分屏，区别在怎么对待 tmux。

- **iTerm2** 有 `tmux -CC`，把 tmux 会话显示成原生的窗口、标签和分屏，远程服务器上 tmux 的持久化你照样有，滚动和复制却用的是终端自己的，macOS 上没有别的终端做得这么好。
- **WezTerm** 自带多路复用，远程机器上也装了 WezTerm 的话，不用 tmux 会话也能一直跑着。
- **Ghostty** 有原生分屏，和 tmux 就是普通地一起用，没有专门的集成。

## 图片

| | iTerm2 | Ghostty | WezTerm |
|---|---|---|---|
| iTerm2 内联图片（`imgcat`） | 支持 | 不支持 | 支持 |
| Kitty 图片协议 | 支持 | 支持 | 支持 |
| Sixel | 支持 | 不支持 | 支持 |

现在大多数能在终端里显示图片的工具都用 Kitty 协议，所以常见情况三个都能覆盖。

## 通知

三个都能把转义序列变成 macOS 通知，但 AI 编程工具对它们并不一视同仁，Claude Code 默认的 `auto` 通道在 Ghostty 里直接能用，在 iTerm2 里要先在设置里打开转义序列提醒，在 WezTerm 里则一声不吭，直到你把 `preferredNotifChannel` 设成 `terminal_bell` 或者加一个 hook，每种情况的细节在这篇[通知指南](https://kaku.fun/zh/blog/claude-code-notifications)里。

## 重启之后

iTerm2 能恢复窗口，还能在 App 重启时让会话继续活着，Ghostty 通过 `window-save-state` 走 macOS 的窗口恢复，窗口、标签、分屏和工作目录都会回来，WezTerm 自己不恢复会话，一般是加插件，或者靠它的多路复用。

## 发版节奏

iTerm2 和 Ghostty 都在正常发版，WezTerm 最后一个稳定版是 2024 年 2 月的，开发一直在继续，但修复只能通过 nightly 拿到，所以用 WezTerm 要么一直跟 nightly，要么接受一些老 bug。

## 跑 Claude Code 和 Codex

三个在 Claude Code 里都不用设置就能用 `Shift + Enter` 换行，关闭有程序在跑的窗格前也都会确认，所以差别主要在上面说的通知，以及一个长时间的 agent 会话要用得顺手，需要先配多少东西，这部分在[Claude Code 用什么终端](/zh/blog/best-terminal-for-claude-code)里讲得更细。

Kaku 在这里挨着 WezTerm，它是 WezTerm 的分支，保留了 Lua 配置和引擎，把 AI 编程命令行工具用得到的部分配好了，比如 `Cmd + Click` 打开 `path:line`，重启后保留 agent 的最后一屏，并且按正常的 macOS 版本发布，而不是只有 nightly。喜欢 WezTerm 的那套思路，又希望它直接适合 Claude Code 和 Codex 的话，可以试试。

## 常见问题

### Ghostty 比 iTerm2 快吗？

Ghostty 围绕 GPU 渲染来做，一般用着更轻，iTerm2 也用 Metal 渲染，日常工作里两者都够快，真正拉开差距的是功能而不是速度。

### 三个里哪个和 tmux 配合最好？

iTerm2，因为 `tmux -CC` 能把 tmux 窗口变成原生的标签和分屏，在 Ghostty 和 WezTerm 里 tmux 就是普通用法。

### WezTerm 还在维护吗？

还在，GitHub 上开发一直在继续，只是最新的稳定版停在 2024 年 2 月，之后的改动都通过 nightly 发布。

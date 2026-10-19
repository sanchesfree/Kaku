# 终端 shell 集成靠 OSC 把目录和提示符交给终端

> OSC 7、133、9、8 各自告诉终端什么，Kaku 0.25.0 的 fish 和 zsh 实际发哪些，以及怎么用 printf 核对。

发布于 2026-10-17 · Tw93 · https://kaku.fun/zh/blog/shell-integration-osc

在本机的 Mac 上，Kaku 里新开一个标签会落在当前目录，因为终端能读到这个窗格所属进程组的工作目录，停在提示符时那个进程就是 shell 自己。OSC 序列是另一路报告，shell 写出一段很短的转义序列，终端认识它就把数据留下，序列本身不会印出来。Kaku 0.25.0 里，fish 会自己发 OSC 7 报目录，再发 OSC 133 给提示符做标记，zsh 的集成发的是给助手用的 OSC 1337 用户变量，并不发 OSC 7 和 OSC 133。通知走 OSC 9 和 OSC 777，跟这套 shell 集成是两条路，Claude Code 和 Codex 该怎么设写在[通知那篇](/zh/blog/claude-code-notifications)里。

## 终端拿到序列之后做什么

一段 OSC 以 ESC 和 `]` 开头，后面是编号，参数用分号隔开，结尾是 BEL（`\a`）或 ST（`ESC \`）。终端会把整段吃掉。如果回滚里能看见 `]7;file://` 这种字，说明 ESC 这个字节在 Kaku 读到之前就丢了，剩下的就成了普通文本。

Kaku 把每一种序列记在窗格上。OSC 7 写下工作目录，有它的时候优先于从进程读到的目录。OSC 133 把后面的格子标成提示符、输入或输出，也可以记下退出码。OSC 1337 存一个带名字的变量。OSC 9 和 OSC 777 在窗口处于后台时变成一条 macOS 通知。OSC 8 把一段文字标成链接，`Cmd + Click` 会打开它。

![Kaku 把 OSC 7 记成新标签页要用的工作目录，OSC 133 记成提示符区域，OSC 1337 交给助手钩子，OSC 9、OSC 777 和 OSC 8 变成通知或可点击的链接](https://kaku.fun/img/blog/shell-integration-osc.webp)

*终端把每一种序列记成窗格上的状态，本机上如果一直没有 OSC 7，目录还可以从进程本身读到。*

OSC 7 报的是当前目录，[iTerm2 的文档](https://iterm2.com/documentation-escape-codes.html)把它写成 file URL，形如 `file://hostname/path`，等同于它自己的 RemoteHost 加 CurrentDir。[WezTerm](https://wezterm.org/shell-integration.html)用这个 URL 决定新标签开在哪，Kaku 也一样。三项继承开关默认都开着，[配置页](/zh/docs/configuration)上是同一段。

```lua
config.window_inherit_working_directory = true
config.tab_inherit_working_directory = true
config.split_pane_inherit_working_directory = true
```

`Cmd + T` 在这个目录开新标签，`Cmd + D` 和 `Cmd + Shift + D` 在这里分屏，`Cmd + Shift + T` 把刚关掉的标签按它原来的目录重新打开。本机上如果还没有收到 OSC 7，Kaku 会问 macOS（`proc_pidinfo`），进程自己的目录就够用。SSH 过去之后，本机那个进程还停在你敲 `ssh` 的目录里。远程 shell 如果发了 OSC 7，记下的就换成远程路径，但新标签仍是本机的 shell，Kaku 只取 URL 里的路径部分，所以这个标签会去 Mac 上找同名路径。

OSC 133 是 FinalTerm 的提示符标记，[iTerm2 的文档](https://iterm2.com/documentation-escape-codes.html)写了四个。`133 ; A` 是提示符开始，`133 ; B` 是提示符结束、你开始输入，`133 ; C` 是命令输出开始，`133 ; D ; <status>` 是退出码，Kaku 在状态缺失时按 0 读。Kaku 基于 WezTerm，滚到上一个提示符区域的动作叫 `ScrollToPrompt`，[WezTerm 默认没有绑键](https://wezterm.org/config/lua/keyassignment/ScrollToPrompt.html)，Kaku 0.25.0 也没有。iTerm2 自己的安装脚本会在每个提示符旁画一个标记，用 `Cmd + Shift + Up` 和 `Cmd + Shift + Down` 跳，Kaku 不安装那份脚本。

OSC 1337 的 `SetUserVar` 是 iTerm2 的窗格变量，名字是明文，值是 base64。Kaku 的助手听的是这条通道上的 `kaku_last_cmd` 和 `kaku_last_exit_code`，命令失败之后可以给出一条修复，用 `Cmd + Shift + E` 贴回提示符。这和 OSC 133 不是一条通道。`Cmd + L` 打开聊天时，还可以带上上一条命令最多 51 行输出，但要 C 已经记下输出从哪一行开始，并且 D 已经记下一个非零退出码，下一次 `133 ; A` 会把这两项都清掉。fish 会在下一次提示符发 A，却从不发 D，zsh 的文件两个都不发，所以这份集成装上之后，那 51 行是空的。

OSC 9 是 iTerm2 的单行通知，写成 `9 ; message`。OSC 777 是 `777 ; notify ; title ; body`，[WezTerm 的文档](https://wezterm.org/config/lua/config/notification_handling.html)用的就是这个形式。`9 ;` 后面如果跟着数字，比如 `9 ; 4`，那是 ConEmu 的进度命令，Kaku 不当成通知。OSC 8 来自[这份 VTE 和 iTerm2 的提议](https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda)，`8 ; ; URL` 和结尾的 `8 ; ;` 之间的文字会变成链接，哪怕这些字本身不是 URL，`Cmd + Click` 打开它。裸的 URL，以及 `src/main.rs:42` 这种路径，没有 OSC 8 也能点开。

## Kaku 怎么接上 shell

`kaku init` 会写一份托管文件，再让 shell 去加载它。zsh 会在 `~/.zshrc` 末尾加上两行，一行把 `~/.config/kaku/zsh/bin` 放进 `PATH`，另一行是这样。

```bash
[[ -f "$HOME/.config/kaku/zsh/kaku.zsh" ]] && source "$HOME/.config/kaku/zsh/kaku.zsh" # Kaku Shell Integration
```

fish 写的是 `~/.config/fish/conf.d/kaku.fish`，里面再 source `~/.config/kaku/fish/kaku.fish`。`kaku doctor` 会检查这份集成在不在。Starship 和 Smart Tab 只在 Kaku 里启动（`TERM_PROGRAM=Kaku`，或者从 Kaku 的 shell 里拉起的 tmux）。这些文件还加载的插件，写在[不用 Oh My Zsh 的 zsh 配置](/zh/blog/zsh-without-oh-my-zsh)里。

fish 在 `fish_prompt` 里发 OSC 7，内容是 `file://` 接上主机名再接上 `$PWD`，同时发 OSC `133 ; A`。它在 `fish_preexec` 里发 OSC `133 ; C`，不发 B 和 D。两个 shell 都只在 Kaku 的窗格里发 OSC 1337 用户变量，因为启动时会设置 `WEZTERM_PANE`。`TERM` 保持 `xterm-256color`，所以远程主机没有 `kaku` 这份 terminfo 也能连上。变量的值不是命令原文，hook 从 `~/.config/kaku/ai_inline_capability` 读出一个 token，用冒号接上正文，再做 base64。没有这个 token，`SetUserVar` 不会去发起助手请求。`KAKU_AUTO_DISABLE` 会把这些 hook 关掉。在 tmux 里，printf 会套上 tmux 的 passthrough 包装，仍然要打开 `allow-passthrough` 才出得去。

zsh 的文件在 `preexec` 和 `precmd` 里发这些用户变量，不发 OSC 7 和 OSC 133。应用包里还有一份 `kaku.sh`，是给 bash 和 zsh 用的 WezTerm 脚本，它会发 OSC 7、完整的 A/B/C/D 标记，以及 `WEZTERM_PROG`。`kaku init` 不会 source 它，它会在每次提示符前改写 `PS1`，把标记加进去。

## 用 printf 检查

先看目录，从还没待在 `/tmp` 的 zsh 里执行下面这行，fish 会在下一个提示符发自己的 OSC 7，把测试值盖掉。

```bash
printf '\033]7;file://%s/tmp\033\\' "$(hostname)"
```

按 `Cmd + T`，再跑 `pwd`，应该打出 `/tmp`。zsh 自己不发 OSC 7，这个路径会一直留着，直到下一条 OSC 7 到来。发一条值不是 URL 的，解析失败就会把它清掉，新标签又跟着 shell 进程走。

```bash
printf '\033]7;x\033\\'
```

再看提示符标记，Kaku 会在你保存 `~/.config/kaku/kaku.lua` 时重新加载，追加一条绑定就行，如果给 `config.keys` 赋一张新表，默认绑定会全部丢掉。

```lua
table.insert(config.keys, {
  key = 'UpArrow',
  mods = 'SHIFT',
  action = wezterm.action.ScrollToPrompt(-1),
})
```

打两个标记再跳。

```bash
printf '\033]133;A\a'; echo first
printf '\033]133;A\a'; echo second
```

往上滚到 `first` 离开屏幕顶端，按 `Shift + Up`，视口会回到那个标记。fish 本来就会在每个提示符发 A，所以这颗键在 fish 里能在真正的提示符之间跳。zsh 里它只会落到确实有人打过的标记上。

通知要等窗口放到后台再跑。

```bash
printf '\e]9;%s\a' "OSC 9"
printf '\e]777;notify;%s;%s\a' "Build" "OSC 777"
```

`notification_handling` 的默认值是 `AlwaysShow`，在 Kaku 里仍然要求窗口没有焦点。

文字本身不是 URL 的链接可以这样发。

```bash
printf '\e]8;;https://kaku.fun\e\\Kaku\e]8;;\e\\\n'
```

在 Kaku 这个词上 `Cmd + Click`，会打开网站。

## 不生效时怎么看

tmux 自己解析转义序列，只把套了 passthrough 包装的那些转出去，而且要 `~/.tmux.conf` 里有 `set -g allow-passthrough on`。改完用 `tmux source-file ~/.tmux.conf` 重新加载。Kaku 的 hook 会给 OSC 1337 用户变量套上这层包装，fish 的 OSC 7、OSC 133 和上面那几条 printf 没有套，在 tmux 里就停在 tmux 那一层。Kaku 写的 `~/.config/kaku/tmux/kaku.tmux.conf` 打开了鼠标，并保留 `KAKU_SESSION`，没有打开 passthrough。[在 Mac 上用 tmux](/zh/blog/tmux-alternative-mac)仍然适合那种断了 SSH 也要活着的会话，多出来的就是这一行。

空敲一次回车不会把上一次失败再报一遍，退出码只在真正跑过一条命令之后才发送。Ctrl+C 和退出码 0 不会来要修复。`Shift + Up` 如果没反应，视口上方就没有提示符区域，zsh 在有人打出 OSC 133 A 之前通常就是这样。

## 常见问题

### 新标签会跟着 SSH 里的远程目录走吗？

不会。新标签是你 Mac 上的本机 shell，远程 shell 发了 OSC 7 时，Kaku 只留下 URL 里的路径部分，新标签会去 Mac 上找同名路径，没有 OSC 7 就开在 `ssh` 进程所在的目录。

### 为什么屏幕上会出现 `]133;A`？

ESC 这个字节在 Kaku 读到之前就丢了，剩下的字符就按普通文本印了出来。

### 别的程序打一段 OSC 1337，能触发助手的修复吗？

hook 发送 `kaku_last_cmd` 时，会把 `~/.config/kaku/ai_inline_capability` 里的 token 加在命令前面。别的程序打出来的序列没有这个 token，文件不存在时 hook 什么都不发。

### iTerm2 的 Install Shell Integration 是同一套吗？

iTerm2 菜单里的安装会放上它自己的脚本，还会记下命令历史，并能用 scp 下载，Kaku 没有这个菜单，在 Kaku 里跳提示符用的是上面的 `ScrollToPrompt` 绑定。

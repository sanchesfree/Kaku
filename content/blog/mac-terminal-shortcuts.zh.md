Mac 终端里真正省时间的快捷键分在两层，一层归终端 App 管，开标签、分屏、搜索输出和翻滚动区都在这里，Terminal.app、Ghostty 和 Kaku 各有一套。另一层归 shell 管，也就是 Ctrl + A、Ctrl + E、Ctrl + W、Ctrl + U、Ctrl + K、Ctrl + R 和用 Alt 按词移动这些行编辑键，只要把 Option 设成 Meta，换到哪个终端里都一样能用。

## 在哪个终端里都能用的行编辑

zsh 和 bash 默认都是 emacs 模式，所以命令行上怎么移动、怎么删字，跟外面套的是哪个终端没有关系。下面这张表是 macOS 上两个 shell 的默认绑定，可以用 `zsh -fc 'bindkey'` 和 `bash -ic 'bind -p'` 自己核对：

| 按键 | 作用 |
|---|---|
| `Ctrl + A` / `Ctrl + E` | 跳到行首 / 行尾 |
| `Ctrl + W` | 删掉前一个词，bash 里是删到前一个空格 |
| `Ctrl + U` | 删掉整行，bash 里是从光标删到行首 |
| `Ctrl + K` | 从光标删到行尾 |
| `Ctrl + Y` | 把刚删掉的内容贴回来 |
| `Ctrl + _` | 撤销上一步编辑 |
| `Alt + B` / `Alt + F` | 往回 / 往前跳一个词 |
| `Alt + D` | 删掉后一个词 |
| `Alt + Backspace` | 删掉前一个词 |
| `Alt + .` | 插入上一条命令的最后一个参数 |

两个 shell 不一样的地方有两个键。一个是 `Ctrl + U`，zsh 里它是 `kill-whole-line`，光标后面的字也会一起删掉，bash 的 `unix-line-discard` 只删到光标为止。另一个是 `Ctrl + W`，zsh 里它是 `backward-kill-word`，词由字母、数字和 `$WORDCHARS` 里的字符组成。这个变量默认带着 `/`，所以一整段路径按一下就没了，把 `/` 从里面去掉之后就能一段一段删，bash 的 `unix-word-rubout` 则是简单地删到上一个空格。两边来回切的话，其他差别可以看 [zsh 和 bash 的区别](/zh/blog/zsh-vs-bash)。

删掉的内容其实没丢，一条很长的命令敲到一半想先跑点别的，按 `Ctrl + U` 把它收起来，跑完再按 `Ctrl + Y` 就能原样贴回来，相当于给命令行临时找了个地方先放一放。

## Option 当 Meta，为什么 Mac 上 Alt + B 和 Alt + F 不灵

Mac 键盘上其实没有 Alt 键，Option 加字母默认是用来打特殊字符的，美式布局下 Option + B 打出来的是 `∫`，而不是往回跳一个词。所以在终端把 Option 当成 Meta 发出去之前，上面表里所有 `Alt` 开头的行都只会打出一堆怪字符，每个终端的开关放在不同地方。

**Terminal.app**，在 Terminal > Settings > Profiles > Keyboard 里勾上 Use Option as Meta key，或者直接按 `Cmd + Option + O` 给当前窗口切换。Apple 的[快捷键列表](https://support.apple.com/guide/terminal/keyboard-shortcuts-trmlshtcts/mac)里也写了，用 Option + D 往后删一个词，得先打开这个选项才行。

**iTerm2**，在 Settings > Profiles > Keys 里把 Left Option key 设成 Esc+，[iTerm2 文档](https://iterm2.com/documentation-preferences-profiles-keys.html)说大多数人选它就对了。

**Ghostty**，对应的是 [`macos-option-as-alt`](https://ghostty.org/docs/config/reference#macos-option-as-alt)，可以填 `true`、`false`、`left` 或 `right`。不设的时候它看键盘布局决定，美式标准和美式国际布局下是 `true`，其他布局都是 `false`，所以用德语、法语这类布局的人得自己写上：

```
macos-option-as-alt = left
```

只把左边的 Option 当 Alt，右边那个就还能用来打带音标的字母和各种符号，平时要写英文以外语言的人会很需要这一点。Ghostty 其他常用的配置可以看 [Ghostty 配置](/zh/blog/ghostty-config)。

**WezTerm 和 Kaku**，用的是 `send_composed_key_when_left_alt_is_pressed` 和 `send_composed_key_when_right_alt_is_pressed` 这两个键，哪一个设成 `false`，对应那一侧的 Option 就会被当成 Alt 发出去。

## 搜历史命令

最值得学会的一个快捷键是 `Ctrl + R`，它会往回增量搜索历史记录，zsh 里叫 `history-incremental-search-backward`，bash 里叫 `reverse-search-history`。敲几个字母就能找到以前跑过的命令，再按一次 `Ctrl + R` 往更早的匹配翻，看到想要的直接回车执行，不想要了就按 `Ctrl + G`，命令行会恢复成搜索前的样子。

另一种常见的设置是按上方向键做前缀搜索，比如先敲 `git push` 再按上键，就只会在以这几个字开头的命令里翻。zsh 自带这两个 widget 但默认没有绑上，在 `~/.zshrc` 里加下面几行就能打开：

```bash
autoload -U up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search
```

fzf 可以把 `Ctrl + R` 换成一个对整份历史做模糊匹配的列表。

## Terminal.app 的快捷键

Apple 公开了完整的列表，下面挑的是每天都会用到的那些：

| 操作 | 快捷键 |
|---|---|
| 新标签 / 新窗口 | `Cmd + T` / `Cmd + N` |
| 下一个 / 上一个标签 | `Ctrl + Tab` / `Ctrl + Shift + Tab` |
| 把窗口拆成两个面板 | `Cmd + D` |
| 关闭拆分面板 | `Cmd + Shift + D` |
| 查找 / 查找下一个 | `Cmd + F` / `Cmd + G` |
| 跳到上一个 / 下一个标记 | `Cmd + Up` / `Cmd + Down` |
| 清除到开头 | `Cmd + K` |
| 反向搜索命令历史 | `Ctrl + R` |
| 切换 Use Option as Meta key | `Cmd + Option + O` |

里面最容易被忽略的是标记，用 `Cmd + Return` 运行命令时会顺手给这一行打上标记，之后按 `Cmd + Up` 和 `Cmd + Down` 就能在标记之间跳，一大段输出不用再拿触控板一路往上找开头在哪。这份列表里没有在拆分面板之间切换的快捷键，如果想要好几个 shell 并排、还能用键盘来回切和调大小，[Mac 上该选哪个终端](/zh/blog/best-terminal-for-mac)那篇比较过几个选择。

## 用 Option 加方向键按词移动

Option + Left 和 Option + Right 按词跳，是大家从 Mac 输入框里带过来的习惯，Apple 也把它列成了 Terminal.app 的默认行为，但不是每个终端都会给这两个键发 shell 认得的序列。按下去如果没动，反而打出了 `[1;3D` 或 `;3D` 这样的字符，就说明终端发的方向键编码在 shell 里没有对应的绑定，要么在终端里把这两个键改成发 `Esc b` 和 `Esc f`，要么在 zsh 里把这两个编码绑上：

```bash
bindkey '^[[1;3D' backward-word
bindkey '^[[1;3C' forward-word
```

在 Terminal.app 里，按住 Option 再移动鼠标指针，可以把插入点直接放到命令行上任意位置，改一条很长的命令时比按什么键都快。

## Kaku 里的快捷键

Kaku 自带的配置把左边的 Option 当成 Meta，右边的 Option 留给打组合字符，所以 `Alt + B`、`Alt + F` 和 `Alt + .` 第一次打开就能用，不用去设置里找。它还把 Option + Left 和 Option + Right 映射成 `Alt + B` 和 `Alt + F`，Cmd + Left 和 Cmd + Right 映射成 `Ctrl + A` 和 `Ctrl + E`，Option + Backspace 映射成 `Ctrl + W`，Cmd + Backspace 映射成 `Ctrl + U`。Kaku 的 zsh 集成又把 `Ctrl + U` 改绑到了 `backward-kill-line`，所以 Cmd + Backspace 跟 Mac 输入框里一样只删到行首，不会把整行都删掉。上下方向键默认也是前缀搜索，如果 atuin 这类工具已经占了上键，Kaku 就不去动它。

标签、分屏、搜索和 AI 这几块的默认快捷键如下，都是对着自带的按键表和[快捷键文档](/zh/docs/keybindings)核对过的：

| 操作 | 快捷键 |
|---|---|
| 新标签 | `Cmd + T` |
| 切到第 1 到第 9 个标签 | `Cmd + 1` 到 `Cmd + 9` |
| 上一个 / 下一个标签 | `Cmd + Shift + [` / `Cmd + Shift + ]` |
| Tab Navigator | `Cmd + Shift + O` |
| 左右分屏 / 上下分屏 | `Cmd + D` / `Cmd + Shift + D` |
| 在窗格之间移动 | `Cmd + Option + 方向键` |
| 放大当前窗格 | `Cmd + Shift + Enter` |
| 在窗格里搜索 | `Cmd + F` |
| 命令面板 | `Cmd + Shift + P` |
| AI 聊天 | `Cmd + L` |
| 采用 Kaku Assistant 的建议 | `Cmd + Shift + E` |
| AI 设置 | `Cmd + Shift + A` |

跟 agent 一起干活时最好用的是放大那个键，一个窗格跑 Claude Code，另一个窗格跑测试，要看一大段 diff 的时候按 `Cmd + Shift + Enter` 让 agent 那边占满整个窗口，看完再按一次就回到分屏。标签一多，Tab Navigator 可以按名字筛，比数到底是 `Cmd + 6` 还是 `Cmd + 7` 省事得多。想加自己的快捷键，就在 `~/.config/kaku/kaku.lua` 里往 `config.keys` 后面追加，不要整张表重新赋值，否则 Kaku 自带的那些默认快捷键会一起被清掉。

## 常见问题

### 为什么按 Option + B 打出来的是 ∫，而不是往回跳一个词？

因为终端把 Option 当成了打字符的键发出去，在 Terminal.app 里勾上 Use Option as Meta key，在 Ghostty 里设 `macos-option-as-alt`，在 WezTerm 里把 `send_composed_key_when_left_alt_is_pressed` 设成 `false` 就好，Kaku 默认已经给左边的 Option 这样设了。

### Ctrl + U 在 zsh 和 bash 里有什么不同？

zsh 里会删掉整行，光标后面的字也一起删，bash 里只从光标删到行首，两边删掉的内容都能用 `Ctrl + Y` 贴回来。

### 在 Mac 上怎么搜以前跑过的命令？

按 `Ctrl + R` 再敲命令里的一部分，继续按 `Ctrl + R` 往更早的匹配翻，回车执行，`Ctrl + G` 取消，这是 shell 自己的功能，所以在哪个终端里都能用。

### 有没有清屏的快捷键？

Terminal.app 里 `Cmd + K` 是清除到开头，Kaku 里 `Cmd + K` 会把屏幕和滚动区一起清掉。`Ctrl + L` 是 shell 自带的 `clear-screen`，在哪个终端里都能用，它会把提示符重新画到屏幕顶上。

### 既想打带音标的字符，又想把 Option 当 Meta，可以吗？

可以，只让一侧的 Option 当 Meta 就行，Ghostty 里写 `macos-option-as-alt = left`，WezTerm 和 Kaku 里分别设左右两个 `send_composed_key` 选项，Kaku 默认就是左边当 Meta、右边打字符这样分的。

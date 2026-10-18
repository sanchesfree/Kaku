Ghostty 在 Mac 上读的是一个纯文本文件，路径是 `~/.config/ghostty/config.ghostty`，1.2.3 之前的版本叫 `~/.config/ghostty/config`，里面一行一个 `key = value`，改完按 `Cmd + Shift + ,` 就能重新加载，想看全部选项和说明，跑一下 `ghostty +show-config --default --docs` 就行。Ghostty 不写配置也能直接用，所以真正值得改的其实就那几项跟个人口味有关的，字体、主题、窗口外观、快捷键、Option 键和 quick terminal，下面按这个顺序一项项讲。

## 配置文件放在哪

按 2026 年 10 月的[官方配置文档](https://ghostty.org/docs/config)，macOS 上 Ghostty 会去两个地方找配置：

```text
~/.config/ghostty/config.ghostty
~/Library/Application Support/com.mitchellh.ghostty/config.ghostty
```

第一个是 XDG 路径，设了 `$XDG_CONFIG_HOME` 就跟着它走，两个文件可以同时存在，Ghostty 先读 XDG 那份再读 macOS 那份，所以同一个 key 写在 `Application Support` 里的会生效。大多数人只留 `~/.config/ghostty/` 下面这一份，放进 dotfiles 管理也方便，两个都没有的话就跑默认值，而默认值里已经带了 JetBrains Mono 和内置的 Nerd Font 图标。

## 语法和重新加载

每一行就是 key、等号、value，注释用 `#` 开头而且得单独占一行，key 全是小写并且区分大小写，value 加不加引号都行，等号后面留空就是把这个 key 恢复成默认值：

```ini
# ~/.config/ghostty/config.ghostty
font-family = "JetBrains Mono"
background = 282c34
font-family =
```

每个 key 同时也是命令行参数，比如 `ghostty --font-family="JetBrains Mono"`，想试一个值又不想动文件的时候很顺手。配置多了可以用 `config-file` 拆开，相对路径按当前文件所在目录算，前面加个 `?` 表示这个文件可有可无，拿来放每台机器各自不同的设置正合适：

```ini
config-file = ?local.ghostty
```

有一点容易踩坑，`config-file` 是在当前文件读完之后才处理的，所以被引入的文件会盖掉写在 `config-file` 那行后面的同名设置。

`Cmd + Shift + ,` 重新加载配置，想换键就去绑 `reload_config` 这个 action，不过有些选项重载后只对新开的窗口和标签生效，还有几个要整个退出重开才行，官方参考文档在每个选项下面都写了是哪种情况。

## 字体和主题

`ghostty +list-fonts` 会列出 Ghostty 能识别的字体名，`font-family` 写多行就是一条回退链，第一行是主字体，后面几行负责补主字体里没有的字符：

```ini
font-family = "JetBrains Mono"
font-family = "Symbols Nerd Font Mono"
font-size = 14
```

因为重复写是往后追加，主题或者引入的文件里可能藏着你不知道的字体，稳妥的做法是先写一行 `font-family = ""` 把列表清空再重新设。粗体和斜体默认从同一个字体家族里找，除非你单独设了 `font-family-bold` 或 `font-family-italic`，`font-size` 的单位是 point，可以写 `13.5` 这样的半号，图标字体该装哪个可以看 [Nerd Fonts 那篇](/zh/blog/nerd-fonts-mac)。

主题是跟着 app 一起装好的，`ghostty +list-themes` 能看到全部，想跟着 macOS 的深色浅色自动切换，一行里把两个都写上：

```ini
theme = light:Rose Pine Dawn,dark:Rose Pine
```

这种写法里 light 和 dark 两半都得有，顺序无所谓，自己做的主题放进 `~/.config/ghostty/themes/`，配置里再写 `background`、`foreground` 或 `palette` 会盖掉主题里的颜色。主题文件本身也是一份配置，什么选项都能设，所以来路不明的主题文件别随手往里放。

## 窗口边距、标题栏和边框

边距的单位是 point，会跟着屏幕缩放：

```ini
window-padding-x = 12
window-padding-y = 8,4
window-padding-balance = true
```

写两个用逗号隔开的数就是分别设左右或者上下，`window-padding-balance` 会把凑不满一整格的那点余量平均分到四条边上，边距改完只对新开的窗口和标签生效，已经开着的不会变。

macOS 标题栏由 `macos-titlebar-style` 控制，有 `native`、默认的 `transparent`、把标签栏塞进标题栏的 `tabs` 和 `hidden` 四种，`hidden` 去掉标题栏但保留圆角边框，`window-decoration = none` 则是标题栏和边框一起去掉，在 macOS 上连标签也一并没了。想要半透明窗口，把 `background-opacity` 设成 `0.9` 左右再加一行 `background-blur = 20`，这个强度和写 `true` 是一样的，只是 macOS 上改透明度靠重载不管用，得把 Ghostty 整个退出再打开。

## 快捷键

一条绑定写成 `keybind = trigger=action`，修饰键有 `shift`、`ctrl`、`alt`（也可以写 `opt`）和 `super`（也可以写 `cmd`），需要参数的 action 用冒号接上：

```ini
keybind = cmd+shift+d=new_split:right
keybind = ctrl+a>n=new_window
keybind = cmd+k=unbind
```

第二行是一个按键序列，先按 `ctrl+a` 松开再按 `n`，Ghostty 会一直等下一个键，没有超时，第三行的 `unbind` 是把默认绑定拿掉，让这个键原样传给终端里跑着的程序。默认绑定用 `ghostty +list-keybinds --default` 查，全部 action 用 `ghostty +list-actions` 查，细节在[快捷键文档](https://ghostty.org/docs/config/keybind)里。

trigger 前面还能加前缀改变行为，`global:` 让快捷键在 Ghostty 不在前台时也能用，macOS 上要先给它辅助功能权限，`unconsumed:` 执行 action 的同时把按键继续传给程序，`performable:` 只在 action 真能执行时才吃掉按键，比如 `performable:cmd+c=copy_to_clipboard` 在没选中文字时就当没绑过。`keybind = clear` 要慎用，它会把这一行之前的绑定全部清空，默认的也算在内。

## Option 当 Alt 用，以及 shell 集成

Mac 上的 Option 键配合字母会打出 `∫` 这类字符，而不是当 Alt 用，于是 shell 和编辑器里那些 Alt 快捷键就失灵了，`macos-option-as-alt` 管的就是这件事：

```ini
macos-option-as-alt = left
```

写 `true` 是两个 Option 都当 Alt，写 `left` 或 `right` 只改一边，另一边还能留着打带音标的字母。不设的时候默认值看键盘布局，U.S. Standard 和 U.S. International 是 `true`，其他布局都是 `false`，用别的布局的人经常就卡在这里。

shell 集成默认是开的，`shell-integration = detect` 会自动识别 bash、elvish、fish、nushell 和 zsh，它负责上报当前目录，让新标签和新分屏开在同一个文件夹里，给提示符打标记供 `jump_to_prompt` 跳转，停在提示符时关窗口也不再弹确认。具体开哪些功能由 `shell-integration-features` 决定，写成逗号分隔的列表，前面加 `no-` 就是关掉：

```ini
shell-integration-features = no-cursor,ssh-terminfo
```

`ssh-terminfo` 会在缺少 Ghostty terminfo 的远程机器上自动装上，`ssh-env` 则是在远程机器上退回 `xterm-256color`，这两个都是 1.2.0 才加的。

## Quick terminal

quick terminal 是一个从屏幕边上滑出来、盖在当前 app 上面的终端窗口，它没有默认快捷键，要自己用 `global:` 前缀把 `toggle_quick_terminal` 绑上：

```ini
keybind = global:ctrl+backquote=toggle_quick_terminal
quick-terminal-position = top
quick-terminal-size = 40%
quick-terminal-screen = mouse
```

`backquote` 是数字 `1` 左边那个键在 W3C 规范里的名字，位置可以选 `top`、`bottom`、`left`、`right` 或 `center`，macOS 上改位置要重启才生效。macOS 上 `quick-terminal-autohide` 默认是 true，窗口一失去焦点就收起来，想让它一直开着就设成 `false`。

## 把 Ghostty 的配置搬到 Kaku

Kaku 用 Lua 配置，文件在 `~/.config/kaku/kaku.lua`，它先加载自带的默认配置再叠上你写的那几行，保存后会自动重新加载，上面这些设置里有好几项已经默认配好了。默认字体是 JetBrains Mono，中文回退到 PingFang SC，Symbols Nerd Font Mono 是打包在 app 里的，不管你换成什么字体都会排在后面当回退，左 Option 发 Meta、右 Option 照常打组合字符，相当于 Ghostty 的 `macos-option-as-alt = left`，`Cmd + Opt + Ctrl + K` 从屏幕顶部拉下一个 Kaku 窗口，用起来跟 quick terminal 差不多，想换键改 `config.macos_global_hotkey`。新装的 Kaku 默认是 Kaku Dark，配置里没有 `config.color_scheme` 这一行时会跟着 macOS 的深浅色走，在 `kaku config` 里选 Auto 就是帮你设成这样。

剩下的基本可以一行对一行地改过去：

```lua
-- font-family = "Fira Code"
config.font = wezterm.font("Fira Code")
-- font-size = 16
config.font_size = 16
-- background-opacity = 0.92
config.window_background_opacity = 0.92
-- window-padding-x / window-padding-y，单位 point
config.window_padding = { left = '12pt', right = '12pt', top = '8pt', bottom = '8pt' }
-- 对应 goto_split:right 的绑定，往 config.keys 里追加，别整个替换
table.insert(config.keys, {
  key = 'RightArrow', mods = 'CMD|SHIFT',
  action = wezterm.action.ActivatePaneDirection('Right'),
})
```

`window_padding` 用 `pt` 才和 Ghostty 的边距一个意思，直接写数字或者 `px` 是物理像素，在 Retina 屏上会显得小一圈，分屏那几条不用搬，`Cmd + D` 和 `Cmd + Shift + D` 本来就是分屏，另外记得用 `table.insert` 往 `config.keys` 里加，直接给它赋一个新表会把 Kaku 的默认快捷键全部冲掉。三种配置方式具体差在哪，可以看 [Ghostty、iTerm2 和 WezTerm 的对比](/zh/blog/ghostty-vs-iterm2-vs-wezterm)。

## 常见问题

### macOS 上 Ghostty 的配置文件在哪？

在 `~/.config/ghostty/config.ghostty`，1.2.3 之前叫 `~/.config/ghostty/config`，Ghostty 还会读 `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty`，而且是最后读，所以这份里的值优先。

### 怎么重新加载 Ghostty 配置？

按 `Cmd + Shift + ,` 就行，不过边距只对新开的窗口和标签生效，`background-opacity` 和 `quick-terminal-position` 在 macOS 上要整个重启。

### Ghostty 里怎么让 Option 当 Alt 用？

两个键都要就设 `macos-option-as-alt = true`，只要一边就写 `left` 或 `right`，用 U.S. 布局的话默认本来就是 true。

### 怎么看 Ghostty 的全部选项？

跑 `ghostty +show-config --default --docs | less`，快捷键相关的用 `ghostty +list-keybinds --default` 和 `ghostty +list-actions`。

### Ghostty 的配置能直接拿到 Kaku 里用吗？

不能直接用，Kaku 读的是 Lua 而不是 `key = value`，不过大部分选项在 `kaku.lua` 里都能对应成一行，字体回退、Option 键和下拉窗口这几样默认就已经配好了。

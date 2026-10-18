在 Mac 上用 Starship，装好只要三步，`brew install starship`，在 `~/.zshrc` 里加一行 `eval "$(starship init zsh)"`，再开一个新的 shell 就能看到新提示符了。之后所有的定制都写在 `~/.config/starship.toml` 这一个 TOML 文件里，显示哪些模块、每个模块长什么样、用什么颜色都在这里改，也可以直接拿社区的预设当起点。想让它一直够快，要盯的主要是 `scan_timeout` 和 `command_timeout` 这两个超时，以及 Git 相关模块在大仓库里到底干了多少活。

## 安装并启用

[Starship 的安装文档](https://starship.rs/guide/)在 macOS 上给了好几种装法，`cargo install starship --locked`、`port install starship` 和官方安装脚本都行，最省事的还是 Homebrew：

```bash
brew install starship
```

装好之后在对应 shell 的配置文件里加上初始化那一行，放在靠后的位置、语法高亮之前，zsh、bash 和 fish 的写法各不一样：

```bash
# ~/.zshrc
eval "$(starship init zsh)"

# ~/.bashrc
eval "$(starship init bash)"
```

```fish
# ~/.config/fish/config.fish
starship init fish | source
```

开一个新的 shell 提示符就换好了。如果你正好也在重新整理 zsh，Starship 这一行和补全、自动建议、语法高亮之间的先后关系，可以看[不用 Oh My Zsh 配好 zsh](/zh/blog/zsh-without-oh-my-zsh)，这篇就不再重复了。

文档里只写了一个前提条件，终端里要装好并启用一套 [Nerd Font](https://www.nerdfonts.com/)，因为 Git、各种语言和工具的默认符号用的都是这些字形，没有的话提示符里就是一排空方块。不想换掉现在用的字体，也可以只加一份符号回退，做法在 [Mac 上的 Nerd Font](/zh/blog/nerd-fonts-mac) 里讲过。

## 配置文件

Starship 不会自己创建配置文件，第一次要手动建一个：

```bash
mkdir -p ~/.config && touch ~/.config/starship.toml
```

如果你习惯把配置放在 dotfiles 仓库里，可以在初始化那一行之前设好 `STARSHIP_CONFIG`，Starship 就会改去读那个路径：

```bash
export STARSHIP_CONFIG=~/dotfiles/starship.toml
```

下面这份小配置差不多把几个核心概念都用上了：

```toml
"$schema" = 'https://starship.rs/config-schema.json'

add_newline = false

[character]
success_symbol = '[>](bold green)'
error_symbol = '[x](bold red)'

[directory]
truncation_length = 2

[package]
disabled = true
```

`$schema` 这一行让编辑器能按 Starship 的配置 schema 补全键名，写起来少查很多次文档。`add_newline` 这种顶层的键管整个提示符，每个 `[表]` 管一个模块。按[配置文档](https://starship.rs/config/)的说法，模块就是根据当前环境显示信息的一个组件，比如在 Node.js 项目里 `nodejs` 模块会显示当前的 Node.js 版本，任何模块加上 `disabled = true` 就会从提示符里彻底消失。

有几个默认值最好心里有数，以下是 2026 年 10 月核对过的。`add_newline` 默认是 `true`，所以两次提示符之间会空一行，不喜欢就关掉，`directory` 默认截到三层父目录，在 Git 仓库里还会截到仓库根目录，`cmd_duration` 只在命令跑了超过两秒时才出现，对应的是 `min_time = 2_000`。`time` 和 `git_metrics` 默认是关着的，要自己写 `disabled = false` 才会显示。

## 格式字符串

每个模块都有自己的 `format`，整个提示符也有一个，格式字符串里能放三种东西：

- **变量**以 `$` 开头，比如 `git_branch` 模块里的 `$branch`，或者提示符 format 里的 `$git_branch`。
- **文字组**写成 `[文字](样式)`，`'[on](red bold)'` 会打出一个红色粗体的 `on`。
- **条件组**用圆括号包起来，里面的变量全是空的时候整组都不显示，`'(@$region)'` 要么显示 `@us-east-1`，要么什么都没有。

样式就是一小段字符串，像 `'bold fg:27'`、`'fg:green bg:blue'`、`'underline bg:#bf5700'`，写 `''` 就是不加任何样式。`$ [ ] ( )` 这几个符号在格式里有特殊含义，想原样打出来要加反斜杠转义，TOML 里用单引号的字符串需要的转义更少，所以文档里的例子大多用单引号。

提示符默认的 format 是 `$all`，展开后是一长串按固定顺序排好的模块，如果只想挪一个模块、其他保持不变，在 `$all` 后面接着写就行，不用整串重写：

```toml
format = '$all$directory$character'
```

显式写出来的模块不会重复出现，所以这一行的效果是把目录挪到第二行，紧挨着提示符字符。想完全掌控顺序的话，就只列你要的那几个模块：

```toml
format = '$directory$git_branch$git_status$nodejs$python$character'
```

颜色也可以先起个名字再到处用，把 `palette` 设成一个名字，在 `[palettes.<名字>]` 下面定义好颜色，之后任何样式字符串里都能直接写这个颜色名：

```toml
palette = 'mine'

[palettes.mine]
mustard = '#af8700'

[git_branch]
style = 'bold mustard'
```

## 预设

[预设页](https://starship.rs/presets/)收集了社区提交的配置，每一个都链到单独的页面，里面有完整的 TOML 和使用方法，以下是 2026 年 10 月页面上列出的：

| 预设 | 改了什么 |
|---|---|
| Nerd Font Symbols | 所有模块都换成 Nerd Font 符号 |
| No Nerd Fonts | 提示符里完全不用 Nerd Font 符号 |
| Bracketed Segments | 每段用方括号包起来，不用 via、on 这类词 |
| Plain Text Symbols | 符号全换成纯文本，适合没有 Unicode 的环境 |
| No Runtime Versions | 隐藏语言运行时的版本号 |
| No Empty Icons | 找不到对应工具时不显示图标 |
| Pure Prompt | 模仿 Pure 的样子和行为 |
| Pastel Powerline、Tokyo Night、Gruvbox Rainbow、Catppuccin Powerline | Powerline 风格的彩色分段 |
| Jetpack | 偏极简的一款 |

页面上还提到 No Nerd Fonts 会在以后的版本里成为默认。预设不是一个开关，它就是一份写好的 `starship.toml`，换上之后和你自己写的配置没有区别，照样一行行改，所以替换之前先把现在的文件另存一份，后悔了还能换回来。`starship` 自己也能打印内置的预设，`starship preset --list` 列出名字，`starship preset tokyo-night -o ~/.config/starship.toml` 直接写成配置文件。

## 让它保持够快

提示符画出来之前你是没法打字的，所以它里面任何一点慢，每按一次回车都感觉得到，大部分情况下动这三个地方就够了。

`scan_timeout` 限制 Starship 扫描当前目录文件的时间，各个语言模块就是靠这一步判断你是不是在 Node.js 或 Python 项目里，默认是 30 ms。`command_timeout` 限制模块调用的每一条外部命令，比如 `git` 或 `node --version`，默认是 500 ms，在特别大的仓库里 Git 的状态可能要算更久，经常待在这种仓库里就把它调高一点，宁可少显示点信息也不想等的话就保持低一些：

```toml
scan_timeout = 10
command_timeout = 1000
```

大仓库里最花时间的通常是 Git，`git_status` 有个 `ignore_submodules`，打开后子模块里的改动就不再算进去，还有个 `use_git_executable`，让它改用 `git` 命令本身来算状态，而不是用 gitoxide。统计增删行数的 `git_metrics` 默认是关的，不看那两个数字就让它一直关着。平时根本不看的模块，直接写 `disabled = true`，或者干脆不写进 `format`。

排查的时候有几样东西能帮上忙，`starship timings` 会列出当前目录下每个模块花了多久，找慢的那个最快，`starship explain` 会显示每个模块的说明，一眼就知道提示符里每一段是谁画的。警告和错误会写进 `~/.cache/starship/session_${STARSHIP_SESSION_KEY}.log`，每个终端会话一个文件，想换目录的话设 `STARSHIP_CACHE` 就行。

## 右侧提示符

`right_format` 和 `format` 写法完全一样，只是画在右边，默认是空的，把命令耗时和时钟挪过去，左边就能一直保持很短：

```toml
format = '$directory$git_branch$git_status$character'
right_format = '$cmd_duration$time'

[time]
disabled = false
```

这里左边的 format 没有用 `$all`，而是把模块一个个写出来，因为 `$all` 里本来就带了 `cmd_duration` 和 `time`，拆开写才能确定这两个模块只放在右边。

## Kaku 里的 Starship

Kaku 的 shell 配置会在没装 Starship 时用 Homebrew 装上，`kaku init` 和首次打开时都会先问你，但它只在 Kaku 里启动 Starship，从 Kaku 里开的 tmux 会话也算。托管的 `kaku.zsh` 判断的是 `TERM_PROGRAM=Kaku`，或者同时有 `$TMUX` 和 Kaku shell 导出的 `KAKU_SESSION`，fish 那边是同一套判断，其他终端还是你原来的提示符。想让所有终端都用 Kaku 的 Starship，在 `.zshrc` 里 Kaku 那行之前加上 `export KAKU_PROMPT_EVERYWHERE=1`，fish 则在 `config.fish` 里写 `set -gx KAKU_PROMPT_EVERYWHERE 1`。图标也不用另装 Nerd Font，Kaku 自带 Symbols Nerd Font Mono，会接在你设的字体后面当回退。

Kaku 没有另外一份提示符配置，它不设 `STARSHIP_CONFIG`，所以 Starship 读的就是正常的 `~/.config/starship.toml`，Kaku 只在这个文件不存在时才把自己那份拷过去，你已经有的话就不会动。唯一的例外是 Kaku 0.10.0 到 0.22.0 拷过去的那份去掉了图标的旧配置，你的文件要是和它一个字节都没差，Kaku 会换成当前版本，改过的或者是软链接的都原样保留。拷过去的那份就是普通配置，随便改，它用一条很短的显式 `format` 代替了 `$all`，把 `command_timeout` 设成 2000 给大仓库里的 Git 状态留出余量，还给 `git_status` 打开了 `ignore_submodules`。

## 常见问题

### Starship 提示符里为什么全是方块或问号？

终端用的字体里没有这些模块要用的 Nerd Font 字形，装一套 Nerd Font，或者只加一份符号字体当回退，也可以换成 No Nerd Fonts 或 Plain Text Symbols 这两个预设，就不再依赖这些字形了。

### Starship 的配置文件在哪？

在 `~/.config/starship.toml`，Starship 不会自己生成，用 `mkdir -p ~/.config && touch ~/.config/starship.toml` 建一个，想放到别处的话，把 `STARSHIP_CONFIG` 指向那个路径就行。

### 在大仓库里提示符为什么变慢，或者 Git 状态不见了？

大仓库里的 Git 命令很容易超过默认 500 ms 的 `command_timeout`，还是想看到状态就把超时调高，在 `[git_status]` 里写上 `ignore_submodules = true`，再把用不上的模块都关掉。

### 怎么把提示符放到右边？

设置 `right_format`，比如 `right_format = '$cmd_duration$time'`，同时左边的 `format` 不要再用 `$all`，只列出你想留在左边的那几个模块。

### Kaku 会覆盖我的 starship.toml 吗？

不会，Kaku 只在没有 `~/.config/starship.toml`，或者它还是旧版 Kaku 拷过去、一个字节都没改过的那份时才写入，你自己写的配置在 Kaku 里和其他终端里都原样生效。

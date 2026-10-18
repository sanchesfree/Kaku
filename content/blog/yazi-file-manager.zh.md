在 Mac 上用 [Yazi](https://yazi-rs.github.io/)，先 `brew install yazi`，顺手把几个负责预览的命令行工具一起装上，然后敲 `yazi` 打开，按 `q` 退出就行。再把官方文档里那个 `y` 函数放进 shell 配置，退出时 shell 会停在你刚才浏览到的目录，不会弹回原地。剩下的配置都在 `~/.config/yazi/` 下的三个 TOML 文件里，而且只需要写你想改的那几行。

## 安装 Yazi 和预览工具

Yazi 唯一必需的依赖是用来识别文件类型的 `file`，macOS 本来就有。其他都是可选的命令行工具，每装一个就多一种能力，[安装页](https://yazi-rs.github.io/docs/installation)给了一行 Homebrew 命令全部装好（2026 年 10 月核对，文档版本 26.9.1）：

```bash
brew update
brew install yazi ffmpeg-full sevenzip jq poppler fd ripgrep fzf zoxide resvg imagemagick-full font-symbols-only-nerd-font
brew link ffmpeg-full imagemagick-full -f --overwrite
```

每个包管的是什么：

| 包 | 打开的能力 |
|---|---|
| `ffmpeg-full` | 视频缩略图 |
| `sevenzip` | 解压和预览压缩包 |
| `jq` | 预览 JSON |
| `poppler` | 预览 PDF |
| `fd` | 按文件名搜索 |
| `ripgrep` | 按文件内容搜索 |
| `fzf` | 在子目录里快速跳转，要求 0.53.0 以上 |
| `zoxide` | 跳到以前去过的目录，依赖 `fzf` |
| `resvg` | 预览 SVG |
| `imagemagick-full` | 预览字体、HEIC 和 JPEG XL，要求 7.1.1 以上 |
| `font-symbols-only-nerd-font` | 文件类型图标 |

只装 `yazi` 本体也能用，其他的可以等用到了再补，文档里也说某个预览出不来的时候，先把对应工具升到最新版再看，想跟最新代码的话可以用 `brew install yazi --HEAD`。如果图标显示成一个个方块，那是字体的事，可以看 [Mac 上的 Nerd Fonts](/zh/blog/nerd-fonts-mac)。

## 先记住这些键

在任意目录下敲 `yazi`，会看到三栏，左边是上一级目录，中间是当前目录，右边是光标所在文件的预览。按 `F1` 或 `~` 打开帮助，按 `q` 退出，[快速上手](https://yazi-rs.github.io/docs/quick-start)里有完整列表，头一天用下面这些就够了：

| 按键 | 作用 |
|---|---|
| `j` / `k` | 光标下移或上移 |
| `l` / `h` | 进入光标所在目录，或者回到上一级 |
| `g` `g` / `G` | 跳到顶部或底部 |
| `J` / `K` | 预览区向下或向上滚 5 个单位 |
| `Space` | 选中或取消选中当前项 |
| `v` | 进入可视模式，一次选一段 |
| `o` 或 `Enter` | 打开选中的文件 |
| `y` / `x` / `p` | 复制、剪切、粘贴 |
| `d` / `D` | 移进废纸篓，或者直接永久删除 |
| `a` | 新建文件，名字以 `/` 结尾就是新建目录 |
| `r` | 重命名 |
| `.` | 显示或隐藏隐藏文件 |
| `s` / `S` | 用 fd 按文件名搜，或者用 ripgrep 按内容搜 |
| `z` / `Z` | 用 fzf 跳转，或者用 zoxide 跳转 |
| `c` `c` | 复制文件路径 |
| `t` `t` | 在当前目录开一个新标签 |

像 `g` `g` 这样写成两个字母的，是先按一个再按另一个，`d` 只是把文件移进废纸篓，按 `g` `t` 就能进废纸篓把它捞回来，误删了也不慌，`D` 才是真删，这个要留神。平时在 shell 里就用 fzf 的话，`z` 用起来是一样的手感，zsh 那一侧怎么配可以看 [Mac 上在 zsh 里用 fzf](/zh/blog/fzf-zsh-mac)。

## y 这个函数

从 shell 里启动的程序没法改 shell 自己的工作目录，所以直接用 `yazi`，退出后还是回到启动时的地方。Yazi 的办法是 `--cwd-file` 参数，退出时把当前目录写进一个临时文件，再由一个小函数读出来执行 `cd`，快速上手页给的 Bash 和 Zsh 版本是这样的：

```bash
function y() {
  local tmp cwd; tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
  command yazi "$@" --cwd-file="$tmp"
  IFS= read -r -d '' cwd < "$tmp"
  [ "$cwd" != "$PWD" ] && [ -d "$cwd" ] && builtin cd -- "$cwd" || builtin true
  command rm -f -- "$tmp"
}
```

把它放进 `~/.zshrc`，开一个新 shell，以后用 `y` 代替 `yazi` 启动，按 `q` 退出时 shell 就已经在你刚才看的那个目录里了，某次不想换目录就按 `Q` 退出。用 fish 的话同一页上有对应的写法：

```fish
function y
  set tmp (mktemp -t "yazi-cwd.XXXXXX")
  command yazi $argv --cwd-file="$tmp"
  if read -z cwd < "$tmp"; and [ "$cwd" != "$PWD" ]; and test -d "$cwd"
    builtin cd -- "$cwd"
  end
  command rm -f -- "$tmp"
end
```

## 三个配置文件 yazi.toml、keymap.toml、theme.toml

Yazi 从 `~/.config/yazi/` 读[三个配置文件](https://yazi-rs.github.io/docs/configuration/overview)：

- `yazi.toml` 放通用设置
- `keymap.toml` 放快捷键
- `theme.toml` 放配色

默认配置已经编进了发布版里，所以不用把整个文件抄一遍，新建文件、只写你要改的那一项就行，比如想默认显示隐藏文件：

```toml
# ~/.config/yazi/yazi.toml
[mgr]
show_hidden = true
```

快捷键稍微不一样，在 `[mgr]` 下写 `keymap = [...]` 会把默认键位整个换掉，多数时候这不是你想要的，用 `prepend_keymap` 或 `append_keymap` 才是在默认键位上叠加自己的：

```toml
# ~/.config/yazi/keymap.toml
[mgr]
prepend_keymap = [
  { on = "e", run = "open", desc = "Edit or open selected files" },
]
```

完整的默认配置在 [Yazi 仓库](https://github.com/sxyazi/yazi/tree/shipped/yazi-config/preset)的 `shipped` 标签下，改某个键或者某个选项之前，去那里查一下原名最省事。想试一套新配置又不想动现在这套，可以把 `YAZI_CONFIG_HOME` 指到另一个目录：

```bash
YAZI_CONFIG_HOME=~/.config/yazi-alt yazi
```

有一个坑要留意，如果你在这几个文件开头加了给编辑器用的 schema 提示，要写成 `#:schema` 注释，不要写成 `$schema` 键。Kaku 的安装脚本里记着 Yazi 26.5.6 起会拒绝 `$schema` 键，直接启动失败，所以以前好好的配置，升级一次 Yazi 就可能打不开了：

```toml
#:schema https://yazi-rs.github.io/schemas/keymap.json
```

## 打开文件

`o` 和 `Enter` 是打开选中的文件，`O` 是交互式打开，会让你挑用哪个 opener，终端支持的话 `Shift + Enter` 和 `O` 是一样的效果。opener 定义在 `yazi.toml` 的 `[opener]` 下，把文件类型对应到 opener 的那些规则，也能像快捷键一样用 `prepend_*` 和 `append_*` 往上叠，常见的做法是加一个 `edit`，把文本文件交给你的编辑器，等它关掉再回来：

```toml
[opener]
edit = [
  { run = "${EDITOR:-vim} %s", desc = "edit", for = "unix", block = true },
]
```

`block = true` 的意思是 Yazi 把终端让给编辑器，你退出编辑器之后再回到 Yazi。要把路径贴到别的 App 里，`c` `c` 复制完整路径，`c` `d` 复制所在目录，`c` `f` 只复制文件名。

## 在 Kaku 里用 Yazi

[Kaku](https://kaku.fun/docs/features) 的 shell 配置里带了一整套 Yazi 设置，但不自带 Yazi 本体。`kaku init` 在交互式 shell 里会先问你，再用 Homebrew 装上缺的工具，Yazi 也在其中，不过只装 `yazi` 这一个，上面那些预览工具还是要自己补。shell 集成给 zsh 和 fish 都定义了同样的 `y` 函数，按 `Cmd + Shift + Y` 会往当前 pane 里敲一个 `y`，所以按 `q` 退出后，shell 已经停在你选的那个目录里。

`~/.config/yazi/` 下还没有这些文件的时候，Kaku 会写一份起步配置，`yazi.toml` 里把预览栏放宽到 `ratio = [3, 3, 10]`，再加上前面那个 `edit` opener，`keymap.toml` 里把 `e` 和 `o` 绑成打开，`Enter` 改成进入目录，已经有的文件不会去动。Kaku 还装了 `kaku-dark` 和 `kaku-light` 两个 flavor，在 `theme.toml` 里维护一段带标记的 `[flavor]`，跟着当前配色是 Kaku Dark 还是 Kaku Light 走，每次启动 Yazi 前都会对一遍，你自己写了 `[flavor]` 的话 Kaku 会原样保留。它写的都是 `#:schema` 注释，也会把 `theme.toml`、`keymap.toml` 和 `yazi.toml` 里旧的 `$schema` 键改过来，上面说的 26.5.6 那个坑就不用自己处理了。

图片预览要看终端能不能画像素，Kaku 实现了 iTerm2 的内联图片协议和 Kitty 图形协议，后者由 `enable_kitty_graphics` 控制、默认就是开的。在 SSH 的 pane 里按 `Cmd + Shift + R`，Kaku 会用 sshfs 把远端主机的文件挂到 `~/Library/Caches/dev.kaku/sshfs` 下，再在新标签里用 Yazi 打开，前提是装好了 macFUSE 和 sshfs。旁边的 `Cmd + Shift + G` 是 lazygit，可以看 [lazygit 和 delta](/zh/blog/lazygit-and-delta)。

## 常见问题

### 怎么让 Yazi 退出时顺便切换 shell 的目录？

用快速上手页里的 `y` 函数，它给 `yazi` 传 `--cwd-file`，等 Yazi 退出后再执行 `cd`，用 `y` 启动，按 `q` 退出会切换目录，按 `Q` 退出则留在原地。

### PDF、视频或 SVG 为什么预览不出来？

每种预览各靠一个工具，PDF 要 `poppler`，视频缩略图要 `ffmpeg-full`，SVG 要 `resvg`，HEIC 和字体要 `imagemagick-full`，缺哪个装哪个，已经装了的就升到最新版再试。

### Mac 上 Yazi 的配置放在哪里？

在 `~/.config/yazi/` 下，分成 `yazi.toml`、`keymap.toml` 和 `theme.toml` 三个文件，想换一个目录就设置 `YAZI_CONFIG_HOME`。

### 升级之后 Yazi 打不开了，该查什么？

先看三个配置文件开头有没有 `$schema = ...` 这一行，Yazi 26.5.6 起不认这个键，把它改成 `#:schema https://...` 注释就好。

### Kaku 会帮我装 Yazi 吗？

在交互式 shell 里跑 `kaku init`，它会问你要不要用 Homebrew 装，也可以自己 `brew install yazi`。装好后 Kaku 会配好 `y` 函数、`Cmd + Shift + Y`，以及跟着 Kaku Dark 或 Kaku Light 走的主题。

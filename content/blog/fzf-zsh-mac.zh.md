在 Mac 上给 zsh 配 fzf，先 `brew install fzf`，再往 `~/.zshrc` 里加一行 `source <(fzf --zsh)`，开一个新 shell 就有三个快捷键可用，Ctrl+R 搜历史命令，Ctrl+T 把文件和目录贴到命令行上，Alt+C 直接跳进某个目录。前两个装好就能用，Alt+C 在 Mac 上要多一步，得让终端把 Option 键当成 Meta 发出去，而大多数终端默认都没开这个。

## 安装和启用

[fzf](https://github.com/junegunn/fzf) 只有一个二进制文件，在 Mac 上用 Homebrew 装最省事：

```bash
brew install fzf
```

然后在 `~/.zshrc` 里加一行：

```bash
# 启用 fzf 的快捷键和模糊补全
source <(fzf --zsh)
```

`--zsh` 会打印出给 zsh 用的集成脚本，source 之后快捷键和 `**<Tab>` 模糊补全就一起配好了。这个参数只在比较新的 fzf 里才有，shell 报错的话先看一眼 `fzf --version`，再用 `brew update; brew upgrade fzf` 升级，2026 年 10 月我核对时 Homebrew 上的版本是 0.74.5。

只想要其中几个快捷键的话，在同一行里把对应的 `*_COMMAND` 变量设成空字符串，放到 source 之后再设是不起作用的：

```bash
FZF_CTRL_R_COMMAND= FZF_ALT_C_COMMAND= source <(fzf --zsh)
```

## 三个快捷键

**Ctrl+R 搜历史。** 它在历史命令里模糊搜索，选中的那条会贴到命令行上但不会直接执行，再按一次 Ctrl+R 可以在按相关度和按时间排序之间切换，`TAB` 能一次选好几条，Alt+R 进入 raw 模式，匹配项周围的几行也会留在列表里，这时用 Ctrl+N 和 Ctrl+P 只在匹配项之间跳。

**Ctrl+T 找文件。** 它列出当前目录下的文件和目录，把选中的路径贴到光标位置，比如先敲 `vim ` 再按 Ctrl+T，挑完路径就直接落在 vim 后面，列表来自 fzf 自带的 walker，参数是 `--walker file,dir,follow,hidden`，所以隐藏文件也会列出来。

**Alt+C 跳目录。** 它只列目录，用的是 `--walker dir,follow,hidden`，选中哪个就 `cd` 进哪个，在一个层级很深的仓库里找某个子目录时，比一层层敲 `cd` 加 Tab 快不少。

在搜索框里，Ctrl+K 和 Ctrl+J（或者 Ctrl+P 和 Ctrl+N）上下移动，回车确认，Ctrl+C、Ctrl+G 或 Esc 退出。输入默认是模糊匹配，空格分开多个词，`'wild` 是精确匹配，`^music` 匹配开头，`.mp3$` 匹配结尾，`!fire` 排除，想整个切到精确模式就给 fzf 加 `-e`。

同一份集成脚本还带了模糊补全，词尾敲 `**` 再按 Tab 就会弹出 fzf：

```bash
vim **<Tab>      # 当前目录下的文件
cd ~/github/**<Tab>
kill -9 **<Tab>  # 选一个进程
ssh **<Tab>      # 来自 /etc/hosts 和 ~/.ssh/config 的主机
```

## Mac 上的坑：Alt+C 和 Option 键

zsh 眼里的 Alt+C 是 Esc 后面跟一个 `c`，fzf 绑的也是这个序列，可 Mac 上没有 Alt 键，只有 Option，默认情况下 Option 加字母会打出一个 Unicode 字符，美式键盘上 Option+B 打出来的是 `∫`，所以按 Alt+C 只会往命令行里多塞一个符号，什么目录都不会跳。

每个终端都有自己的开关，让 Option 改成先发一个 Esc：

- **Terminal.app**：在 Settings 的 Profiles 里打开 Keyboard，勾上 **Use Option as Meta key**，用键盘切换是 `Cmd+Option+O`，Apple 的[快捷键列表](https://support.apple.com/guide/terminal/keyboard-shortcuts-trmlshtcts/mac)里提到它，是因为 Option+D 删词也要靠这个设置。
- **iTerm2**：在 Settings 的 Profiles 里打开 Keys，把 **Left Option Key** 设成 **Esc+**，[iTerm2 文档](https://iterm2.com/documentation-preferences-profiles-keys.html)说大多数人选 Esc+ 就对了，旧的 Meta 选项会改输入字符的最高位，跟现在的系统不兼容。
- **Ghostty**：在配置文件里写 [`macos-option-as-alt`](https://ghostty.org/docs/config/reference)，不写的时候它看键盘布局，U.S. Standard 和 U.S. International 两种布局下默认就是 true，其他布局默认是 false。

```ini
# Ghostty：只让左边的 Option 当 Alt
macos-option-as-alt = left
```

只把左 Option 改成 Meta 是比较常见的折中，左手按 Alt 系的快捷键，右边的 Option 照样能打带音标的字母和各种符号，Ghostty 的其他配置可以看 [Ghostty 配置指南](/zh/blog/ghostty-config)。

## 用 fd 和 bat 调一调默认行为

自带的 walker 在大多数项目里已经够快，剩下要调的一般就两类，一是跳过 `node_modules` 这类很吵的目录，二是加一个预览窗，每个快捷键都有自己的 `*_OPTS` 变量，写在 source 那一行之前：

```bash
brew install bat tree

# Ctrl+T：跳过构建目录，用 bat 预览文件，Ctrl+/ 切换预览窗
export FZF_CTRL_T_OPTS="
  --walker-skip .git,node_modules,target
  --preview 'bat -n --color=always {}'
  --bind 'ctrl-/:change-preview-window(down|hidden|)'"

# Alt+C：用树形结构预览目录
export FZF_ALT_C_OPTS="
  --walker-skip .git,node_modules,target
  --preview 'tree -C {}'"

# Ctrl+R：Ctrl+Y 把命令复制到剪贴板
export FZF_CTRL_R_OPTS="
  --bind 'ctrl-y:execute-silent(echo -n {2..} | pbcopy)+abort'
  --color header:italic
  --header 'Press CTRL-Y to copy command into clipboard'"

source <(fzf --zsh)
```

如果你平时已经在用 [fd](https://github.com/sharkdp/fd)，想让 fzf 列出来的东西和 fd 一模一样，就把 `**<Tab>` 补全用的两个辅助函数换成 fd，快捷键那边也指过去：

```bash
brew install fd

_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}
_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}
export FZF_CTRL_T_COMMAND='fd --hidden --follow --exclude .git'
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
```

`FZF_DEFAULT_COMMAND`（比如 `fd --type f`）只管直接敲 `fzf` 时列什么，README 里写明了 shell 集成不读它，所以几个快捷键才各有各的变量，想处处生效的选项，比如 `--height 40% --layout reverse --border`，放进 `FZF_DEFAULT_OPTS` 就行。

## 用 fzf-tab 接管所有补全

`**<Tab>` 只有敲了触发符才会出来，[fzf-tab](https://github.com/Aloxaf/fzf-tab) 则把 zsh 整个补全菜单换成 fzf，在 `git checkout `、`kill ` 或者变量名后面直接按 Tab 就是一个模糊列表，它自己不做补全，只是把 zsh 原生补全系统的结果拿来展示，所以你原来那些补全配置大都还能用。

```bash
git clone https://github.com/Aloxaf/fzf-tab ~/.zsh/fzf-tab
```

```bash
autoload -U compinit; compinit
source <(fzf --zsh)
source ~/.zsh/fzf-tab/fzf-tab.plugin.zsh

zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'
```

最后一行是在补全 `cd` 时用 eza 预览目录内容，没装的话 `brew install eza`，或者直接删掉这一行。

最容易出问题的是加载顺序。fzf-tab 要放在 `compinit` 之后，又得在 zsh-autosuggestions、fast-syntax-highlighting 这类会包装 widget 的插件之前，同时它还必须是最后一个绑定 Tab 的，而 fzf 自己的补全也绑了 Tab，所以上面 fzf-tab 排在 `source <(fzf --zsh)` 后面。跑起来之后有两个键值得记一下，Ctrl+Space 多选，`/` 在补很深的路径时可以一路连着补下去，不用插件管理器、其余顺序也都排好的 `.zshrc` 可以参考[不用 Oh My Zsh 配好 zsh](/zh/blog/zsh-without-oh-my-zsh)。

## 在 Kaku 里用 fzf

Kaku 不会帮你装 fzf，也不会替你配。它可选的 Homebrew 引导只装 starship、delta、lazygit 和 yazi，zoxide 只在 fish 下才装，zsh 这边自带的是 zsh-autosuggestions、fast-syntax-highlighting、zsh-completions 和 zsh-z，如果 zoxide 已经定义了 `z`，zsh-z 会自动跳过，所以 `source <(fzf --zsh)` 这一行还是得你自己加。Kaku 里的 Smart Tab 会绑定 Tab，`kaku init` 又是把它的 source 行追加到 `.zshrc` 末尾的，这两件事碰在一起就有个先后问题。我两种顺序都试了一遍，fzf 那行放在 Kaku 那行下面，`**<Tab>` 照常弹出 fzf，其余的 Tab 会交回给 Smart Tab，放在上面的话 Tab 就归 Smart Tab 了，`**` 不再触发 fzf。Ctrl+T、Ctrl+R 和 Alt+C 两种顺序下都还绑在 fzf 上。

要用 fzf-tab，就在 `~/.config/kaku/kaku.lua` 里写 `config.smart_tab_mode = 'off'`，新开的 shell 会带上 `KAKU_SMART_TAB_DISABLE=1`，再把 `compinit`、fzf 那行和 fzf-tab 都放在 Kaku 那行上面，补全已经初始化过的话 Kaku 会跳过自己的 `compinit`，autosuggestions 则排在 fzf-tab 之后加载，正好是 fzf-tab 要求的顺序。Alt+C 在 Kaku 里不用额外设置，自带配置把左 Option 当 Meta 发，右 Option 留着打组合字符。

## 常见问题

### 为什么按 Alt+C 打出一个奇怪的字符，而不是跳目录？

因为终端把 Option 当成了输入字符的修饰键，在 Terminal.app 的 Profiles 里勾上 Use Option as Meta key，在 iTerm2 里把 Left Option Key 设成 Esc+，Ghostty 里写 `macos-option-as-alt = left` 就好了。

### 为什么 fzf 不理我设的 FZF_DEFAULT_COMMAND？

shell 集成本来就不读这个变量，Ctrl+T 要设 `FZF_CTRL_T_COMMAND`，Alt+C 要设 `FZF_ALT_C_COMMAND`，`**<Tab>` 则是定义 `_fzf_compgen_path` 和 `_fzf_compgen_dir` 两个函数。

### 怎么关掉其中一个快捷键？

在 source fzf 的那一行里把对应变量设成空字符串，比如 `FZF_ALT_C_COMMAND= source <(fzf --zsh)`，写到 source 那行后面是不起作用的。

### fzf-tab 会取代 `**<Tab>` 吗？

它管得更宽，每一次 Tab 补全都会走 fzf，不过两者可以并存，把 fzf-tab 放在 `source <(fzf --zsh)` 后面加载，让它成为最后一个绑定 Tab 的插件就行。

### 用 fzf 一定要装 fd 吗？

不用，fzf 自带 walker，不装别的工具也能列文件，`--walker-skip` 也能跳过那几个常见的吵闹目录，只有在你别处已经依赖 fd 的过滤规则、想让 fzf 列出同样的结果时，才值得把 fd 接进来。

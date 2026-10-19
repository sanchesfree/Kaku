# 不用 Oh My Zsh，把 zsh 配得又快又好用

> 用原生 zsh 配好自动建议、语法高亮、补全和 Starship 提示符，讲清楚保持启动快的加载顺序，以及怎么测。

发布于 2026-09-27 · Tw93 · https://kaku.fun/zh/blog/zsh-without-oh-my-zsh

想要一个好用的 zsh，其实不需要 Oh My Zsh，大多数人装它图的那些东西，四个组件就够了。zsh-autosuggestions 根据历史给出灰色的建议，语法高亮在你打字时给命令上色，zsh-completions 补上额外的补全定义，Starship 负责提示符。按正确的顺序直接在 `.zshrc` 里加载，再给补全加上缓存，启动快，也一眼能看懂。这篇给出一份这样的 `.zshrc`，讲清楚顺序为什么重要、怎么测，最后说说 Kaku 是怎么用两行把同一套东西装好的。

## 装好这几个组件

用 Homebrew：

```bash
brew install zsh-autosuggestions zsh-syntax-highlighting zsh-completions starship
```

依赖就这些，没有要更新的框架，启动时也不会跑任何你没要求的东西。

## 按顺序加载的 .zshrc

```bash
# 补全定义要在 compinit 之前放进 fpath
fpath=(${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-completions $fpath)

# 补全缓存最多一天完整检查一次
# (#q...) 需要 EXTENDED_GLOB，不开的话这个判断永远为真
setopt EXTENDED_GLOB
autoload -Uz compinit
if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
  compinit && touch "${ZDOTDIR:-$HOME}/.zcompdump"
else
  compinit -C
fi

# 历史
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_IGNORE_SPACE

# 提示符
eval "$(starship init zsh)"

# 根据历史给建议
source ${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-autosuggestions/zsh-autosuggestions.zsh

# 语法高亮必须放在最后
source ${HOMEBREW_PREFIX:-/opt/homebrew}/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

`HOMEBREW_PREFIX` 由 `brew shellenv` 设置，后面的默认值对应 Apple Silicon 的默认路径，把路径直接写出来而不是调用 `$(brew --prefix)`，每开一个 shell 就少起一个进程。

## 顺序为什么重要

大部分问题由三条规则决定：

- **补全要在 `compinit` 之前。** `compinit` 只扫一次 `fpath`，之后才加进去的，要等下次重建才看得到。
- **大多数时候用 `compinit -C`。** 完整的 `compinit` 会检查每一个补全文件，加上 `-C` 就直接信任缓存的 `.zcompdump`，上面那个判断会在缓存超过 24 小时后完整检查一次，需要时才重建，成功后更新缓存时间，在 M5 Pro 上完整跑一次是 29.3 ms，走缓存是 16.2 ms。`(#q...)` 这个判断只有开了 `EXTENDED_GLOB` 才生效，不开的话这串字符根本不会被当成通配，判断永远为真，每个 shell 都会悄悄完整检查一遍。
- **语法高亮放最后。** 它是靠包住 zsh 行编辑器的 widget 来工作的，在它之后定义的 widget，包括 autosuggestions 的，都不会被高亮，它自己的文档也要求放在最后加载。

## 别猜，测一下

```bash
time zsh -i -c exit
```

想要更稳的数字，用 `hyperfine` 多跑几次：

```bash
brew install hyperfine
hyperfine --warmup 5 'zsh -i -c exit'
```

`zsh -i -c exit` 测的是直到第一个提示符出现前的所有耗时，挂在提示符上的那部分不算，拿来每次对比一处改动正合适，哪个数字突然变大，就注释掉一半再测。

## Kaku 是怎么做的

Kaku 自带这一套，在你的 `.zshrc` 里加两行来加载，一行管 `PATH`，一行 source `~/.config/kaku/zsh/kaku.zsh`，里面带的是 zsh-autosuggestions、fast-syntax-highlighting、zsh-completions，以及用来跳到常去目录的 zsh-z，提示符用 Starship。

![Kaku 的 zsh 配置按顺序分六步：PATH 和 Kaku 检测，用缓存的 init 启动 Starship 提示符，历史和按键，每天最多完整检查一次的 compinit -C，z 和 autosuggestions 以你自己的为准，语法高亮推迟到第一个提示符](https://kaku.fun/img/blog/kaku-zsh-load-order.webp)

*规则和上面一样，多了缓存的提示符 init，以及推迟到第一个提示符的高亮。*

在上面几条规则之外，它还多做了三件事：

- **缓存 Starship 的 init 脚本**，热启动时提示符不用再起额外的进程。
- **把语法高亮推迟**到第一个提示符快要出现的时候，它还是最后一个加载，但不拖慢前面那一段。
- **用 `zcompile` 编译整个文件**，zsh 读的是字节码，不用每次重新解析。

它也会给你自己的配置让路，如果你的 `.zshrc` 已经加载了 autosuggestions、高亮插件，或者 zoxide 这类目录跳转工具，Kaku 就跳过自己那份，补全已经初始化过的话也会跳过 `compinit`。

在 M5 Pro 上用 `hyperfine` 各跑 30 次，空的 `.zshrc` 启动是 10.8 ms，完整的 Kaku 配置是 43.3 ms。

常见的两个顾虑各有一个开关，`KAKU_SKIP_TOOL_BOOTSTRAP=1 kaku init` 只配好 shell，不装那几个可选的 Homebrew 工具，`kaku reset` 会把 Kaku 管理的那几行和文件再删掉，你自己写的东西都留着。

## 常见问题

### Oh My Zsh 慢吗？

要看你加载了多少插件、用的哪个主题，用 `time zsh -i -c exit` 测一下自己的启动时间，再和一份只加载你真正在用的组件的 `.zshrc` 比一比。

### 用 zsh-syntax-highlighting 还是 fast-syntax-highlighting？

两个都会在你打字时给命令行上色，zsh-syntax-highlighting 用的人更多，fast-syntax-highlighting 是另一个项目，有自己的主题，Kaku 带的是后者，不管用哪个，都放在 `.zshrc` 最后。

### zsh 补全为什么不出来？

通常是补全目录在 `compinit` 跑完之后才加进 `fpath`，或者缓存的 `.zcompdump` 比它还旧，把 `fpath` 那行挪到 `compinit` 上面，再跑一次 `rm ~/.zcompdump; exec zsh`。

### Kaku 的 zsh 配置能和我自己的 Starship 配置一起用吗？

可以，Kaku 只在没有 `~/.config/starship.toml`，或者它和 Kaku 0.10.0 到 0.22.0 带的那份一个字节都没差时才写入，你自己写的或软链接的配置不会被改动。

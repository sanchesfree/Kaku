从 macOS 10.15 起，zsh 就是默认的登录 shell，也是默认的交互式 shell，新建的账户同样默认用它，2026 年 10 月核对过。macOS 10.14 和更早的系统默认是 bash，`/bin/bash` 现在仍然可以选，自己敲命令就用 zsh。写脚本时 zsh 跟 Bourne shell（sh）兼容得很好，跟 bash 也大体兼容，只是有几处不一样，可移植的脚本用 sh 写，只有用到 bash 专有语法时才用 bash。

## macOS 10.15 改了什么

Apple 的说明页是[在 Mac 上将 zsh 用作默认 Shell](https://support.apple.com/zh-cn/102360)，开头那几条都出自这一页，旧系统也可以把 zsh 设成默认。

系统里本来就有 `/bin/zsh`，`/bin/bash` 也还能选，账户默认是别的 shell 时去开 bash，macOS 会打出一行提示，说默认的交互式 shell 现在是 zsh。不想看这行提示，把下面这一行写进 `~/.bash_profile` 或 `~/.profile`：

```bash
export BASH_SILENCE_DEPRECATION_WARNING=1
```

## 启动文件、提示符和补全

`.zprofile` 对应 `.bash_profile`，登录时跑，SSH 登录也算，`.zshrc` 对应 `.bashrc`，每开一个新的终端会话就跑一次。bash 文件里给环境变量的 `export`，原样放进 zsh 就能用：

```bash
export MY_SETTING=1
```

如果要在 `.zprofile` 里接着用 POSIX 的 `.profile`，可以写成这样：

```bash
[[ -e ~/.profile ]] && emulate sh -c 'source ~/.profile'
```

zsh 的提示符占位符和 bash 不是一套，上色也不用写 ANSI 转义序列。Apple 那页把 `.bash_profile` 里的这段 bash 提示符：

```bash
export PS1="\[\e[92;40m\]\h\[\e[m\]:\[\e[93m\]\W\[\e[m\] \\$ "
```

换成放在 `.zprofile` 或 `.zshrc` 里的 zsh 提示符：

```bash
export PS1="%10F%m%f:%11F%1~%f \$ "
```

这些占位符和 zsh 的命令行补全怎么写，Apple 让你在终端里看 `man zsh`。想要一份现成的 `.zshrc`，把按历史给建议、语法高亮、额外补全和提示符都配好，可以看[不用 Oh My Zsh 配好 zsh](/zh/blog/zsh-without-oh-my-zsh)。

## 脚本

在 macOS 10.15 或更新的系统上，把 `/var/select/sh` 改成 `/bin/bash`、`/bin/dash` 或 `/bin/zsh`，就可以测跟 Bourne shell 兼容的脚本。这条路径如果指到 bash 以外的 shell，用了 bashism（只有 bash 才有的语法）的脚本可能跑不对。

只测这一次，直接让 zsh 按 sh 跑：

```bash
zsh --emulate sh
```

## 怎么切换 shell

在终端里跑 `chsh -s` 改的是这个账户的默认登录 shell，路径得列在 `/etc/shells` 里，比如 `/bin/zsh`、`/bin/bash`、`/bin/csh`、`/bin/dash`、`/bin/ksh`、`/bin/sh` 或 `/bin/tcsh`。

```bash
chsh -s /bin/zsh
```

要改回 bash：

```bash
chsh -s /bin/bash
```

macOS 13 或更新的系统，从苹果菜单打开系统设置，点用户与群组，在右边的列表里按住 Control 键点按你的用户名或头像，选高级选项，输入用户名和密码，从登录 Shell 菜单里选一个 shell，点「好」。更早的 macOS，从苹果菜单打开系统偏好设置，点用户与群组，点锁形图标，输入用户名和密码，在左边按住 Control 键点按你的用户名，选高级选项，从登录 Shell 菜单里选一个 shell，点「好」。

登录 Shell 菜单改的和 `chsh` 是同一个账户默认值，只想让新的终端窗口和标签页用另一个 shell，这个默认值留着不动。打开终端的设置（更早的系统里叫偏好设置），在通用面板里选 命令（完整的路径），再填一个 `/etc/shells` 里的路径，比如 `/bin/zsh` 或 `/bin/bash`。

## 如果你用 Kaku

Kaku 的 shell 集成是给 zsh 和 fish 做的，`kaku init` 会在 `~/.zshrc` 里加两行，一行管 PATH，一行 source Kaku 的 shell 集成，由它加载 zsh-autosuggestions、fast-syntax-highlighting、zsh-completions 和 zsh-z。`kaku init` 还会问你要不要用 Homebrew 装上 Starship、Delta、Lazygit 和 Yazi。Starship 提示符和 Smart Tab 只在 Kaku 里启动，别的终端还是原来的提示符，`kaku doctor` 会检查 zsh 和 fish 的集成是否正常。

在 bash 里，Kaku 只包了一层 `ssh` 和 `mosh`，远程主机没有 `kaku` 的 terminfo 时退回 `xterm-256color`，zsh 和 fish 里也是同一层包装。想自己在 `.zshrc` 里一样样配起来的话，可以看[不用 Oh My Zsh 配好 zsh](/zh/blog/zsh-without-oh-my-zsh)。

## 常见问题

### macOS 上还能用 bash 吗？

能，`/bin/bash` 列在 `/etc/shells` 里，macOS 10.14 和更早系统的默认 shell 就是它，账户现在用的是别的 shell 时再去开 bash，会看到一行提示，说默认的交互式 shell 现在是 zsh。把 `export BASH_SILENCE_DEPRECATION_WARNING=1` 写进 `~/.bash_profile` 或 `~/.profile`，这行提示就不再出现。

### 怎么把默认 shell 换成 zsh，或者换回 bash？

跑 `chsh -s /bin/zsh` 或 `chsh -s /bin/bash`，路径得在 `/etc/shells` 里，在 macOS 13 或更新的系统上，系统设置里的用户与群组、高级选项、登录 Shell 改的也是同一个配置。只想改新的终端窗口和标签页，就把终端的通用面板设成命令（完整的路径），账户的默认 shell 留着不动。

### `.bash_profile` 和 `.bashrc` 里的设置放哪？

登录时要带上、SSH 连过来也要生效的配置放在 `.zprofile`，它对应 `.bash_profile`，每个新终端会话的设置放在 `.zshrc`，它对应 `.bashrc`。`export` 那几行可以原样抄过去，提示符用的是 zsh 的占位符，所以上面那段 zsh 的 `PS1` 放在 `.zprofile` 或 `.zshrc` 里，其余的看 `man zsh`。POSIX 的 `.profile` 可以用 `emulate sh` 从 `.zprofile` 里 source 进来。

### 怎么拿 sh 测一个脚本？

在 macOS 10.15 或更新的系统上，把 `/var/select/sh` 改成 `/bin/bash`、`/bin/dash` 或 `/bin/zsh` 就可以测脚本，不过这条路径如果不是 bash，用了 bashism 的脚本可能跑不对，单次测试也可以直接跑 `zsh --emulate sh` 让 zsh 按 sh 模拟。

### Kaku 会像配 zsh 那样配 bash 吗？

`kaku init` 配的是 zsh、fish，或者两个都配，zsh 的插件和 Smart Tab 属于 zsh 这边，Starship 提示符给 Kaku 里的 zsh 和 fish 用。bash 的集成会包住 `ssh` 和 `mosh`，远端没有 `kaku` 的 terminfo 时改用 `xterm-256color`，zsh 和 fish 的集成也是这样。

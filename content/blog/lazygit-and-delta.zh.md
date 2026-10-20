Lazygit 加 delta，不离开终端就能把 git 用得又快又顺，lazygit 是一个全屏的 git 界面，暂存一行、修改上一个提交、做 rebase 都只差一个键，delta 给 diff 加上语法高亮、行号，还能标出一行里具体改了哪几个词。用 `brew install lazygit git-delta` 装上，把 git 的 pager 指向 delta，再在 lazygit 的配置里加一行 renderer，让它的 diff 视图也用 delta。这篇就讲这几步，以及审 AI 编程 agent 刚改完的代码时最有用的几个快捷键，按 lazygit 0.66 和 delta 0.20.1 核对过。

## 安装

```bash
brew install lazygit git-delta
```

Homebrew 里的名字是 `git-delta`，写 `delta` 也能装，是它的别名，装好之后的命令叫 `delta`。

## 让 git 用 delta

delta 接过 git 的输出再打印一份更好看的结果，所以是作为 git 的 pager 接进去的：

```bash
git config --global core.pager delta
git config --global interactive.diffFilter 'delta --color-only'
git config --global merge.conflictStyle zdiff3
```

`core.pager` 管的是 `git diff`、`git log -p` 和 `git show`，`interactive.diffFilter` 给 `git add -p` 里的 hunk 上色，`zdiff3` 会在合并冲突里把共同祖先也显示出来，大部分冲突因此更好读。delta 自己的选项写在 `~/.gitconfig` 的 `[delta]` 段里：

```ini
[delta]
    line-numbers = true
    side-by-side = true
```

左右对照需要比较宽的窗口，平时多在窄分屏里干活的话就别开。

## 让 lazygit 用 delta

lazygit 自己的 diff 面板不读 `core.pager`，它用的是配置文件里的一组 diff renderer，配置文件所在的目录可以用 `lazygit --print-config-dir` 查到：

```yaml
git:
  diffRenderers:
    - command: delta --dark --paging=never
```

浅色主题就把 `--dark` 换成 `--light`，`--paging=never` 不能少，因为滚动由 lazygit 自己负责，renderer 也可以列好几个，在 lazygit 里按 `|` 来回切，比如 delta 和 git 原始的输出各一个。

[[figure:lazygit-delta-pipeline|git diff 和 git log -p 通过 core.pager 交给 delta，lazygit 通过 diffRenderers 交给 delta，delta 上好色的输出显示在 Kaku 的窗格里，Cmd+Shift+G 打开 lazygit|两个入口，同一个渲染器。]]

有一个 delta 的选项带不过去，用 `n` 和 `N` 在文件之间跳转的 `navigate`，只有 delta 自己当 pager 时才生效，在 lazygit 里不起作用。

## 最先值得记住的快捷键

| 按键 | 位置 | 作用 |
|---|---|---|
| `space` | Files | 暂存或取消暂存一个文件 |
| `enter` | Files | 打开文件，按行或按 hunk 暂存 |
| `a` | Files | 全部暂存或全部取消 |
| `c` | Files | 提交 |
| `A` | Files | 修改上一个提交 |
| `d` | Files | 丢弃改动 |
| `P` / `p` | 任意位置 | push / pull |
| `z` / `Z` | 任意位置 | 撤销 / 重做 |
| `?` | 任意位置 | 列出当前面板的所有按键 |

## 审 agent 的改动

Claude Code 或 Codex 一口气改了十几个文件之后，提交前真正要看清的是到底改了什么，这件事 lazygit 很擅长：

1. 打开 Files 面板，一个个文件看过去，diff 由 delta 来渲染。
2. 在文件上按 `enter`，只暂存你认可的那些 hunk，其余的留在工作区，让 agent 重做。
3. 不值得留的文件按 `d` 丢掉。
4. 把剩下的提交，反悔了就按 `z`。

## 在 Kaku 里用 lazygit

Kaku 里按 `Cmd + Shift + G` 会在当前窗格、当前目录打开 lazygit，如果一个仓库有没提交的改动，而你还没在这里用过 lazygit，Kaku 会提示一次可以用这个快捷键。lazygit 和 delta 都在 `kaku init` 可以用 Homebrew 帮你装的可选工具里，上面那些 git 和 lazygit 的设置还是要你自己加。

## 常见问题

### 为什么 git 用上了 delta，lazygit 却没有？

lazygit 的 diff 面板是自己渲染的，只认它配置里 `git.diffRenderers` 下列出的 renderer，在那里加上 `- command: delta --dark --paging=never` 就行。

### Mac 上 lazygit 的配置文件在哪？

跑一下 `lazygit --print-config-dir`，Mac 上一般是 `~/Library/Application Support/lazygit` 或 `~/.config/lazygit`，具体读哪个以这条命令为准，单个仓库还可以有自己的 `.git/lazygit.yml`。

### 怎么关掉 delta 的左右对照？

把 `~/.gitconfig` 里 `[delta]` 段的 `side-by-side = true` 删掉，或者改成 `false`。

### brew 包到底叫 delta 还是 git-delta？

正式名字是 `git-delta`，`brew install delta` 通过别名装的是同一个东西，装好的命令都叫 `delta`。

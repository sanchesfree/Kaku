提示符、文件列表和状态栏里的图标，只有终端用的字体里有这个字形才画得出来，没有的话就是一个个空方块或问号。解决办法有两个，一是装一套 [Nerd Font](https://www.nerdfonts.com/)，也就是打过补丁、塞进了几千个图标的编程字体，二是保留你现在的字体，再把只含图标的 Nerd Font 加成回退字体。有些终端自带这份回退，WezTerm、Ghostty 和 Kaku 都是，那就什么都不用装。

## Nerd Font 是什么

[Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) 拿 JetBrains Mono、Fira Code、Hack 这类编程字体，往里面加上几套图标字体的字形，包括 Powerline 符号、Font Awesome、Material Design Icons、Devicons、Octicons、Codicons 等，Starship 这样的提示符、Yazi 和 lazygit 这样的终端工具，还有很多状态栏，画分支、文件夹和语言图标时用的就是这些码位。

这个项目还发布了只含图标的 `SymbolsOnly` 字体，用途是让你保留喜欢的字体，你的字体里缺的字符，终端再去这份符号字体里找。

## 字形缺了会怎样

一个字体只画得出它自己有的字符，缺字的时候终端会顺着回退列表往下找，再去找系统字体，就像在英文字体里打中文照样能显示出来。但 Nerd Fonts 的图标放在私用区，系统字体里都没有，整条链上找不到一个 Nerd Font，最后就只能画成方块。

在 WezTerm 里可以用 `wezterm ls-fonts --text` 加一小段文字，看每个字符是哪个字体画出来的，这是分清到底没装字体还是配置写错最快的办法。

## 装补丁字体

每一套补丁字体都是一个 Homebrew cask，在 Mac 上不加 `--cask` 也能找到：

```bash
brew install font-jetbrains-mono-nerd-font
brew install font-hack-nerd-font
```

补丁版的字体名是原名去掉空格再加上 ` Nerd Font`，JetBrains Mono 就变成 `JetBrainsMono Nerd Font`，终端字体设置里要填的是这个名字，原版的 `JetBrains Mono` 是另一个字体族。不想用 Homebrew 的话，[发布页](https://github.com/ryanoasis/nerd-fonts/releases/latest)上每个字体族都有一个压缩包，解开后双击每个 `.ttf` 安装就行。

## 保留原字体，加一份符号回退

只含图标的那份字体也是 cask：

```bash
brew install font-symbols-only-nerd-font
```

怎么加要看终端。[WezTerm](https://wezterm.org/config/fonts.html) 不需要装，它自带 JetBrains Mono、Nerd Font Symbols 和 Noto Color Emoji，并且会接在你设的字体列表后面：

```lua
config.font = wezterm.font_with_fallback {
  'Fira Code',
  'DengXian',
}
```

[Ghostty](https://ghostty.org/docs/config/reference) 也不需要装，它内嵌了 JetBrains Mono，Nerd Font 图标也是内置的。它的回退是多写几行 `font-family`，第一行是主字体，后面几行补主字体里缺的码位，想换一份别的符号字体，就让它单独占一行，具体名字用 `ghostty +list-fonts` 查，写一行空的 `font-family = ""` 可以清掉文件前面设过的字体。Ghostty 1.2.0 起还有 `adjust-icon-height`，能调 Nerd Font 图标的最大高度，Powerline 和制表符字形不受影响。

README 里也说了，回退来的符号在缩放和位置上不一定对得齐，如果图标和文字放在一起看着有点歪，换成同一字体族的补丁版会更稳。Mac 上 WezTerm 的整套配置可以看 [Mac 版 WezTerm 配置](/zh/blog/wezterm-config-for-mac)。

## Mono、Propo 和默认宽度

每套补丁字体都有三种图标宽度，区别只在图标上，字母本身不变：

| 版本 | 图标宽度 | 什么时候用 |
|---|---|---|
| `Nerd Font` | 尽量做成双宽 | 终端允许图标伸进下一格 |
| `Nerd Font Mono` | 只占一格 | 图标压到文字上，或者让列对不齐了 |
| `Nerd Font Propo` | 按比例 | 在终端外面用，比如编辑器的界面 |

在终端里用 Mono 最稳，每个图标都只占一格，表格和状态栏的列不会乱。

## 选哪个基础字体

以下按 Nerd Fonts README 整理，2026 年 10 月核对过：

| 补丁字体族 | 原字体 | 说明 |
| --- | --- | --- |
| JetBrainsMono Nerd Font | JetBrains Mono | 命名规则和原版一致 |
| FiraCode Nerd Font | Fira Code | 带连字 |
| Hack Nerd Font | Hack | README 自己举的例子 |
| Iosevka Nerd Font | Iosevka | 字窄，一屏放得下更多列 |
| CaskaydiaCove Nerd Font | Cascadia Code | 原名是保留字体名，所以改了名 |

所有图标都能在 [cheat sheet](https://www.nerdfonts.com/cheat-sheet) 里搜到，还能直接复制码位。

## Kaku 里的字体

Kaku 不用另装 Nerd Font，默认字体是 JetBrains Mono，中文用 PingFang SC，同时自带 Symbols Nerd Font Mono，并把它接在你用的字体后面当回退，所以 Starship、lazygit、Yazi 和状态栏的图标第一次打开就能正常显示。

在 `~/.config/kaku/kaku.lua` 里换了字体，这份回退也还在，换成什么字体图标都不会丢：

```lua
config.font = wezterm.font("Fira Code")
```

Kaku 跟着主题调字重这件事只对默认的 JetBrains Mono 生效，你自己设了字体之后，Kaku 就不再去动它的字重。Starship 在内的 shell 那一侧怎么配，可以看[不用 Oh My Zsh 配好 zsh](/zh/blog/zsh-without-oh-my-zsh)。

## 常见问题

### 在 WezTerm 里换了字体，图标还在吗？

在。`wezterm.font_with_fallback` 会把你的字体放在前面，WezTerm 再把自带的回退接在后面，其中就有 Nerd Font Symbols，用 `wezterm ls-fonts` 能看到整条链。

### Nerd Font、Nerd Font Mono 和 Nerd Font Propo 有什么区别？

只差在图标宽度上，普通版允许图标占两格，Mono 每个图标只占一格，Propo 按比例排，在终端里用 Mono 不会压到文字。

### 在 Ghostty 里怎么加符号回退？

不用加，Ghostty 已经内置了 Nerd Font 图标，只有想换一份别的符号字体时，才需要先装好它，用 `ghostty +list-fonts` 查到名字，再在主字体后面加一行 `font-family`。

### 在 Kaku 里需要装 Nerd Font 吗？

不需要，Kaku 自带 Symbols Nerd Font Mono，接在你的字体后面当回退，你在 `kaku.lua` 里自己设的字体也一样。

### Nerd Fonts 没提供的字体能自己打补丁吗？

能，先用 `brew install fontforge` 装好 FontForge，从最新发布里下载 `FontPatcher.zip`，再运行 `fontforge -script font-patcher PATH_TO_FONT --complete`，生成的字体族名是原名加上 ` Nerd Font`。

# 从 iTerm2 或 WezTerm 迁移

哪些会变，哪些能直接带过来，设置该放在哪里。

## 第一次启动

用 `brew install --cask kaku` 安装后先打开一次，Kaku 会在首次启动时生成 `~/.config/kaku/kaku.lua`，字体、主题、标签和 shell 套件都已经设好。`kaku init` 负责 shell 集成，它只在 `~/.zshrc` 里加一行加载 Kaku 的 shell 配置，文件里其他内容不动，还可以顺手装上 Starship、Delta、Lazygit 和 Yazi，装完用 `kaku doctor` 检查一遍。

```bash
brew install --cask kaku
kaku init
kaku doctor
```

## 从 iTerm2 过来

Kaku 没有 Profile 设置窗口，设置都写在 `kaku.lua` 里，常用的几项比如主题、字体和全局快捷键，可以用 `kaku config` 或 `Cmd + ,` 打开设置面板来改。iTerm2 用户最常按的几个快捷键在 Kaku 里是一样的：

| 操作 | Kaku |
| --- | --- |
| 新建标签 | `Cmd + T` |
| 左右分屏 | `Cmd + D` |
| 上下分屏 | `Cmd + Shift + D` |
| 放大 / 还原窗格 | `Cmd + Shift + Enter` |
| 按词左右跳 | `Opt + Left` / `Opt + Right` |
| 在任意 App 里呼出或隐藏 Kaku | `Cmd + Opt + Ctrl + K` |

全局快捷键的用法和 iTerm2 的 Hotkey Window 差不多，可以在 `kaku config` 里改，也可以写 `config.macos_global_hotkey`。关闭窗口时 Kaku 会保存窗口布局，按 `Cmd + Option + Shift + T` 可以打开上一次的布局。

Kaku 默认是 Kaku Dark 主题，WezTerm 内置的配色方案都可以直接按名字用，其中不少比如 Dracula、Solarized、Catppuccin，和 iTerm2 用户常导入的是同一套：

```lua
config.color_scheme = "Catppuccin Mocha"
config.font = wezterm.font('Your Font Name')
config.font_size = 16
```

## 从 WezTerm 过来

Kaku 基于 WezTerm，用的是同一套 Lua 配置，不过它读的是 `~/.config/kaku/kaku.lua`，不会去找 `~/.wezterm.lua`。这个文件会先加载 Kaku 自带的默认配置，把想保留的 WezTerm 设置复制到 `-- User overrides:` 下面就行，`wezterm` 已经引入好了：

```lua
-- User overrides:
config.font_size = 15
config.window_background_opacity = 0.95

table.insert(config.keys, {
  key = 'RightArrow',
  mods = 'CMD|SHIFT',
  action = wezterm.action.ActivatePaneDirection('Right'),
})
```

快捷键要往 `config.keys` 里追加，不要直接赋一个新表，那样会把 Kaku 的默认快捷键清掉。Kaku 有些默认值和 WezTerm 不一样，比如 `line_height = 1.28`，想要 WezTerm 那样的行高就设成 `config.line_height = 1.0`，其他设置照着 WezTerm 的 Lua 文档写就可以。

## 接下来

[上手指南](https://kaku.fun/zh/docs/guide)讲日常怎么用，[配置](https://kaku.fun/zh/docs/configuration)列出了 Kaku 的全部设置，[对比](https://kaku.fun/zh/compare)把 Kaku 和 iTerm2、Warp、Ghostty、WezTerm 放在一起看。

---

Source: https://kaku.fun/zh/docs/migrate
Site index for LLMs: https://kaku.fun/llms.txt

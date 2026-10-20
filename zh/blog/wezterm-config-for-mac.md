# 一份实用的 Mac 版 WezTerm 配置，以及 Kaku 改了什么

> 在 macOS 上最值得改的 WezTerm 设置，从字体、行高到快捷键和渲染，以及 Kaku 选了哪些默认值、为什么。

发布于 2026-09-28 · Tw93 · https://kaku.fun/zh/blog/wezterm-config-for-mac

一份好用的 Mac 版 WezTerm 配置只需要十几行，一个带中文回退的字体，稍微加大一点的行高，左 Option 当 Meta 发出去，标题栏按钮放进标签栏，配色跟着系统走，再换成 Metal 渲染。配置文件是 `~/.wezterm.lua`，一段返回一张表的 Lua 脚本，每次保存 WezTerm 都会重新加载。Kaku 是 WezTerm 的分支，自带一整份配置。还在 WezTerm、Ghostty 和 iTerm2 之间犹豫的话，可以先看 [Ghostty、iTerm2 和 WezTerm 怎么选](/zh/blog/ghostty-vs-iterm2-vs-wezterm)。

## 从 config_builder 开始

```lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()

-- 设置写在这里

return config
```

`config_builder()` 返回的表会在你拼错选项名时报出来，而不是悄悄忽略，下面所有设置都写在这两行中间。

## 字体和间距

```lua
config.font = wezterm.font_with_fallback {
  'JetBrains Mono',
  'PingFang SC',
}
config.font_size = 15
config.line_height = 1.15
config.harfbuzz_features = { 'calt=0', 'clig=0', 'liga=0' }
```

- **`font_with_fallback`** 对每个字符按顺序挨个字体试，中文和日文会落到 PingFang SC 上，而不是让 macOS 随便挑一个。
- **`line_height`** 大于 1.0 会在行与行之间加空隙，长输出读起来更舒服，但框线字符和方块字符会跟着行一起拉高，二维码和字符画都会变高。
- **`harfbuzz_features`** 关掉连字，喜欢把 `=>` 画成箭头的话就别加这行。

## 让按键用起来像 Mac

```lua
config.send_composed_key_when_left_alt_is_pressed = false
config.send_composed_key_when_right_alt_is_pressed = true

config.keys = {
  { key = 'd', mods = 'CMD', action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' } },
  { key = 'd', mods = 'CMD|SHIFT', action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' } },
}
```

前两行把两个 Option 键分开用，左 Option 当 Meta 发出去，shell、Vim 和 Emacs 里的 `Alt` 快捷键才能用，右 Option 照样能打出 `é` 和 `€` 这类字符。后面的按键表加上了 iTerm2 风格的分屏，`Cmd + D` 和 `Cmd + Shift + D`。

## 窗口

```lua
config.window_decorations = 'INTEGRATED_BUTTONS|RESIZE'
config.window_padding = { left = 16, right = 16, top = 16, bottom = 0 }
config.native_macos_fullscreen_mode = true
```

`INTEGRATED_BUTTONS` 把红黄绿三个按钮放进标签栏，不再单独占一条标题栏，`native_macos_fullscreen_mode` 用的是 macOS 自己那种独占一个桌面的全屏，而不是 WezTerm 的无边框全屏。

## 深色和浅色

WezTerm 可以问 macOS 现在是什么外观，配色就能跟着走：

```lua
local function scheme_for(appearance)
  if appearance:find 'Dark' then
    return 'Builtin Solarized Dark'
  end
  return 'Builtin Solarized Light'
end

config.color_scheme = scheme_for(wezterm.gui.get_appearance())
```

外观一变配置就会重新加载，所以 macOS 在深浅色之间切换时，终端也跟着切。

## 渲染

```lua
config.front_end = 'WebGpu'
config.webgpu_power_preference = 'LowPower'
config.max_fps = 60
```

WezTerm 默认的前端是 OpenGL，`WebGpu` 在 Mac 上走 Metal 渲染，`LowPower` 在有两块显卡的机器上优先用集成显卡。

## Kaku 替你设好了什么

Kaku 保留了 WezTerm 的引擎和 Lua API，上面这些设置在 Kaku 里同样能用，不同的是起点，你的 `~/.config/kaku/kaku.lua` 会先加载 Kaku 自带的那份配置，再把你在下面写的内容叠上去。

![三层配置：kaku.lua 里你自己的覆盖最后生效，下面是 Kaku 自带配置，包含字体、按键和 1.28 行高，再下面是 WezTerm 的默认值](https://kaku.fun/img/blog/kaku-config-layers.webp)

*只写你想不一样的地方，其余都来自自带的那一层。*

这篇讲的大部分东西，自带的那一层已经有了：

| 设置 | Kaku 默认值 |
|---|---|
| 字体 | JetBrains Mono，中日韩文字用 PingFang SC |
| 字号 | 17，低分辨率屏幕上是 15 |
| `line_height` | 1.28 |
| 连字 | 关闭 |
| 左 / 右 Option | Meta / 组合字符 |
| 分屏 | `Cmd + D` / `Cmd + Shift + D` |
| 窗口 | 按钮放进标签栏，40px 内边距，低分辨率屏上 26px，原生全屏 |
| 标签栏 | 在底部，只有一个标签时隐藏 |
| 配色 | Kaku Dark 和 Kaku Light |
| 渲染 | WebGpu，LowPower，60 fps |

被问得最多的是行高，1.28 比大多数终端都宽松，代价是二维码、`neofetch` 的 logo 这类字符画会高出大约 28%，介意的话覆盖掉就行：

```lua
config.line_height = 1.1
```

新装的 Kaku 默认是 Kaku Dark，想跟着 macOS 外观走，就在 `kaku config` 里选 Auto，思路和上面那个配色函数一样。

## 把 WezTerm 配置搬过来

把你在意的设置复制到 `kaku.lua` 里 `-- User overrides:` 那一行下面，别整个文件覆盖掉，这样自带的那一层还会加载。没写的设置用的是 Kaku 的值而不是 WezTerm 的，大多数时候这正是你想要的，不过如果哪里看着和以前不一样，可以先从这一点查起。

## 常见问题

### Mac 上 WezTerm 的配置文件在哪？

`~/.wezterm.lua`，或者 `~/.config/wezterm/wezterm.lua`，也可以用环境变量 `WEZTERM_CONFIG_FILE` 指定一个路径。

### WezTerm 会自动重新加载配置吗？

会，保存文件时就重新加载，出错的话会弹一个带行号的窗口，上一份能用的配置继续生效。

### WezTerm 里怎么让 Option 当 Alt 用？

设 `send_composed_key_when_left_alt_is_pressed = false`，右边那个键如果从来不用来打带重音的字符，也可以一样设。

### 我的 WezTerm 配置能在 Kaku 里用吗？

Kaku 用的是 WezTerm 的配置系统，大多数 macOS 设置都能写在 `kaku.lua` 里，Windows 专用选项已经弃用，不会生效。把设置写在 `-- User overrides:` 下面，Kaku 的默认值就还会在底下加载。

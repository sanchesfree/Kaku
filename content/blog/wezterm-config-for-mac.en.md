A good WezTerm config for Mac only needs a dozen lines: a font with a CJK fallback, a little extra line height, the left Option key sent as Meta, integrated title bar buttons, a color scheme that follows the system, and the Metal renderer. The file is `~/.wezterm.lua`, it is a Lua script that returns a table, and WezTerm reloads it every time you save. This post walks through those settings one group at a time, then shows which of them Kaku already sets for you, since Kaku is a WezTerm fork that ships with a full config of its own.

## Start from config_builder

```lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()

-- settings go here

return config
```

`config_builder()` gives you a table that warns about misspelled options instead of silently ignoring them. Everything below goes between those two lines.

## Fonts and spacing

```lua
config.font = wezterm.font_with_fallback {
  'JetBrains Mono',
  'PingFang SC',
}
config.font_size = 15
config.line_height = 1.15
config.harfbuzz_features = { 'calt=0', 'clig=0', 'liga=0' }
```

- **`font_with_fallback`** tries each font in order for every character, so Chinese or Japanese text falls through to PingFang SC instead of whatever macOS picks.
- **`line_height`** above 1.0 adds space between rows. It makes long output easier to read, but box drawing and block characters stretch with the row, so QR codes and ASCII art get taller.
- **`harfbuzz_features`** turns off ligatures. Leave this out if you like `=>` drawn as an arrow.

## Keys that behave like a Mac

```lua
config.send_composed_key_when_left_alt_is_pressed = false
config.send_composed_key_when_right_alt_is_pressed = true

config.keys = {
  { key = 'd', mods = 'CMD', action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' } },
  { key = 'd', mods = 'CMD|SHIFT', action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' } },
}
```

The first two lines split the Option keys: left Option is sent as Meta, so `Alt` shortcuts in the shell, Vim and Emacs work, while right Option still types characters like `é` and `€`. The key table adds iTerm2-style splits on `Cmd + D` and `Cmd + Shift + D`.

## The window

```lua
config.window_decorations = 'INTEGRATED_BUTTONS|RESIZE'
config.window_padding = { left = 16, right = 16, top = 16, bottom = 0 }
config.native_macos_fullscreen_mode = true
```

`INTEGRATED_BUTTONS` puts the traffic lights into the tab bar instead of a separate title bar. `native_macos_fullscreen_mode` uses the macOS fullscreen with its own Space, rather than WezTerm's borderless one.

## Light and dark

WezTerm can ask macOS for the current appearance, so the color scheme can follow it:

```lua
local function scheme_for(appearance)
  if appearance:find 'Dark' then
    return 'Builtin Solarized Dark'
  end
  return 'Builtin Solarized Light'
end

config.color_scheme = scheme_for(wezterm.gui.get_appearance())
```

Because the config reloads when the appearance changes, switching macOS between light and dark switches the terminal too.

## Rendering

```lua
config.front_end = 'WebGpu'
config.webgpu_power_preference = 'LowPower'
config.max_fps = 60
```

WezTerm's default front end is OpenGL. `WebGpu` renders through Metal on a Mac, and `LowPower` asks for the integrated GPU on machines that have two.

## What Kaku sets for you

Kaku keeps WezTerm's engine and Lua API, so all of the settings above work in Kaku too. The difference is where you start. Your `~/.config/kaku/kaku.lua` first loads Kaku's bundled config, then applies whatever you write below it.

[[figure:kaku-config-layers|Three layers: your overrides in kaku.lua are applied last, on top of Kaku's bundled config with its fonts, keys and 1.28 line height, which sits on WezTerm's defaults|Write only what you want different; everything else comes from the bundled layer.]]

Most of this post is already in that bundled layer:

| Setting | Kaku default |
|---|---|
| Font | JetBrains Mono, with PingFang SC for CJK |
| Size | 17, or 15 on a low resolution screen |
| `line_height` | 1.28 |
| Ligatures | Off |
| Left / right Option | Meta / compose characters |
| Splits | `Cmd + D` / `Cmd + Shift + D` |
| Window | Integrated buttons, 40px padding, native fullscreen |
| Tab bar | At the bottom, hidden with one tab |
| Colors | Kaku Dark and Kaku Light |
| Rendering | WebGpu, LowPower, 60 fps |

The line height is the one people ask about. 1.28 is roomier than most terminals, and the cost is that character-cell graphics such as QR codes and `neofetch` logos come out about 28% taller. If that bothers you, override it:

```lua
config.line_height = 1.1
```

New installs start in Kaku Dark. Choose Auto in `kaku config` to follow the macOS appearance instead, the same idea as the color scheme function above.

## Bringing a WezTerm config over

Copy the settings you care about into `kaku.lua` below the `-- User overrides:` line, not over the whole file, so the bundled layer still loads. Settings you leave out keep Kaku's value, not WezTerm's, which is usually what you want, but worth knowing if something looks different from before.

## FAQ

### Where is the WezTerm config file on Mac?

`~/.wezterm.lua`, or `~/.config/wezterm/wezterm.lua`. WezTerm also accepts a path in the `WEZTERM_CONFIG_FILE` environment variable.

### Does WezTerm reload its config automatically?

Yes, when the file is saved. Errors show up in a window with the line number, and the last working config stays active.

### How do I make Option work as Alt in WezTerm?

Set `send_composed_key_when_left_alt_is_pressed = false`. Do the same for the right key if you never type accented characters with it.

### Can I use my WezTerm config in Kaku?

Yes, Kaku uses WezTerm's configuration system, so any WezTerm option works in `kaku.lua`. Put your settings below `-- User overrides:` so Kaku's defaults still load underneath.

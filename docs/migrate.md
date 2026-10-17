# Migrate from iTerm2 or WezTerm

What changes, what carries over, and where your settings go.

## First Run

Install with `brew install --cask kaku` and open it once. Kaku creates `~/.config/kaku/kaku.lua` on first launch, with fonts, themes, tabs and the shell suite already set. `kaku init` sets up shell integration: it adds one line to `~/.zshrc` that loads Kaku's shell setup and leaves the rest of the file alone, and can install Starship, Delta, Lazygit and Yazi. `kaku doctor` checks the result.

```bash
brew install --cask kaku
kaku init
kaku doctor
```

## From iTerm2

Kaku has no profile window. Settings live in `kaku.lua`, and `kaku config` or `Cmd + ,` opens a settings panel for the common ones: theme, font, global hotkey and more. The shortcuts iTerm2 users reach for most already match:

| Action | Kaku |
| --- | --- |
| New tab | `Cmd + T` |
| Split vertical | `Cmd + D` |
| Split horizontal | `Cmd + Shift + D` |
| Zoom / unzoom pane | `Cmd + Shift + Enter` |
| Jump word left / right | `Opt + Left` / `Opt + Right` |
| Show or hide Kaku from any app | `Cmd + Opt + Ctrl + K` |

The hotkey works like an iTerm2 hotkey window and can be changed in `kaku config` or with `config.macos_global_hotkey`. Window layouts are saved when you close a window, and `Cmd + Option + Shift + T` reopens the last one.

Kaku starts in Kaku Dark. WezTerm's built-in color schemes are available by name, and many of them, such as Dracula, Solarized and Catppuccin, come from the same collection iTerm2 users import:

```lua
config.color_scheme = "Catppuccin Mocha"
config.font = wezterm.font('Your Font Name')
config.font_size = 16
```

## From WezTerm

Kaku is built on WezTerm and uses the same Lua configuration, but it reads `~/.config/kaku/kaku.lua` and never looks at `~/.wezterm.lua`. That file loads Kaku's bundled defaults first; copy the settings you want from your WezTerm config below `-- User overrides:`, where `wezterm` is already required:

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

Append to `config.keys` instead of assigning a new table, which would erase Kaku's default shortcuts. Kaku's defaults differ from WezTerm's in places, for example `line_height = 1.28`; set `config.line_height = 1.0` to get WezTerm's row height back. The WezTerm Lua reference applies to everything else.

## Next Steps

The [Guide](https://kaku.fun/docs/guide) walks through daily use, [Configuration](https://kaku.fun/docs/configuration) lists every Kaku setting, and [Compare](https://kaku.fun/compare) sets Kaku next to iTerm2, Warp, Ghostty and WezTerm.

---

Source: https://kaku.fun/docs/migrate
Site index for LLMs: https://kaku.fun/llms.txt

# Nerd Fonts on Mac: Install Them or Use a Symbols Fallback

> Why prompts and TUIs show boxes instead of icons, how to install a patched Nerd Font with Homebrew, and when a symbols-only fallback is enough.

Published 2026-10-08 · Tw93 · https://kaku.fun/blog/nerd-fonts-mac

Icons in a prompt, a file listing or a status line only show up when the terminal has a font that contains them, and when it does not, you get empty boxes or question marks. There are two fixes: install a [Nerd Font](https://www.nerdfonts.com/), a programming font patched with thousands of icons, or keep your font and add the symbols-only Nerd Font as a fallback. Some terminals, WezTerm, Ghostty and Kaku among them, already ship that fallback, so there is nothing to install.

## What Nerd Fonts are

[Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) takes a programming font such as JetBrains Mono, Fira Code or Hack and adds glyphs from several icon fonts: Powerline symbols, Font Awesome, Material Design Icons, Devicons, Octicons, Codicons and a few more. Prompts like Starship, file managers like Yazi and lazygit, and many status lines use those code points for branch, folder and language icons.

The project also publishes `SymbolsOnly` fonts that contain just the icons. They exist so you can keep the font you like and let the terminal fall back to the symbols for anything your font lacks.

## When a glyph is missing

A font draws only the characters it contains. When it lacks one, the terminal walks its fallback list and then the system fonts, the same way a Chinese character typed in a Latin font still appears. An icon in the Nerd Fonts private-use range is not in any system font, so with no Nerd Font anywhere in the chain, it renders as a box.

In WezTerm, you can see which font supplied each character with `wezterm ls-fonts --text` followed by a short string, which is the quickest way to tell a missing font from a misconfigured one.

## Install a patched font

Every patched family is a Homebrew cask, and on a Mac, Homebrew finds it without the `--cask` flag:

```bash
brew install font-jetbrains-mono-nerd-font
brew install font-hack-nerd-font
```

The patched family name is the original name with spaces removed, plus ` Nerd Font`, so JetBrains Mono becomes `JetBrainsMono Nerd Font`. That is the name to put in your terminal's font setting; the upstream `JetBrains Mono` is a different family. If you would rather not use Homebrew, the [release page](https://github.com/ryanoasis/nerd-fonts/releases/latest) has an archive per family, and you install the fonts by double-clicking each `.ttf`.

## Keep your font and add a symbols fallback

The symbols-only font is also a cask:

```bash
brew install font-symbols-only-nerd-font
```

How you add it depends on the terminal. [WezTerm](https://wezterm.org/config/fonts.html) does not need it, because it bundles JetBrains Mono, Nerd Font Symbols and Noto Color Emoji and appends them after whatever list you set:

```lua
config.font = wezterm.font_with_fallback {
  'Fira Code',
  'DengXian',
}
```

[Ghostty](https://ghostty.org/docs/config/reference) does not need it either, because it embeds JetBrains Mono and has built-in Nerd Font symbols. Fallback there uses repeated `font-family` lines: the first value is the main face and later values fill the code points it lacks, so if you want a different symbols font, it goes on its own line. `ghostty +list-fonts` prints the exact name to use, and an empty `font-family = ""` clears any families set earlier in the file. Since Ghostty 1.2.0, `adjust-icon-height` changes the maximum height of Nerd Font icons without touching Powerline and box-drawing glyphs.

The Nerd Fonts README notes that scaling and placement of fallback symbols can be hit or miss, so if icons look slightly off next to your text, a patched font of the same family is the more consistent choice. A Mac WezTerm setup is covered in [WezTerm on Mac](/blog/wezterm-config-for-mac).

## Mono, Propo and the default width

Each patched family comes in three icon widths, and the difference is the icons, not the letters:

| Variant | Icon width | Use it when |
|---|---|---|
| `Nerd Font` | Double-width where possible | Your terminal lets icons overflow into the next cell |
| `Nerd Font Mono` | Single cell | Icons overlap text or break column alignment |
| `Nerd Font Propo` | Proportional | You use the font outside a terminal, in an editor UI |

In a terminal, Mono is the safe default: every icon stays in one cell, so tables and status lines keep their columns.

## Which base font

Checked October 2026 against the Nerd Fonts README:

| Patched family | Upstream | Note |
| --- | --- | --- |
| JetBrainsMono Nerd Font | JetBrains Mono | Same name pattern as upstream |
| FiraCode Nerd Font | Fira Code | Ligatures included |
| Hack Nerd Font | Hack | The README's own example |
| Iosevka Nerd Font | Iosevka | Narrow, fits more columns |
| CaskaydiaCove Nerd Font | Cascadia Code | Renamed because of a reserved font name |

The [cheat sheet](https://www.nerdfonts.com/cheat-sheet) lets you search every icon and copy its code point.

## Fonts in Kaku

Kaku needs no Nerd Font install. Its default font is JetBrains Mono with PingFang SC for Chinese, and it ships Symbols Nerd Font Mono and adds it as a fallback after whatever font you use, so Starship, lazygit, Yazi and status line icons render on first launch.

That fallback stays in place when you change the font in `~/.config/kaku/kaku.lua`, so you can pick any face and still keep the icons:

```lua
config.font = wezterm.font("Fira Code")
```

Kaku's theme-aware font weights only apply to the default JetBrains Mono stack, so once you set your own font, Kaku stops adjusting its weight. The shell side of the setup, Starship included, is in [zsh without Oh My Zsh](/blog/zsh-without-oh-my-zsh).

## FAQ

### Does WezTerm keep icon glyphs after I set my own font?

Yes. `wezterm.font_with_fallback` puts your faces first, and WezTerm appends its default fallback, which includes Nerd Font Symbols. `wezterm ls-fonts` prints the chain.

### How do Nerd Font, Nerd Font Mono and Nerd Font Propo differ?

Only in icon width. The plain variant lets icons be double-width, Mono keeps each icon in one cell, and Propo uses proportional widths. In a terminal, Mono avoids overlapping text.

### How do I add a symbols fallback in Ghostty?

You do not need one, because Ghostty has built-in Nerd Font symbols. To use a different symbols font, install it, run `ghostty +list-fonts` to get its name, and add it as a second `font-family` line after your main font.

### Do I need a Nerd Font in Kaku?

No. Kaku ships Symbols Nerd Font Mono as a fallback after your font, including a font you set yourself in `kaku.lua`.

### Can I patch a font Nerd Fonts does not ship?

Yes. Install FontForge with `brew install fontforge`, download `FontPatcher.zip` from the latest release, and run `fontforge -script font-patcher PATH_TO_FONT --complete`. The new family is named after the original plus ` Nerd Font`.

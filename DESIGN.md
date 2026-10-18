# Kaku Static Website Design

## Visual Theme

Kaku shares the Kami parchment system used across the family sites (mole.fit and kin) so the apps read as one series. Warm parchment page surface, ink-blue accents, serif type, restrained hairline rules, and dark terminal/screenshot surfaces only where the product needs them. Avoid decorative grids, heavy shadows, oversized marketing type, and card-heavy composition.

## Palette

- `#f5f4ed` parchment page background (`--paper`)
- `#faf9f5` elevated and card surface (`--paper-elev` / `--paper-card`)
- `#141413` primary ink text (`--ink`); `#3d3d3a` dim, `#6b6a64` muted
- `#1B365D` ink-blue brand and actions (`--brand`); `#2D5A8A` hover (`--brand-light`); `#EEF2F7` tint
- `#0d7d4d` green for command-success accents only
- `#141318` terminal canvas (`--term`); `#e7e4d9` terminal text
- `#d8d5c8` warm line/divider (`--line`); `#e5e3d8` soft line (`--line-soft`)

## Typography

Serif-first, matching the family. English pages use Charter with Georgia / Palatino fallbacks; Chinese pages use `TsangerJinKai02`, `Source Han Serif SC`, then `Songti SC`. Body, headings, and small labels (eyebrows, captions, nav) all share the serif; `--ui` is an alias of `--serif`, and labels are never uppercased. Reading copy is 17px, secondary copy 16px, labels and meta 13 to 15px, with nothing under 12px outside code. Monospace (`JetBrains Mono`) is for terminal prompts, code snippets, and the version tag. Do not add a font CDN by default.

## Components

Buttons are pill-shaped (999px radius), at least 44px tall, with a filled ink-blue primary or an ink-blue outline secondary. Cards are parchment blocks with hairline borders and no decorative shadows. Terminal windows keep dark chrome but no extra visual effects.

## Layout

The chrome aligns with the mole-mac (Kami) site so the two feel like one series:

- A top eyebrow strip, not a sticky nav bar: wordmark plus version (mono) on the left, Docs plus the language toggle plus GitHub/X icons on the right, in small serif.
- A left-aligned big-serif hero (`Kaku` with the `書` orbit glyph and a blur-in rise), a serif tagline, and a single dotted trust row in place of stat and tag clutter.
- Sections separated by generous vertical rhythm (96px) rather than divider lines; only the hero keeps a bottom rule.
- A footer that carries the `Kaku · 書` serif wordmark and an italic ethos line. Because Kaku is a multi-page doc site, the footer keeps its Product / Docs / Community / Project link columns rather than collapsing to mole's single-page colophon.

Inner content widths stay close to the blog: about 760px for prose and 1120px for page sections.

Sidebar-less prose pages (`/about`, `/compare`, `/contact`, `/privacy`) reuse the docs chrome, `page-hero doc-hero` plus `article.doc-content`, with `.prose-doc` spanning the same width as the page hero so the intro and body share one right edge. The comparison page stays the durable home for alternative-intent queries.

## Blog

`/blog` and `/zh/blog` follow mole.fit's blog on Kaku's tokens: an index of parchment cards with the cover flush on top, and an article page with the page hero (breadcrumb, title, date and reading time), a cover cropped to 16:7 on desktop and 16:9 on phones, a 760px prose column, one quiet install card, and three related posts. Search intent picks the topics, and every post opens with the direct answer before Kaku's part.

- **Covers** are illustrations from an image model (the Codex CLI's image tool), not screenshots: matte paper cutouts on `#F5F4ED` parchment, navy `#1B365D`, pale grey-blue `#DCE3EE` and `#EEF2F7`, off-white, at most one small muted green `#0D7D4D` accent, with no text, logos, real UI or window chrome. Keep the subject between y 100 and 800 of the 1600x900 canvas, measured with a threshold mask rather than `-trim` because the paper grain defeats it. Convert with `magick in.png -resize 1600x900^ -gravity center -extent 1600x900` and `cwebp -q 86`.
- **Diagrams** explain a mechanism only. Each one is data in `scripts/build_blog_diagrams.py`, drawn as a desktop layout and a stacked `-mobile` layout in JetBrains Mono, saved at 2x and shown at their own width up to the column, so a narrow diagram is never stretched. Labels stay English and short; the caption carries the explanation in each language.

## Agent surface

The site serves a machine-readable twin of itself so AI agents do not have to scrape the HTML:

- **Markdown twins.** Every content page has a `.md` sibling. `scripts/build_markdown.py` generates them from the HTML, so never hand-edit a generated `.md`. The two homepage twins, `index.md` and `zh/index.md`, are the exception: they are hand written, because the landing page is marketing layout rather than prose. `vercel.json` serves markdown on `Accept: text/markdown` for `/` and `/zh`, aliases `/llms.md` to `/index.md`, and sets `Vary: Accept`.
- **Page feed.** `scripts/build_feed.py` emits `feeds/pages.jsonl`, one schema.org `WebPage` per page, indexed by `schemamap.xml` and announced by the `Link: rel="describedby"` response header. Keep `Schemamap:` out of `robots.txt`: Search Console flags it as a syntax error, and every sitemap submitted while it was there stayed "Couldn't fetch" (2026-10-15).
- **Release feed.** `scripts/build_releases.py` writes `feed.xml`, `feeds/releases.json`, and the English and Chinese changelog pages from stable GitHub releases. Nightly builds are not included. Do not hand-edit those files.
- **Hand-maintained.** `llms.txt` (plus the scoped `docs/llms.txt` and `zh/llms.txt`), `agent.json` (served at `/?mode=agent`), and `.well-known/agent-skills/index.json`. Keep the version number, CLI surface, and docs list in these in step with the docs when they change.
- **JSON-LD.** The homepages carry a `@graph` with `SoftwareApplication`, `Organization`, `WebSite`, and a `WebPage` with `speakable`. Every other content page carries `BreadcrumbList` plus `TechArticle`. New pages need both, and a `<link rel="alternate" type="text/markdown">` in `<head>`.

Kaku has no public API, SDK, or standalone cloud terminal. Optional remote access connects browsers to a running Mac through a relay. Do not add OpenAPI specs, OAuth metadata, MCP server cards, or `auth.md`: they would describe endpoints that do not exist.

## Verification

Verify with a static server, desktop screenshot, 375px mobile screenshot, and link checking across Chinese and English pages before pushing. Generated files must be current:

```bash
python3 scripts/build_markdown.py --check
python3 scripts/build_feed.py --check
python3 scripts/build_releases.py --check
```

Routing and header behavior (`Accept` negotiation, `?mode=agent`, `Link`, `Vary`) can only be exercised with `vercel dev`, and `vercel dev` ignores the `has` property, so the two `has`-based rewrites are confirmed only on a real deployment.

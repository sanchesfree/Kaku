#!/usr/bin/env python3
"""Generate the NLWeb schema feed (feeds/pages.jsonl) from the site's HTML.

One schema.org WebPage object per line, built from each page's <title>,
<meta name="description">, canonical URL, and language. schemamap.xml lists
this feed and the Link response header announces it.

    python3 scripts/build_feed.py
    python3 scripts/build_feed.py --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEED = ROOT / "feeds" / "pages.jsonl"
SKIP = {"404.html"}


def meta(html: str, name: str) -> str:
    m = re.search(rf'<meta name="{name}" content="([^"]*)"', html)
    return m.group(1) if m else ""


def build() -> str:
    rows = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.split("/")[-1] in SKIP or rel.startswith("scripts/"):
            continue
        html = path.read_text(encoding="utf-8")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        lang = re.search(r'<html lang="([^"]+)"', html)
        if not canonical:
            print(f"warning: {rel} has no canonical link, skipped", file=sys.stderr)
            continue
        url = canonical.group(1)
        rows.append(
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "@id": url,
                "url": url,
                "name": (title.group(1).strip() if title else ""),
                "description": meta(html, "description"),
                "inLanguage": lang.group(1) if lang else "en",
                "isPartOf": {"@type": "WebSite", "@id": "https://kaku.fun/#website"},
                "encoding": {
                    "@type": "MediaObject",
                    "encodingFormat": "text/markdown",
                    "contentUrl": re.sub(r"/$", "/index", url) + ".md",
                },
            }
        )
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without writing")
    args = parser.parse_args()

    text = build()
    if args.check:
        if not FEED.exists() or FEED.read_text(encoding="utf-8") != text:
            print("feeds/pages.jsonl is stale, run scripts/build_feed.py", file=sys.stderr)
            return 1
        print(f"page feed up to date ({text.count(chr(10))} entries)")
        return 0

    FEED.parent.mkdir(exist_ok=True)
    FEED.write_text(text, encoding="utf-8")
    print(f"wrote {FEED.relative_to(ROOT)} ({text.count(chr(10))} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

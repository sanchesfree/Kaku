#!/usr/bin/env python3
"""Date the next queued blog post with today's date and rebuild the blog.

Run once a day by the scheduled workflow. A day that already has a post, or an
empty queue, changes nothing, so a rerun or a missed day never publishes two
posts at once. Prints the slug it published, or nothing.

    python3 scripts/publish_next_post.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_blog import SRC, today  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    path = SRC / "index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    now = today().isoformat()
    if any(p.get("date") == now for p in data["posts"]):
        return 0
    queued = [p for p in data["posts"] if not p.get("date")]
    if not queued:
        return 0
    queued[0]["date"] = now
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for script in ("build_blog.py", "build_feed.py"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True, stdout=subprocess.DEVNULL)
    print(queued[0]["slug"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

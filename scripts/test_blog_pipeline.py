#!/usr/bin/env python3
"""Exercise daily publishing in a disposable git checkout, never the real queue."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent


class BlogPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "site"
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
        for relative in tracked.stdout.decode().split("\0"):
            if not relative:
                continue
            source = ROOT / relative
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target, follow_symlinks=False)
        # Keep the fixture independent of how far the production queue has run.
        queue_path = self.root / "content/blog/index.json"
        queue = json.loads(queue_path.read_text())
        for index, post in enumerate(queue["posts"]):
            post["date"] = "2026-10-17" if index == 0 else None
            post.pop("modified", None)
        queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n")
        for name in ("sitemap.xml", "sitemap-index.xml", "schemamap.xml"):
            path = self.root / name
            path.write_text(re.sub(r"<lastmod>[^<]+</lastmod>", "<lastmod>2026-10-17</lastmod>", path.read_text()))
        self.script("build_blog", day="2026-10-17")
        self.script("build_feed", day="2026-10-17")
        self.run_cmd("git", "init", "-q")
        self.commit("2026-10-17")

    def run_cmd(self, *args, day="2026-10-18", success=True):
        env = dict(os.environ, BLOG_TODAY=day, GIT_AUTHOR_DATE=day + "T12:00:00+08:00",
                   GIT_COMMITTER_DATE=day + "T12:00:00+08:00",
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        result = subprocess.run(args, cwd=self.root, env=env, capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def script(self, name, *args, **kwargs):
        return self.run_cmd(sys.executable, "scripts/" + name + ".py", *args, **kwargs)

    def commit(self, day):
        self.run_cmd("git", "add", "-A")
        self.run_cmd("git", "-c", "user.name=Blog Test", "-c", "user.email=blog@example.invalid",
                     "commit", "-qm", "fixture", day=day)

    def test_two_days_and_same_day_rerun(self):
        for day, slug in (("2026-10-18", "claude-code-notifications"),
                          ("2026-10-19", "codex-cli-setup")):
            with self.subTest(day=day):
                self.assertEqual(self.script("publish_next_post", day=day).stdout.strip(), slug)
                for name in ("build_blog", "build_markdown", "build_feed", "highlight"):
                    self.script(name, "--check", day=day)
                self.script("check_sitemap", day=day)
                self.commit(day)
                self.script("check_sitemap", day=day)
                self.assertEqual(self.script("publish_next_post", day=day).stdout, "")
                self.assertEqual(self.run_cmd("git", "status", "--porcelain").stdout, "")
        posts = json.loads((self.root / "content/blog/index.json").read_text())["posts"]
        self.assertEqual(sum(bool(p["date"]) for p in posts), 3)

    def test_feed_markdown_targets(self):
        self.script("build_feed")
        rows = [json.loads(line) for line in (self.root / "feeds/pages.jsonl").read_text().splitlines()]
        for row in rows:
            target = urlsplit(row["encoding"]["contentUrl"]).path.lstrip("/")
            with self.subTest(url=row["url"]):
                self.assertTrue((self.root / target).is_file(), target)

    def test_changed_page_still_requires_its_own_date(self):
        with (self.root / "about.html").open("a") as page:
            page.write("\n<!-- fixture change -->\n")
        self.commit("2026-10-18")
        result = self.script("check_sitemap", success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("older than", result.stdout + result.stderr)

    def test_changed_article_still_requires_its_own_date(self):
        with (self.root / "content/blog/best-terminal-for-claude-code.en.md").open("a") as post:
            post.write("\nA changed article.\n")
        self.commit("2026-10-18")
        result = self.script("check_sitemap", success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("best-terminal-for-claude-code lastmod", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

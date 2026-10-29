"""Smoke tests: the site builds and every page exists. Run with `python -m unittest`."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build  # noqa: E402

EXPECTED_PAGES = [
    "index.html",
    "404.html",
    "blog/index.html",
    "cv/index.html",
    "coding/index.html",
    "creative/index.html",
    "static/css/style.css",
]


class FrontMatterTest(unittest.TestCase):
    def test_split_front_matter(self):
        meta, body = build.split_front_matter("---\ntitle: Hi\n---\nBody text")
        self.assertEqual(meta, {"title": "Hi"})
        self.assertEqual(body.strip(), "Body text")

    def test_no_front_matter(self):
        self.assertEqual(build.split_front_matter("Just text"), ({}, "Just text"))


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "site"

    def tearDown(self):
        self.tmp.cleanup()

    def test_all_pages_are_built(self):
        build.SiteBuilder(self.out).build()
        for page in EXPECTED_PAGES:
            self.assertTrue((self.out / page).is_file(), f"missing {page}")

    def test_posts_with_body_get_a_page(self):
        build.SiteBuilder(self.out).build()
        for post in build.load_posts(build.CONTENT_DIR / "blog"):
            page = self.out / "blog" / post.slug / "index.html"
            self.assertEqual(page.exists(), post.has_page, post.slug)

    def test_base_path_prefixes_links(self):
        build.SiteBuilder(self.out, base_path="/my-site").build()
        html = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/my-site/static/css/style.css"', html)
        self.assertIn('href="/my-site/blog/"', html)


if __name__ == "__main__":
    unittest.main()

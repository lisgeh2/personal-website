#!/usr/bin/env python3
"""Build the static personal website.

Content lives in ``content/`` (YAML + Markdown), layout in ``templates/``
(Jinja2), and assets in ``static/``. Running this script renders everything
into ``_site/``, ready to be served by any static host (e.g. GitHub Pages).

Usage:
    python build.py                  # build into _site/
    python build.py --serve          # build, then preview on localhost:8000
    python build.py --base-path /my-repo   # when hosted under a sub-path
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import http.server
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
OUTPUT_DIR = ROOT / "_site"

FRONT_MATTER_DELIMITER = "---"


# --------------------------------------------------------------------------- #
# Content model
# --------------------------------------------------------------------------- #

@dataclass
class Post:
    """A blog entry: either a written thought or a paper note."""

    slug: str
    title: str
    date: dt.date
    kind: str = "thought"  # "thought" or "paper"
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    html: str = ""
    # Paper-specific metadata (optional).
    authors: str = ""
    venue: str = ""
    paper_url: str = ""
    pdf: str = ""  # optional downloadable version, path relative to the site root

    @property
    def has_page(self) -> bool:
        """Entries without a body only link out (e.g. a quick paper pointer)."""
        return bool(self.html.strip())


def load_yaml(path: Path) -> dict | list:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def split_front_matter(text: str) -> tuple[dict, str]:
    """Split a Markdown file into (metadata, body)."""
    if not text.startswith(FRONT_MATTER_DELIMITER):
        return {}, text
    _, meta, body = text.split(FRONT_MATTER_DELIMITER, 2)
    return yaml.safe_load(meta) or {}, body


def load_post(path: Path) -> Post:
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    date = meta.pop("date", None)
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)
    if date is None:
        raise ValueError(f"{path.name}: front matter needs a 'date'")
    if "title" not in meta:
        raise ValueError(f"{path.name}: front matter needs a 'title'")
    html = markdown.markdown(body, extensions=["fenced_code", "tables", "footnotes", "md_in_html"])
    return Post(slug=path.stem, date=date, html=html, **meta)


def load_posts(directory: Path) -> list[Post]:
    posts = [load_post(p) for p in directory.glob("*.md") if not p.name.startswith("_")]
    return sorted(posts, key=lambda post: post.date, reverse=True)


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

class SiteBuilder:
    def __init__(self, output_dir: Path, base_path: str = ""):
        self.output_dir = output_dir
        self.base_path = base_path.rstrip("/")
        self.site = load_yaml(CONTENT_DIR / "site.yaml")
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.globals.update(site=self.site, url=self.url, year=dt.date.today().year)
        self.env.filters["date"] = lambda d, fmt="%B %-d, %Y": d.strftime(fmt)

    def url(self, path: str) -> str:
        """Prefix an absolute site path with the deployment base path."""
        return f"{self.base_path}/{path.lstrip('/')}"

    def render(self, template: str, out_path: str, **context) -> None:
        target = self.output_dir / out_path
        target.parent.mkdir(parents=True, exist_ok=True)
        html = self.env.get_template(template).render(**context)
        target.write_text(html, encoding="utf-8")

    def build(self) -> None:
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        shutil.copytree(STATIC_DIR, self.output_dir / "static")

        posts = load_posts(CONTENT_DIR / "blog")
        thoughts = [p for p in posts if p.kind == "thought"]
        papers = [p for p in posts if p.kind == "paper"]

        self.render("home.html", "index.html", page="home", recent_posts=posts[:3])
        self.render("blog_index.html", "blog/index.html", page="blog",
                    thoughts=thoughts, papers=papers)
        for post in posts:
            if post.has_page:
                self.render("post.html", f"blog/{post.slug}/index.html", page="blog", post=post)

        cv = load_yaml(CONTENT_DIR / "cv.yaml")
        if cv.get("pdf") and not (ROOT / cv["pdf"]).is_file():
            cv["pdf"] = None  # hide the download button until the PDF exists
        self.render("cv.html", "cv/index.html", page="cv", cv=cv)

        for kind in ("coding", "creative"):
            data = load_yaml(CONTENT_DIR / f"{kind}.yaml")
            self.render("projects.html", f"{kind}/index.html", page=kind,
                        heading=data["heading"], intro=data.get("intro", ""),
                        projects=data.get("projects", []))

        self.render("404.html", "404.html", page="404")
        print(f"Built site with {len(posts)} blog entries -> {self.output_dir}")


def serve(directory: Path, port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving on http://127.0.0.1:{port}  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--serve", action="store_true", help="preview the site locally after building")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--base-path", default="", help="URL prefix, e.g. /personal-website")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    SiteBuilder(args.output, base_path="" if args.serve else args.base_path).build()
    if args.serve:
        serve(args.output, args.port)


if __name__ == "__main__":
    main()

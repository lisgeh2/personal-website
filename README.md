# Personal website

A small, readable personal website built by a **Python static-site generator**.
It's plain HTML and CSS. The only JavaScript is the animated
[Vanta.js](https://www.vantajs.com/) "NET" background on the home page.

| Page              | URL          | Edit this file              |
|-------------------|--------------|-----------------------------|
| Home              | `/`          | `content/site.yaml`         |
| Blog (thoughts + papers) | `/blog/` | `content/blog/*.md`     |
| CV                | `/cv/`       | `content/cv.yaml`           |
| Coding projects   | `/coding/`   | `content/coding.yaml`       |
| Creative projects | `/creative/` | `content/creative.yaml`     |

## Quick start



```bash
pip install -r requirements.txt
python build.py --serve      # http://127.0.0.1:8000
```

Pushing to `main` builds and deploys the site to GitHub Pages automatically
(see `.github/workflows/deploy.yml`). Enable it once under
**Settings → Pages → Source: GitHub Actions**.

## Project layout

```
build.py              # the generator: loads content, renders templates, writes _site/
content/              # ← everything you edit lives here
  site.yaml           #   name, tagline, LinkedIn/GitHub links, navigation
  cv.yaml             #   CV sections and skills
  coding.yaml         #   coding projects (title, description, url, year)
  creative.yaml       #   creative projects
  blog/               #   one Markdown file per post
    _TEMPLATE.md      #   copy this to start a new post
templates/            # Jinja2 HTML layouts (base.html is shared by every page)
  macros.html         #   small reusable components (icons, links, list rows, page header)
static/
  css/style.css       # all styles; colours are CSS variables at the top
  js/background.js    # Vanta.js background (home page only)
  files/              # downloadable files (cv.pdf shows a "Download PDF" link on the CV page)
tests/                # smoke tests: python -m unittest discover -s tests
```

## Common tasks

- **Write a blog post:** copy `content/blog/_TEMPLATE.md` to `content/blog/my-post.md`.
  The file name becomes the URL (`/blog/my-post/`). Set `kind: thought` or `kind: paper`.
  If a paper entry has no body text, the list links straight to its `paper_url`.
- **Add a project:** add an entry to `coding.yaml` or `creative.yaml`.
- **Change colours/fonts:** edit the variables in the `:root` block at the top of `style.css`.
  The Vanta net uses `--hero-accent` and `--hero-bg`.
- **Tweak the animation:** change the options in `static/js/background.js`.
  Visitors who set "reduce motion" get a static gradient instead.
- **Add a new page:** create a template in `templates/`, add one `self.render(...)` line in
  `SiteBuilder.build()`, and add it to `nav` in `site.yaml`.

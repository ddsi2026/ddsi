#!/usr/bin/env python3
"""
DDSI Tech Hub Blog Builder
==========================

Turns markdown files in blog/content/*.md into styled HTML pages that match
the main site's navy & gold design, plus a blog/index.html listing page.

HOW TO ADD A NEW PODCAST EPISODE (or any blog post):
  1. Copy blog/content/episode-01.md to a new file, e.g. episode-02.md
  2. Fill in the frontmatter (between the --- lines) and the show notes below it
  3. Drop the cover image into blog/images/
  4. Run:  python3 build_blog.py
  5. Commit/upload the newly generated .html files alongside index.html

No other setup needed - this script has no dependencies beyond the
`markdown` and `pyyaml` packages (pip install markdown pyyaml).
"""

import re
import sys
from pathlib import Path
from datetime import date

try:
    import markdown as md
    import yaml
except ImportError:
    sys.exit("Missing dependencies. Run: pip install markdown pyyaml --break-system-packages")

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
OUTPUT_DIR = ROOT

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.DOTALL)

PAGE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<script id="Cookiebot" src="https://consent.cookiebot.com/uc.js" data-cbid="93786d8f-7512-427c-b471-567cafb2d65c" data-blockingmode="auto" type="text/javascript"></script>
<title>{title} | D&amp;D Strategic Impact</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet" />
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --navy: #0b1322; --navy-mid: #121e33; --navy-light: #1a2a44;
    --gold: #c9a84c; --gold-light: #e8c97a; --gold-dim: #8a6e2f;
    --slate: #9aafc8; --slate-light: #d4dde8; --white: #f5f2ec;
    --font-display: 'Cormorant Garamond', Georgia, serif;
    --font-body: 'DM Sans', sans-serif;
  }}
  body {{ background: var(--navy); color: var(--white); font-family: var(--font-body); font-weight: 300; line-height: 1.7; }}
  a {{ color: var(--gold); }}
  nav {{ padding: 1.25rem 3rem; border-bottom: 1px solid rgba(201,168,76,0.12); background: rgba(11,19,34,0.95); }}
  nav a {{ font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--slate); text-decoration: none; }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 4rem 1.5rem 6rem; }}
  .tag {{ display: inline-block; font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold-dim); border: 1px solid rgba(201,168,76,0.25); padding: 0.3rem 0.8rem; margin-bottom: 1.5rem; }}
  h1 {{ font-family: var(--font-display); font-weight: 300; font-size: clamp(2rem, 4.5vw, 3rem); line-height: 1.15; margin-bottom: 1rem; }}
  .meta {{ font-size: 0.75rem; color: var(--slate); letter-spacing: 0.05em; margin-bottom: 2rem; }}
  .cover {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; margin-bottom: 2.5rem; border: 1px solid rgba(201,168,76,0.15); }}
  .listen-row {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 3rem; }}
  .listen-row a {{ font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; border: 1px solid rgba(201,168,76,0.3); padding: 0.65rem 1.25rem; text-decoration: none; }}
  .content h2 {{ font-family: var(--font-display); font-weight: 400; font-size: 1.6rem; margin: 2.5rem 0 1rem; color: var(--gold-light); }}
  .content p {{ margin-bottom: 1.2rem; color: var(--slate-light); }}
  .content ul, .content ol {{ margin: 0 0 1.2rem 1.3rem; color: var(--slate-light); }}
  .content li {{ margin-bottom: 0.4rem; }}
  .content em {{ color: var(--gold-dim); }}
  .back-link {{ display: inline-block; margin-top: 3rem; font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; text-decoration: none; }}
  footer {{ padding: 2rem 3rem; border-top: 1px solid rgba(201,168,76,0.12); font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--slate); text-align: center; }}
</style>
</head>
<body>
<nav><a href="../index.html">&#8592; D&amp;D Strategic Impact</a></nav>
"""

PAGE_FOOT = """
<footer>D&amp;D Tech Hub &middot; A D&amp;D Strategic Impact Initiative</footer>
</body>
</html>
"""


def load_post(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path.name}: missing frontmatter (--- block)")
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    meta["_body_html"] = md.markdown(body, extensions=["extra"])
    meta.setdefault("slug", path.stem)
    return meta


def render_post_page(post: dict) -> str:
    listen_links = ""
    if post.get("listen_spotify_url") and post["listen_spotify_url"] != "#":
        listen_links += f'<a href="{post["listen_spotify_url"]}" target="_blank" rel="noopener">Listen on Spotify</a>'
    if post.get("listen_apple_url") and post["listen_apple_url"] != "#":
        listen_links += f'<a href="{post["listen_apple_url"]}" target="_blank" rel="noopener">Listen on Apple Podcasts</a>'

    cover_html = ""
    if post.get("cover_image"):
        cover_html = f'<img class="cover" src="{post["cover_image"]}" alt="{post.get("title","")} cover art" />'

    guest_html = f'<div class="meta">Guest: {post["guest"]}</div>' if post.get("guest") else ""

    return f"""{PAGE_HEAD.format(title=post.get('title','Untitled'))}
<div class="wrap">
  <div class="tag">{post.get('category','Blog')}{' &middot; Episode ' + str(post['episode_number']) if post.get('episode_number') else ''}</div>
  <h1>{post.get('title','Untitled')}</h1>
  <div class="meta">{post.get('date','')}</div>
  {guest_html}
  {cover_html}
  <div class="listen-row">{listen_links}</div>
  <div class="content">{post['_body_html']}</div>
  <a class="back-link" href="index.html">&#8592; All Episodes &amp; Posts</a>
</div>
{PAGE_FOOT}"""


def render_index(posts: list) -> str:
    posts_sorted = sorted(posts, key=lambda p: str(p.get("date", "")), reverse=True)
    categories = sorted(set(p.get("category", "blog") for p in posts_sorted))

    filter_buttons = '<button class="filter-btn active" data-cat="all">All</button>' + "".join(
        f'<button class="filter-btn" data-cat="{c}">{c.title()}</button>' for c in categories
    )

    cards = ""
    for p in posts_sorted:
        cover = p.get("cover_image", "")
        cover_html = f'<img src="{cover}" alt="{p.get("title","")}" />' if cover else '<div class="no-cover">No Cover Yet</div>'
        cards += f"""
        <a class="card" href="{p['slug']}.html" data-cat="{p.get('category','blog')}">
          <div class="card-art">{cover_html}</div>
          <div class="card-body">
            <div class="card-tag">{p.get('category','Blog')}{' &middot; Ep. ' + str(p['episode_number']) if p.get('episode_number') else ''}</div>
            <div class="card-title">{p.get('title','Untitled')}</div>
            <div class="card-desc">{p.get('description','')}</div>
          </div>
        </a>"""

    return f"""{PAGE_HEAD.format(title='Tech Hub Blog')}
<style>
  .wrap {{ max-width: 1100px; }}
  h1 {{ margin-bottom: 0.5rem; }}
  .filters {{ display: flex; gap: 0.75rem; margin: 2rem 0 3rem; flex-wrap: wrap; }}
  .filter-btn {{ background: transparent; border: 1px solid rgba(201,168,76,0.25); color: var(--slate); font-family: var(--font-body); font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.5rem 1.1rem; cursor: pointer; }}
  .filter-btn.active, .filter-btn:hover {{ border-color: var(--gold); color: var(--gold); }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5px; background: rgba(201,168,76,0.12); }}
  .card {{ background: var(--navy); text-decoration: none; color: inherit; display: block; transition: background 0.2s; }}
  .card:hover {{ background: var(--navy-light); }}
  .card-art {{ aspect-ratio: 16/9; background: var(--navy-light); overflow: hidden; }}
  .card-art img {{ width: 100%; height: 100%; object-fit: cover; }}
  .no-cover {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold-dim); border: 1px dashed rgba(201,168,76,0.25); }}
  .card-body {{ padding: 1.5rem; }}
  .card-tag {{ font-size: 0.6rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold-dim); margin-bottom: 0.5rem; }}
  .card-title {{ font-size: 0.95rem; font-weight: 500; margin-bottom: 0.5rem; }}
  .card-desc {{ font-size: 0.78rem; color: var(--slate); line-height: 1.6; }}
</style>
<div class="wrap">
  <div class="tag">Tech Hub</div>
  <h1>Blog &amp; Episodes</h1>
  <p style="color:var(--slate);font-size:0.9rem;max-width:600px">News from the D&amp;D Tech Hub, plus every Leading Transformation podcast episode with full show notes.</p>
  <div class="filters">{filter_buttons}</div>
  <div class="grid" id="postGrid">{cards}</div>
</div>
<script>
  const params = new URLSearchParams(window.location.search);
  const initialCat = params.get('category') || 'all';

  function applyFilter(cat) {{
    document.querySelectorAll('.card').forEach(c => {{
      c.style.display = (cat === 'all' || c.dataset.cat === cat) ? '' : 'none';
    }});
    document.querySelectorAll('.filter-btn').forEach(b => {{
      b.classList.toggle('active', b.dataset.cat === cat);
    }});
  }}

  document.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', () => applyFilter(btn.dataset.cat));
  }});

  applyFilter(initialCat);
</script>
{PAGE_FOOT}"""


def main():
    posts = [load_post(p) for p in sorted(CONTENT_DIR.glob("*.md"))]
    if not posts:
        print("No markdown posts found in blog/content/.")
        return

    for post in posts:
        out_path = OUTPUT_DIR / f"{post['slug']}.html"
        out_path.write_text(render_post_page(post), encoding="utf-8")
        print(f"Wrote {out_path.relative_to(ROOT.parent)}")

    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(render_index(posts), encoding="utf-8")
    print(f"Wrote {index_path.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()

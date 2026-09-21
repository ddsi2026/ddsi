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
<link rel="icon" href="../favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="32x32" href="../images/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="../images/favicon-16x16.png" />
<link rel="apple-touch-icon" href="../images/apple-touch-icon.png" />
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
  html {{ scroll-behavior: smooth; }}
  body {{ background: var(--navy); color: var(--white); font-family: var(--font-body); font-weight: 300; line-height: 1.7; overflow-x: hidden; position: relative; }}
  a {{ color: inherit; text-decoration: none; }}
  .page-bg {{ position: fixed; inset: 0; z-index: -2; background-image: url('../images/portfolio-bg.jpg'); background-size: cover; background-position: center; opacity: 0.2; filter: grayscale(0.1) contrast(1.05); }}
  .page-bg-overlay {{ position: fixed; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(11,19,34,0.72), rgba(11,19,34,0.9) 40%, var(--navy) 92%); }}
  nav {{ position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 3rem; border-bottom: 1px solid rgba(201,168,76,0.12); background: rgba(11,19,34,0.95); backdrop-filter: blur(12px); }}
  .nav-logo {{ display: flex; align-items: center; gap: 12px; }}
  .nav-logo-main {{ font-family: var(--font-display); font-size: 1rem; font-weight: 500; letter-spacing: 0.12em; color: var(--gold); text-transform: uppercase; line-height: 1.2; }}
  .nav-logo-sub {{ font-size: 0.55rem; letter-spacing: 0.18em; color: var(--slate); text-transform: uppercase; line-height: 1.2; }}
  .nav-links {{ display: flex; align-items: center; gap: 2rem; }}
  .nav-link {{ font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--slate); cursor: pointer; white-space: nowrap; }}
  .nav-link:hover {{ color: var(--gold); }}
  .nav-cta {{ font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase; padding: 0.55rem 1.3rem; border: 1px solid var(--gold-dim); color: var(--gold); }}
  .nav-cta:hover {{ background: var(--gold); color: var(--navy); }}
  .nav-toggle {{ display: none; flex-direction: column; gap: 5px; cursor: pointer; padding: 0.5rem; }}
  .nav-toggle span {{ width: 22px; height: 1.5px; background: var(--gold); display: block; }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding: 9rem 2rem 6rem; }}
  .tag {{ display: inline-block; font-size: 0.66rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold-dim); border: 1px solid rgba(201,168,76,0.25); padding: 0.35rem 0.9rem; margin-bottom: 1.5rem; }}
  h1 {{ font-family: var(--font-display); font-weight: 300; font-size: clamp(2.2rem, 4.5vw, 3.2rem); line-height: 1.15; margin-bottom: 1rem; max-width: none; }}
  .meta {{ font-size: 0.85rem; color: var(--slate); letter-spacing: 0.05em; margin-bottom: 2rem; }}
  .cover {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; margin-bottom: 2.5rem; border: 1px solid rgba(201,168,76,0.15); }}
  .listen-row {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 3rem; }}
  .listen-row a {{ font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; border: 1px solid rgba(201,168,76,0.3); padding: 0.7rem 1.4rem; text-decoration: none; }}
  .content h2 {{ font-family: var(--font-display); font-weight: 400; font-size: 1.75rem; margin: 2.5rem 0 1rem; color: var(--gold-light); }}
  .content p {{ margin-bottom: 1.2rem; color: var(--slate-light); font-size: 1rem; }}
  .content ul, .content ol {{ margin: 0 0 1.2rem 1.3rem; color: var(--slate-light); font-size: 1rem; }}
  .content li {{ margin-bottom: 0.4rem; }}
  .content em {{ color: var(--gold-dim); }}
  .back-link {{ display: inline-block; margin-top: 3rem; font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; text-decoration: none; color: var(--gold); }}
  footer {{ padding: 3rem; border-top: 1px solid rgba(201,168,76,0.12); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; position: relative; }}
  .footer-left {{ font-size: 0.7rem; color: var(--slate); }}
  .footer-right {{ font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--slate); }}
  @media (max-width: 900px) {{
    nav {{ padding: 0.75rem 1.25rem; }}
    .nav-links {{ display: none; position: absolute; top: 100%; left: 0; right: 0; flex-direction: column; align-items: flex-start; gap: 1.25rem; background: var(--navy); padding: 1.5rem; border-bottom: 1px solid rgba(201,168,76,0.2); }}
    .nav-links.open {{ display: flex; }}
    .nav-toggle {{ display: flex; }}
  }}
  @media (max-width: 860px) {{
    .wrap {{ padding: 8rem 1.25rem 4rem; }}
  }}
</style>
</head>
<body>
<div class="page-bg"></div>
<div class="page-bg-overlay"></div>
<nav>
  <a class="nav-logo" href="../index.html">
    <img src="../logo.png" alt="Logo" style="height: 34px; width: auto;">
    <div style="display:flex;flex-direction:column;">
      <span class="nav-logo-main">D&amp;D Strategic Impact</span>
      <span class="nav-logo-sub">A D&amp;D Legacy Capital Company</span>
    </div>
  </a>
  <div class="nav-toggle" onclick="document.getElementById('navLinks').classList.toggle('open')"><span></span><span></span><span></span></div>
  <div class="nav-links" id="navLinks">
    <a class="nav-link" href="../index.html#top">Overview</a>
    <a class="nav-link" href="../index.html#portfolio-section">Portfolio</a>
    <a class="nav-link" href="../index.html#advisory-section">Advisory</a>
    <a class="nav-link" href="../index.html#techhub-section">Tech Hub</a>
    <a class="nav-link" href="../index.html#incubator-section">Incubator</a>
    <a class="nav-link" href="../index.html#podcast-preview-section">Podcast</a>
    <a class="nav-link" href="../about.html">About Us</a>
    <a class="nav-link nav-cta" href="../index.html#contact-section">Engage</a>
  </div>
</nav>
"""

PAGE_FOOT = """
<footer>
  <div class="footer-left">Leading Transformation Podcast &middot; A <a href="../index.html">D&amp;D Strategic Impact</a> Initiative</div>
  <div class="footer-right">&copy; 2026 D&amp;D Strategic Impact</div>
</footer>
<script>
  var navToggleLinks = document.getElementById('navLinks');
  if (navToggleLinks) {
    navToggleLinks.querySelectorAll('.nav-link').forEach(function(l){
      l.addEventListener('click', function(){ navToggleLinks.classList.remove('open'); });
    });
  }
</script>
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


TOPICS = [
    "AI Adoption: Pilot to Deployment",
    "Realizing Measurable ROI",
    "Compliance & Governance",
    "Scaling Technology",
    "Building in Regulated Industries",
    "Unconventional, Overlooked Insights",
]


def render_index(posts: list) -> str:
    # Podcast episodes list in episode order (1, 2, 3, ...); everything else
    # (non-episode blog posts) lists newest-first by date.
    episodes = sorted(
        (p for p in posts if p.get("episode_number") is not None),
        key=lambda p: p["episode_number"],
    )
    others = sorted(
        (p for p in posts if p.get("episode_number") is None),
        key=lambda p: str(p.get("date", "")),
        reverse=True,
    )
    posts_sorted = episodes + others

    topics_html = "".join(f'<div class="topic-item">{t}</div>' for t in TOPICS)

    rows = ""
    for p in posts_sorted:
        cover = p.get("cover_image", "")
        cover_html = f'<img src="{cover}" alt="{p.get("title","")}" />' if cover else '<div class="no-cover">No Cover Yet</div>'
        guest_line = f'<div class="row-guest">Guest: {p["guest"]}</div>' if p.get("guest") else ""
        rows += f"""
        <a class="episode-row" href="{p['slug']}.html">
          <div class="row-art">{cover_html}</div>
          <div class="row-body">
            <div class="row-tag">{p.get('category','Blog')}{' &middot; Episode ' + str(p['episode_number']) if p.get('episode_number') else ''}</div>
            <div class="row-title">{p.get('title','Untitled')}</div>
            {guest_line}
            <div class="row-desc">{p.get('description','')}</div>
          </div>
        </a>"""

    return f"""{PAGE_HEAD.format(title='Leading Transformation Podcast')}
<style>
  .wrap {{ max-width: 1280px; }}
  h1 {{ margin-bottom: 1.25rem; max-width: none; font-size: clamp(2.6rem, 5.5vw, 4rem); }}
  .lede {{ color: var(--slate-light); font-size: 1.15rem; max-width: 880px; line-height: 1.85; margin-bottom: 3.5rem; }}
  .topics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5px; background: rgba(201,168,76,0.15); margin-bottom: 4.5rem; }}
  .topic-item {{ background: var(--navy-mid); padding: 1.4rem 1.5rem; font-size: 0.9rem; letter-spacing: 0.02em; color: var(--gold-light); text-align: center; font-family: var(--font-display); }}
  .episode-list {{ display: flex; flex-direction: column; gap: 2px; background: rgba(201,168,76,0.12); margin-bottom: 4.5rem; }}
  .episode-row {{ display: flex; gap: 2.5rem; background: var(--navy); text-decoration: none; color: inherit; padding: 2rem; align-items: center; transition: background 0.2s; }}
  .episode-row:hover {{ background: var(--navy-light); }}
  .row-art {{ flex: 0 0 340px; aspect-ratio: 16/9; background: var(--navy-light); overflow: hidden; border: 1px solid rgba(201,168,76,0.15); }}
  .row-art img {{ width: 100%; height: 100%; object-fit: cover; }}
  .no-cover {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold-dim); border: 1px dashed rgba(201,168,76,0.25); }}
  .row-body {{ flex: 1; min-width: 0; }}
  .row-tag {{ font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--gold-dim); margin-bottom: 0.6rem; }}
  .row-title {{ font-size: 1.55rem; font-weight: 400; font-family: var(--font-display); line-height: 1.25; margin-bottom: 0.6rem; }}
  .row-guest {{ font-size: 0.85rem; color: var(--gold); margin-bottom: 0.6rem; letter-spacing: 0.02em; }}
  .row-desc {{ font-size: 0.95rem; color: var(--slate-light); line-height: 1.7; }}
  .guest-cta {{ background: var(--navy-mid); border: 1px solid rgba(201,168,76,0.2); padding: 3.5rem 2.5rem; text-align: center; }}
  .guest-cta h2 {{ font-family: var(--font-display); font-weight: 400; font-size: 1.9rem; margin-bottom: 1rem; color: var(--gold-light); }}
  .guest-cta p {{ color: var(--slate-light); max-width: 620px; margin: 0 auto 1.75rem; font-size: 0.95rem; line-height: 1.75; }}
  .btn-primary {{ display: inline-block; padding: 0.95rem 2.5rem; background: var(--gold); color: var(--navy); font-family: var(--font-body); font-size: 0.75rem; font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; }}
  .btn-primary:hover {{ background: var(--gold-light); }}
  @media (max-width: 900px) {{
    .topics-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .episode-row {{ flex-direction: column; align-items: flex-start; gap: 1.25rem; padding: 1.5rem; }}
    .row-art {{ flex: none; width: 100%; }}
  }}
</style>
<div class="wrap">
  <div class="tag">Leading Transformation</div>
  <h1>Leading Transformation</h1>
  <p class="lede">An interview series with executives and founders navigating AI adoption and technology transformation inside large, regulated organizations.</p>
  <div class="topics-grid">{topics_html}</div>
  <div class="episode-list">{rows}</div>
  <div class="guest-cta">
    <h2>Become a Guest</h2>
    <p>We're always looking to feature enterprise leaders sharing their real AI-adoption and technology-transformation journey. If that's you, we'd love to have you on the show.</p>
    <a class="btn-primary" href="../index.html?inquiry=podcast#contact-section">Get Featured</a>
  </div>
</div>
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

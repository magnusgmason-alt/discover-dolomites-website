#!/usr/bin/env python3
"""Builds journal article pages for discoverdolomites.org from articles.json.
Usage: articles.py <site_root> <articles.json>"""
import json, sys, os, html

ROOT, SRC = sys.argv[1], sys.argv[2]
SITE = "https://discoverdolomites.org"
arts = json.load(open(SRC, encoding="utf-8"))
by_slug = {a["slug"]: a for a in arts}

HEADER = """<header class="site-header solid" id="header">
  <div class="container header-inner">
    <a class="logo" href="/" aria-label="Discover Dolomites, home">Discover<b>Dolomites</b><i>.</i></a>
    <button class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span><span></span></button>
    <nav class="nav" id="nav" aria-label="Main">
      <a href="/#guides">All guides</a>
      <div class="dropdown">
        <button class="dropdown-btn" aria-haspopup="true" aria-expanded="false">Regions <span aria-hidden="true">▾</span></button>
        <div class="dropdown-menu">
          <a href="/#map">All regions</a>
          <a href="/#map">Cortina d’Ampezzo</a>
          <a href="/#map">Val Gardena</a>
          <a href="/#map">Alta Badia</a>
          <a href="/#map">Alpe di Siusi</a>
          <a href="/#map">Tre Cime</a>
          <a href="/#map">Val di Fassa</a>
        </div>
      </div>
      <a href="/summer/">Summer</a>
      <a href="/winter/">Winter</a>
      <a href="/#peaks">The Rock</a>
      <a href="/#history">History</a>
      <a href="/journal/">Journal</a>
      <a href="/#checklist">Free checklist</a>
      <div class="dropdown lang">
        <button class="dropdown-btn" aria-haspopup="true" aria-expanded="false">EN <span aria-hidden="true">▾</span></button>
        <div class="dropdown-menu">
          <a href="#" aria-current="true">English</a>
          <span class="soon">Italiano · soon</span>
          <span class="soon">Deutsch · soon</span>
          <span class="soon">Español · soon</span>
          <span class="soon">中文 · soon</span>
          <span class="soon">日本語 · soon</span>
        </div>
      </div>
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="container footer-inner">
    <a class="logo" href="/">Discover<b>Dolomites</b><i>.</i></a>
    <nav aria-label="Footer">
      <a href="/#guides">All guides</a>
      <a href="/summer/">Summer</a>
      <a href="/winter/">Winter</a>
      <a href="/journal/">Journal</a>
      <a href="/#checklist">Free checklist</a>
    </nav>
    <p>© <span id="year">2026</span> Discover Dolomites. Independent travel guides to the Dolomites and the mountains of northern Italy.</p>
  </div>
</footer>"""


def img(name, alt, sizes, cls="", eager=False, w=1800, h=1200):
    c = f' class="{cls}"' if cls else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img{c} src="/assets/img/{name}-1800.jpg" srcset="/assets/img/{name}-800.jpg 800w, '
            f'/assets/img/{name}-1800.jpg 1800w" sizes="{sizes}" alt="{html.escape(alt)}" width="{w}" height="{h}" {load}>')


def related_card(a):
    return f"""        <article class="journal-card">
          <a class="card-link" href="/journal/{a['slug']}/">
          {img(a['image'], a['image_alt'], '(min-width: 760px) 430px, 100vw', w=a['image_w'], h=a['image_h'])}
          <div><span class="tags">{html.escape(a['tags'])}</span><h3>{html.escape(a['title'])}</h3><p>{html.escape(a['card_summary'])}</p><span class="soon-label">{a['read_time']} read</span></div>
          </a>
        </article>"""


COVER = '          <img src="/assets/img/cover-{0}-500.jpg" alt="Discover Dolomites, {1} Edition" width="500" height="750" loading="lazy" decoding="async">'
def cta(a):
    if a.get("season") == "winter":
        return dict(covers=COVER.format("winter","Winter"), cta_eyebrow="The winter guide · Coming soon", cta_title="Discover Dolomites: Winter Edition", cta_text="Skiing and snowboarding by level, ski areas and lift maps, rifugi, and winter safety.", cta_link="/#winter")
    return dict(covers=COVER.format("summer","Summer")+"\n"+COVER.format("winter","Winter"), cta_eyebrow="The guides · Coming soon", cta_title="Plan it properly with Discover Dolomites", cta_text="A summer edition for hiking trails, huts and maps, and a winter edition for skiing and snowboarding.", cta_link="/#guides")

for a in arts:
    url = f"{SITE}/journal/{a['slug']}/"
    others = [by_slug[s] for s in a["related"]]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": a["title"], "description": a["description"],
             "image": f"{SITE}/assets/img/{a['image']}-1800.jpg", "datePublished": a["date"], "dateModified": a["date"],
             "author": {"@type": "Organization", "name": "Discover Dolomites", "url": SITE + "/"},
             "publisher": {"@type": "Organization", "name": "Discover Dolomites", "url": SITE + "/"},
             "mainEntityOfPage": url},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Journal", "item": SITE + "/journal/"},
                {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]}]}
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(a['seo_title'])}</title>
  <meta name="description" content="{html.escape(a['description'])}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Discover Dolomites">
  <meta property="og:title" content="{html.escape(a['title'])}">
  <meta property="og:description" content="{html.escape(a['description'])}">
  <meta property="og:image" content="{SITE}/assets/img/{a.get('og', a['image'] + '-1800')}.jpg">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{html.escape(a['title'])}">
  <meta name="twitter:image" content="{SITE}/assets/img/{a.get('og', a['image'] + '-1800')}.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0e1317">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&amp;family=Playfair+Display:ital,wght@0,600;0,700;1,500&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css?v=5">
  <link rel="stylesheet" href="/assets/css/article.css?v=3">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>

{HEADER}

<main id="top">
  <section class="article-hero">
    {img(a['image'], a['image_alt'], '100vw', cls='bg', eager=True, w=a['image_w'], h=a['image_h'])}
    <div class="shade"></div>
    <div class="container article-hero-inner">
      <p class="crumbs"><a href="/">Home</a> &nbsp;/&nbsp; <a href="/journal/">Journal</a></p>
      <p class="eyebrow light">{html.escape(a['tags'])}</p>
      <h1>{html.escape(a['title'])}</h1>
      <span class="rule"></span>
      <p class="article-meta">{a['read_time']} read · Updated {a['date_label']}</p>
    </div>
  </section>

  <div class="article-wrap">
    <div class="container">
      <article class="article-body">
{a['body_html']}
        <p class="updated-note">{a['note']}</p>
      </article>

      <aside class="article-cta" aria-label="The Discover Dolomites guides">
        <div class="covers">
{cta(a)["covers"]}
        </div>
        <div>
          <p class="eyebrow">{cta(a)["cta_eyebrow"]}</p>
          <h2>{cta(a)["cta_title"]}</h2>
          <p>{cta(a)["cta_text"]}</p>
          <div class="btn-row"><a class="btn primary" href="/#checklist">Get the free checklist</a><a class="btn outline" href="{cta(a)["cta_link"]}">{"See the guide" if a.get("season")=="winter" else "See the guides"}</a></div>
        </div>
      </aside>
    </div>
  </div>

  <section class="related" aria-labelledby="related-title">
    <div class="container">
      <p class="eyebrow center">From the journal</p>
      <h2 class="center" id="related-title">Keep planning</h2>
      <div class="journal-grid">
{chr(10).join(related_card(o) for o in others)}
      </div>
    </div>
  </section>
</main>

{FOOTER}

<script src="/assets/js/main.js?v=3" defer></script>
</body>
</html>
"""
    d = os.path.join(ROOT, "journal", a["slug"])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)
    words = len(html.unescape(__import__("re").sub("<[^>]+>", " ", a["body_html"])).split())
    print(a["slug"], words, "words")

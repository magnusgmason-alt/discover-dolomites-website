import json,sys,html,re
ROOT,SRC,TOOL=sys.argv[1:4]
arts=json.load(open(SRC))
src=open(TOOL).read()
ns={}
exec(src.split("for a in arts:")[0].replace("ROOT, SRC = sys.argv[1], sys.argv[2]","ROOT,SRC=%r,%r"%(ROOT,SRC)),ns)
H,F,card=ns["HEADER"],ns["FOOTER"],ns["related_card"]
H=H.replace('<a href="/journal/">Journal</a>','<a href="/journal/" aria-current="page">Journal</a>')
win=[a for a in arts if a.get("season")=="winter"]; rest=[a for a in arts if a.get("season")!="winter"]
def grid(lst): return "\n".join(card(a) for a in lst)
ld={"@context":"https://schema.org","@type":"CollectionPage","name":"The Discover Dolomites Journal","url":"https://discoverdolomites.org/journal/",
 "hasPart":[{"@type":"Article","headline":a["title"],"url":f"https://discoverdolomites.org/journal/{a['slug']}/"} for a in arts]}
page=f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Dolomites Travel Journal: Planning, Skiing &amp; Hiking Guides | Discover Dolomites</title>
  <meta name="description" content="Practical guides to the Dolomites: when to go, where to stay, what to book, and skiing and snowboarding with kids, beginners and families.">
  <link rel="canonical" href="https://discoverdolomites.org/journal/">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://discoverdolomites.org/journal/">
  <meta property="og:site_name" content="Discover Dolomites">
  <meta property="og:title" content="The Discover Dolomites Journal">
  <meta property="og:description" content="Practical guides to planning, skiing and hiking in the Dolomites.">
  <meta property="og:image" content="https://discoverdolomites.org/assets/img/share-home.jpg?v=2">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0e1317">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&amp;family=Playfair+Display:ital,wght@0,600;0,700;1,500&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css?v=5">
  <link rel="stylesheet" href="/assets/css/article.css?v=3">
  <script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
</head>
<body>

{H}

<main id="top">
  <section class="article-hero">
    {ns['img']('winter-alpenglow','Snow-dusted Dolomites peaks glowing at sunrise','100vw',cls='bg',eager=True)}
    <div class="shade"></div>
    <div class="container article-hero-inner">
      <p class="crumbs"><a href="/">Home</a></p>
      <p class="eyebrow light">From the journal</p>
      <h1>The Discover Dolomites Journal</h1>
      <span class="rule"></span>
      <p class="article-meta">Tips, maps &amp; field notes for summer and winter</p>
    </div>
  </section>

  <section class="related" aria-labelledby="winter-title">
    <div class="container">
      <p class="eyebrow center">Winter 2026/27</p>
      <h2 class="center" id="winter-title">Skiing &amp; snowboarding</h2>
      <div class="journal-grid">
{grid(win)}
      </div>
    </div>
  </section>

  <section class="related" aria-labelledby="plan-title">
    <div class="container">
      <p class="eyebrow center">All year</p>
      <h2 class="center" id="plan-title">Planning your trip</h2>
      <div class="journal-grid">
{grid(rest)}
      </div>
    </div>
  </section>
</main>

{F}

<script src="/assets/js/main.js?v=3" defer></script>
</body>
</html>
"""
open(ROOT+"/journal/index.html","w").write(page)

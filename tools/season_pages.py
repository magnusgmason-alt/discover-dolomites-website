import json,sys,html
from PIL import Image
ROOT,SRC,TOOL=sys.argv[1:4]
arts={a["slug"]:a for a in json.load(open(SRC))}
src=open(TOOL).read(); ns={}
exec(src.split("for a in arts:")[0].replace("ROOT, SRC = sys.argv[1], sys.argv[2]","ROOT,SRC=%r,%r"%(ROOT,SRC)),ns)
H,F,card,img=ns["HEADER"],ns["FOOTER"],ns["related_card"],ns["img"]
def dims(i): return Image.open(f"{ROOT}/assets/img/{i}-1800.jpg").size
n=[0]
def fig(i,alt,place,cap):
    w,h=dims(i); c=("portrait" if h>w else "wide")+(" flip" if n[0]%2 else ""); n[0]+=1
    return (f'<figure class="{c}"><img src="/assets/img/{i}-1800.jpg" srcset="/assets/img/{i}-800.jpg 800w, /assets/img/{i}-1800.jpg 1800w" sizes="(min-width: 760px) 720px, 100vw" alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async">'
            f'<figcaption><span class="fig-place">{html.escape(place)}</span>{html.escape(cap)}</figcaption></figure>')
def book(season):
    if season=="summer":
        return '''  <section class="section stone book-bg book-bg-summer">
    <div class="container book-feature">
      <a class="cover" href="/#guides"><img src="/assets/img/cover-summer-900.jpg" srcset="/assets/img/cover-summer-500.jpg 500w, /assets/img/cover-summer-900.jpg 900w" sizes="(min-width: 900px) 360px, 80vw" alt="Cover of Discover Dolomites, Summer Edition" width="900" height="1350" loading="lazy" decoding="async"></a>
      <div>
        <p class="eyebrow">The summer guide · Coming soon</p>
        <h3>Discover Dolomites<small>Summer Edition</small></h3>
        <p class="subtitle">Hiking trails, huts &amp; maps</p>
        <ul class="features"><li>Best hiking trails</li><li>Hut-to-hut routes</li><li>Trail maps</li><li>Season &amp; weather calendar</li></ul>
        <div class="btn-row">
          <a class="btn primary" href="/#checklist">Notify me at launch</a>
          <a class="btn outline" href="/winter/">See the winter edition</a>
        </div>
      </div>
    </div>
  </section>'''
    return '''  <section class="section stone book-bg book-bg-winter">
    <div class="container book-feature">
      <a class="cover" href="/#guides"><img src="/assets/img/cover-winter-900.jpg" srcset="/assets/img/cover-winter-500.jpg 500w, /assets/img/cover-winter-900.jpg 900w" sizes="(min-width: 900px) 360px, 80vw" alt="Cover of Discover Dolomites, Winter Edition" width="900" height="1350" loading="lazy" decoding="async"></a>
      <div>
        <p class="eyebrow">The winter guide · Coming soon</p>
        <h3>Discover Dolomites<small>Winter Edition</small></h3>
        <p class="subtitle">Skiing, snowboarding &amp; maps</p>
        <ul class="features"><li>Ski areas by level</li><li>Sella Ronda &amp; lift maps</li><li>Family skiing</li><li>Slope rules &amp; safety</li></ul>
        <div class="btn-row">
          <a class="btn primary" href="/#checklist">Notify me at launch</a>
          <a class="btn outline" href="/summer/">See the summer edition</a>
        </div>
      </div>
    </div>
  </section>'''
def page(slug,title,seo,desc,eyebrow,meta,hero,hero_alt,body,rel_title,rel):
    w,h=dims(hero); url=f"https://discoverdolomites.org/{slug}/"
    hh=H.replace(f'<a href="/{slug}/">',f'<a href="/{slug}/" aria-current="page">')
    ld={"@context":"https://schema.org","@type":"WebPage","name":title,"description":desc,"url":url,
        "breadcrumb":{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://discoverdolomites.org/"},{"@type":"ListItem","position":2,"name":title,"item":url}]}}
    cards="\n".join(card(arts[s]) for s in rel)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(seo)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Discover Dolomites">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="https://discoverdolomites.org/assets/img/share-{slug}.jpg">
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

{hh}

<main id="top">
  <section class="article-hero">
    {img(hero,hero_alt,'100vw',cls='bg',eager=True,w=w,h=h)}
    <div class="shade"></div>
    <div class="container article-hero-inner">
      <p class="crumbs"><a href="/">Home</a></p>
      <p class="eyebrow light">{eyebrow}</p>
      <h1>{html.escape(title)}</h1>
      <span class="rule"></span>
      <p class="article-meta">{meta}</p>
    </div>
  </section>

  <div class="article-wrap">
    <div class="container">
      <article class="article-body">
{body}
      </article>
    </div>
  </div>

{book(slug)}

  <section class="related" aria-labelledby="rel-title">
    <div class="container">
      <p class="eyebrow center">From the journal</p>
      <h2 class="center" id="rel-title">{rel_title}</h2>
      <div class="journal-grid">
{cards}
      </div>
    </div>
  </section>
</main>

{F}

<script src="/assets/js/main.js?v=3" defer></script>
</body>
</html>
'''
import os
summer=f'''        <p>Summer in the Dolomites runs from late June to late September. The snow retreats from the high trails, the lifts start turning, and the mountain huts open their doors. It is the season for hiking under pale rock towers, sleeping in huts, and long lunches with a view. Here is what a Dolomites summer looks like, and where to start.</p>

        <h2>When the season starts</h2>
        <p>Most low and mid-altitude huts open around 20 June, and the rest follow as their paths clear of snow. July and early September are the most reliable months for high routes. August is the warmest and busiest, with the Italian Ferragosto holiday on 15 August at its peak. Our month-by-month guide, <a href="/journal/best-time-to-visit-the-dolomites/">the best time to visit the Dolomites</a>, has the details.</p>
        {fig("seceda-aerial","Aerial view of the Seceda ridge and its green slopes in summer","Seceda · Val Gardena","Seceda above Val Gardena: a knife-edge ridge over green alpine meadows.")}

        <h2>Classic summer hikes</h2>
        <ul>
          <li><strong>Tre Cime di Lavaredo:</strong> the famous loop around the three towers, starting from Rifugio Auronzo at the end of the toll road.</li>
          <li><strong>Seceda:</strong> a cable car from Ortisei up to one of the most photographed ridges in the Alps.</li>
          <li><strong>Alpe di Siusi:</strong> easy walks across Europe's largest high alpine meadow, below the Sassolungo and the Sciliar.</li>
          <li><strong>Cadini di Misurina:</strong> a short, steep path to a viewpoint over a forest of jagged spires.</li>
          <li><strong>Lago di Braies:</strong> an emerald lake ringed by cliffs, and the start of the Alta Via 1.</li>
        </ul>
        {fig("tre-cime-clouds","The three rock towers of Tre Cime di Lavaredo under big clouds","Tre Cime di Lavaredo","The three towers, the best-known shape in the Dolomites.")}

        <h2>Hut to hut</h2>
        <p>The Dolomites have a dense network of mountain huts (rifugi), many reached only on foot. You can walk from hut to hut for days on the long-distance Alte Vie, such as the Alta Via 1 from Lago di Braies, sleeping in dormitories or small rooms and eating hearty mountain food. Start a multi-day route no earlier than the last week of June, and book huts well ahead: see <a href="/journal/dolomites-what-to-book-in-advance/">what to book in advance</a>.</p>
        {fig("path-hiker","A lone hiker on a winding path across a green slope below a cloud-covered Seceda ridge","Below Seceda","Many trails start right from a lift station, so even short walks reach big scenery.")}

        <h2>Via ferratas</h2>
        <p>Many Dolomites routes follow iron cables, ladders and rungs, some built along First World War front lines. They let walkers reach places otherwise reserved for climbers. You need a helmet, harness and via ferrata lanyard, a head for heights and settled weather. If you are new to them, go with a mountain guide.</p>

        <h2>Weather and safety</h2>
        <p>Summer storms can build within minutes. Start early, aim to be off exposed ridges and via ferratas by early afternoon, carry a warm layer and rain jacket even on hot days, and check the forecast every morning. In an emergency, call 112.</p>
        {fig("cadini-hero","Jagged rock spires of the Cadini di Misurina rising through mist","Cadini di Misurina","When cloud rolls in, the spires of the Cadini appear and vanish within minutes.")}

        <h2>Where to stay in summer</h2>
        <p>Val Gardena and Alta Badia put you close to the most lifts and huts. Cortina is the base for the Tre Cime and the eastern Dolomites. Alpe di Siusi suits families and gentle walkers. Compare them in <a href="/journal/where-to-stay-in-the-dolomites/">which Dolomites valley to stay in</a>.</p>'''
n[0]=0
winter=f'''        <p>In winter the Dolomites become one of the largest ski areas in the world. Dolomiti Superski links twelve ski areas and around 1,200 km of slopes on one pass, from Cortina to Val Gardena, and the 2026/27 season runs from 28 November 2026 to 2 May 2027. Wide, groomed pistes, mountain huts on the slopes and the pale towers above make it unlike anywhere else in the Alps.</p>

        <h2>The main ski areas</h2>
        <ul>
          <li><strong>Val Gardena and Alpe di Siusi:</strong> 181 km of slopes together, from gentle meadows to the Sella Ronda.</li>
          <li><strong>Alta Badia:</strong> easy cruising runs, excellent ski schools and some of the best hut food in the Alps.</li>
          <li><strong>Cortina d'Ampezzo:</strong> Olympic history, the Tofane and the Cinque Torri.</li>
          <li><strong>Kronplatz (Plan de Corones):</strong> one mountain, lifts on every side, and a large snowpark.</li>
          <li><strong>Val di Fassa, Carezza and Obereggen:</strong> compact, family-friendly areas below the Rosengarten and the Latemar.</li>
          <li><strong>Arabba and the Marmolada:</strong> steeper runs and the highest peak in the Dolomites.</li>
        </ul>
        {fig("lit-piste-sassolungo","A freshly groomed piste and chairlift below the Sassolungo at night","Sassolungo · Val Gardena","Pistes are groomed every night, ready for the first lift in the morning.")}

        <h2>The Sella Ronda</h2>
        <p>The classic ski tour circles the Sella massif over four passes and through four valleys: about 44 km in a day, signposted in orange (clockwise) and green (anticlockwise). It suits confident intermediate skiers. Read <a href="/journal/sella-ronda-for-families-and-beginners/">the Sella Ronda for families and beginners</a> before you go.</p>
        {fig("passo-pordoi-dusk","Hotels and a winding road at Passo Pordoi at dusk below the Sella walls","Passo Pordoi","Passo Pordoi, one of the four passes on the Sella Ronda.")}

        <h2>Families and beginners</h2>
        <p>The Dolomites are one of the best places in the Alps to learn. Children born 2019 to 2023 ski free with a paying adult, ski schools teach from age three or four, and areas like Alpe di Siusi and Carezza are gentle and calm. Start with <a href="/journal/skiing-in-the-dolomites-with-kids/">skiing in the Dolomites with kids</a> and <a href="/journal/dolomites-skiing-for-beginners/">skiing for beginners</a>.</p>
        {fig("cinque-torri-winter","The Cinque Torri rock towers above snowy slopes near Cortina","Cinque Torri · Cortina","The Cinque Torri above Cortina, one of the most spectacular ski areas in the Dolomites.")}

        <h2>Rules to know</h2>
        <p>Italy has its own ski law. Helmets are compulsory for every skier and snowboarder, third-party liability insurance is mandatory, and there is an alcohol limit on the slopes. Details are in <a href="/journal/dolomites-ski-rules-helmets-insurance-safety/">Dolomites ski rules</a>.</p>

        <h2>Beyond the slopes</h2>
        <p>Not everyone needs to ski. Groomed winter walks, sledging runs, horse-drawn sleighs, Christmas markets and huts reached by gondola make the Dolomites a good winter trip for the whole family. See <a href="/journal/dolomites-winter-with-toddlers-and-non-skiers/">the Dolomites in winter with toddlers and non-skiers</a>.</p>
        {fig("winter-huts-rock-wall","Wooden huts in a sunny snowy meadow below pale rock walls","High meadows","Quiet huts and sunny meadows, a few minutes from the nearest lift.")}

        <h2>Ski and snowboard maps</h2>
        <p>We have drawn an illustrated panorama of every Dolomiti Superski area and the Sella Ronda, with runs by difficulty, lifts, peaks and villages: <a href="/ski-maps/">see all the ski and snowboard maps</a>.</p>'''
os.makedirs(ROOT+"/summer",exist_ok=True); os.makedirs(ROOT+"/winter",exist_ok=True)
open(ROOT+"/summer/index.html","w").write(page("summer","Summer in the Dolomites","Dolomites in Summer: Hiking, Huts & Via Ferratas | Discover Dolomites",
 "Hiking trails, hut-to-hut routes, via ferratas and the best summer walks in the Dolomites, from the Tre Cime and Seceda to Alpe di Siusi.",
 "The summer edition","Late June to September · Hiking, huts &amp; maps","tre-cime-aerial-dusk","Aerial view of Tre Cime di Lavaredo at first light with Rifugio Auronzo below",summer,"Plan your summer",
 ["best-time-to-visit-the-dolomites","where-to-stay-in-the-dolomites","dolomites-what-to-book-in-advance"]))
open(ROOT+"/winter/index.html","w").write(page("winter","Winter in the Dolomites","Dolomites in Winter: Skiing, Snowboarding & Ski Areas | Discover Dolomites",
 "Dolomiti Superski, the main ski areas, the Sella Ronda, family skiing, slope rules and winter beyond the pistes: your guide to the Dolomites in winter.",
 "The winter edition","Season 28 Nov 2026 – 2 May 2027 · Skiing, snowboarding &amp; maps","val-gardena-night-panorama","Val Gardena at night below the Sassolungo and the Sella group",winter,"Skiing &amp; snowboarding guides",
 [s for s,a in arts.items() if a.get("season")=="winter"]))
print("ok")

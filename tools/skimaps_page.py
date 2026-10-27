import json,sys,html
sys.path.insert(0,'/home/claude/skimaps')
from areas import AREAS
ROOT,SRC,TOOL,STATS=sys.argv[1:5]
src=open(TOOL).read(); ns={}
exec(src.split("for a in arts:")[0].replace("ROOT, SRC = sys.argv[1], sys.argv[2]","ROOT,SRC=%r,%r"%(ROOT,SRC)),ns)
H,F,img=ns["HEADER"],ns["FOOTER"],ns["img"]
st=json.load(open(STATS))
INFO={
'val-gardena-alpe-di-siusi':'The heart of the Sella Ronda on one side, Europe’s largest high alpine meadow on the other. Gentle Alpe di Siusi suits families and beginners; Ciampinoi and the Saslong add steep classics.',
'alta-badia':'Wide, well-groomed cruising runs between Corvara, Colfosco, La Villa and San Cassiano, with the Gran Risa World Cup slope and some of the best hut food in the Alps.',
'arabba-marmolada':'Steeper runs above Arabba at Porta Vescovo, and the Marmolada glacier, the highest skiing in the Dolomites, reached from Malga Ciapela.',
'val-di-fassa-carezza':'Canazei, Campitello and the Belvedere and Col Rodella lifts link into the Sella Ronda; Carezza, below the Latemar and Rosengarten, is quiet and family-friendly.',
'cortina-d-ampezzo':'Olympic Cortina: the Tofane, Cinque Torri with Lagazuoi, and Faloria-Cristallo, framed by some of the most spectacular rock in the range.',
'kronplatz':'One rounded summit with lifts and runs on every side, plus a large snowpark. Easy to navigate and quick to ski from any of the base villages.',
'3-zinnen-dolomites':'Monte Elmo and Croda Rossa above Sesto and San Candido, with long forest runs and views of the Sexten Dolomites.',
'val-di-fiemme-obereggen':'Obereggen and Pampeago below the Latemar, with a big snowpark and night skiing, plus Cermis above Cavalese.',
'san-martino-passo-rolle':'Tognola, Ces and Colverde above San Martino di Castrozza, and the open slopes of Passo Rolle below the Pale di San Martino.',
'alpe-lusia-san-pellegrino':'Alpe Lusia above Moena, and Passo San Pellegrino linked with Falcade: sunny, uncrowded skiing at the southern edge of the Sella group.',
'civetta':'Alleghe, Zoldo and Selva di Cadore linked below the north face of the Civetta, one of the great walls of the Dolomites.',
'plose':'Bressanone’s own mountain: wide open runs with views to the Odle, and one of the longest toboggan runs in the region. Part of the Rio Pusteria–Bressanone area.',
'gitschberg-jochtal':'Maranza and Valles above Rio Pusteria, linked by lift: sunny, family-friendly slopes. Part of the Rio Pusteria–Bressanone area.',
'sella-ronda':'The classic loop around the Sella massif: about 44 km, four passes, four valleys, signposted orange clockwise and green anticlockwise.',
}
cards=[]
for slug,t,sub,fb,az in AREAS:
    s=st.get(slug,{})
    cards.append(f'''        <article class="skimap" id="{slug}">
          <div class="skimap-head"><p class="eyebrow">{'The circuit' if slug=='sella-ronda' else 'Ski area'}</p><h2>{html.escape(t)}</h2><p class="skimap-sub">{html.escape(INFO[slug])}</p>
          <p class="skimap-stats"><span><b>{s.get('km','')} km</b> of runs on this map</span><span><b>{s.get('lifts','')}</b> lifts</span></p></div>
          <a class="skimap-img" href="/assets/img/skimap-{slug}.jpg" target="_blank" rel="noopener"><img src="/assets/img/skimap-{slug}-1600.jpg" srcset="/assets/img/skimap-{slug}-1600.jpg 1600w, /assets/img/skimap-{slug}.jpg 2400w" sizes="(min-width: 1200px) 1160px, 100vw" alt="Illustrated ski and snowboard map of {html.escape(t)}" width="2400" height="1790" loading="lazy" decoding="async"></a>
          <p class="fine">Tap the map to open it full size.</p>
        </article>''')
toc=''.join(f'<a href="#{s}">{html.escape(t)}</a>' for s,t,*_ in AREAS)
url="https://discoverdolomites.org/ski-maps/"
hh=H
page=f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Dolomites Ski Maps 2026/27: All 12 Dolomiti Superski Areas | Discover Dolomites</title>
  <meta name="description" content="Illustrated ski and snowboard maps of every Dolomiti Superski area and the Sella Ronda: runs by difficulty, lifts, peaks and villages, plus a winter map of the whole Dolomites.">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Discover Dolomites">
  <meta property="og:title" content="Dolomites ski &amp; snowboard maps"><meta property="og:description" content="Every Dolomiti Superski area and the Sella Ronda, mapped.">
  <meta property="og:image" content="https://discoverdolomites.org/assets/img/share-ski-maps.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0e1317">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&amp;family=Playfair+Display:ital,wght@0,600;0,700;1,500&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css?v=5"><link rel="stylesheet" href="/assets/css/article.css?v=3">
  <style>
  .skimaps-wrap{{background:var(--paper);padding:clamp(48px,7vw,88px) 0}}
  .skimap-toc{{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;max-width:980px;margin:0 auto 56px}}
  .skimap-toc a{{font:600 .85rem var(--sans);text-decoration:none;color:var(--ink);border:1.5px solid rgba(14,19,23,.18);border-radius:999px;padding:8px 16px}}
  .skimap-toc a:hover{{border-color:var(--red);color:var(--red)}}
  .skimap{{max-width:1160px;margin:0 auto clamp(64px,9vw,110px)}}
  .skimap-head{{max-width:760px;margin:0 auto 26px;text-align:center}}
  .skimap-head h2{{font-size:clamp(1.8rem,3.4vw,2.6rem);letter-spacing:-.03em;margin:4px 0 10px}}
  .skimap-sub{{color:var(--muted);margin:0 0 14px}}
  .skimap-stats{{display:flex;gap:28px;justify-content:center;font-size:.9rem;color:var(--muted);margin:0}} .skimap-stats b{{color:var(--red);font-size:1.15rem}}
  .skimap-img{{display:block}} .skimap-img img{{display:block;width:100%;height:auto;border-radius:3px;box-shadow:0 24px 60px rgba(14,19,23,.18)}}
  .skimap .fine{{text-align:center}}
  .overview{{max-width:1160px;margin:0 auto 72px}} .overview img{{width:100%;height:auto;display:block}}
  .maps-note{{max-width:760px;margin:0 auto;text-align:center;color:var(--muted);font-size:.9rem}}
  </style>
</head>
<body>

{hh}

<main id="top">
  <section class="article-hero">
    {img('val-gardena-night-panorama','Val Gardena at night below the Sassolungo','100vw',cls='bg',eager=True,w=1800,h=1012)}
    <div class="shade"></div>
    <div class="container article-hero-inner">
      <p class="crumbs"><a href="/">Home</a> &nbsp;/&nbsp; <a href="/winter/">Winter</a></p>
      <p class="eyebrow light">Winter 2026/27</p>
      <h1>Dolomites ski &amp; snowboard maps</h1>
      <span class="rule"></span>
      <p class="article-meta">12 Dolomiti Superski areas · the Sella Ronda · one pass</p>
    </div>
  </section>

  <div class="skimaps-wrap"><div class="container">
    <div class="overview">
      <p class="eyebrow center">The whole range</p>
      <h2 class="center">The Dolomites in winter</h2>
      <img src="/assets/img/dolomites-winter-map-1600.jpg" srcset="/assets/img/dolomites-winter-map-1600.jpg 1600w, /assets/img/dolomites-winter-map.jpg 2400w" sizes="(min-width: 1200px) 1160px, 100vw" alt="Illustrated winter map of the Dolomites with peaks, towns and ski villages" width="2400" height="2010" loading="lazy" decoding="async">
    </div>
    <p class="eyebrow center">Jump to a ski area</p>
    <nav class="skimap-toc" aria-label="Ski areas">{toc}</nav>
{chr(10).join(cards)}
    <p class="maps-note">Our maps are illustrated panoramas drawn from open data: runs and lifts © OpenStreetMap contributors, terrain from Mapzen / AWS Terrain Tiles. Run lengths are measured from the mapped runs and differ from official figures. They are for planning only. Always check the official piste map, and run and lift status, on the day. More on the circuit in <a href="/journal/sella-ronda-for-families-and-beginners/">the Sella Ronda for families and beginners</a>.</p>
  </div></div>
</main>

{F}

<script src="/assets/js/main.js?v=3" defer></script>
</body>
</html>
'''
import os; os.makedirs(ROOT+'/ski-maps',exist_ok=True)
open(ROOT+'/ski-maps/index.html','w').write(page); print('ok')

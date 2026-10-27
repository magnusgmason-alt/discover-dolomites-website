"""Compose a Discover Dolomites ski & snowboard panorama: terrain render + SVG overlay."""
import json, math, sys, html, base64, io, numpy as np
from PIL import Image
sys.path.insert(0, '/home/claude/skimaps')
from terrain import Area, paint, render, project

OSM = json.load(open('/home/claude/skimaps/osm.json'))
RED = '#c8202f'
DIFF = {'novice': ('#1f6fd1', 'Easy'), 'easy': ('#1f6fd1', 'Easy'), 'intermediate': ('#d7262e', 'Intermediate'),
        'advanced': ('#121417', 'Difficult'), 'expert': ('#121417', 'Difficult'), 'freeride': ('#f08a00', 'Ski route'),
        'extreme': ('#121417', 'Difficult')}

def esc(s): return html.escape(s or '')
NAMES = {'Saslonch':'Sassolungo','Große Fermeda':'Gran Fermeda','Piz Sëlva':'Piz Selva','Sas dla Porta':'Sass de la Porta'}
GERMANISH = ('Sankt', 'St. ', ' am ', 'ü', 'ö', 'ß', 'Wolken', 'Kastel', 'Seis', 'Gröden', 'Brixen', 'Bruneck', 'Toblach', 'Innichen', 'Sexten', 'Corvara in')
LADIN = ('ë', 'ï', 'Urtij', 'Sëlva', 'Calfosch', 'Badia', 'Ciampedel', 'Cianacei', 'Moena')
def it_name(n):
    parts = [p.strip() for p in n.replace(' – ', ' - ').split(' - ')]
    if len(parts) == 1: return NAMES.get(n, n)
    for p in parts[::-1]:
        if not any(g in p for g in GERMANISH) and not any(l in p for l in LADIN): return p
    return parts[-1]

def build(cfg, out_png, W=3000, H=2000):
    fb = cfg['focus_bbox']
    if 'render_bbox' not in cfg:
        m = cfg.get('margin', 0.13)
        cfg['render_bbox'] = (fb[0] - m * 1.3, fb[1] - m, fb[2] + m * 1.3, fb[3] + m)
    lo0, la0, lo1, la1 = cfg['render_bbox']
    span = max((fb[2] - fb[0]) * 77000, (fb[3] - fb[1]) * 111000)
    cfg.setdefault('cam_dist', span * 1.05)
    cfg.setdefault('cam_h', 2000 + span * 0.62)
    A = Area(lo0, la0, lo1, la1, res=cfg.get('res', 10))
    col, slope = paint(A, light_az=cfg.get('light_az', (cfg['view_az'] - 65) % 360), treeline=cfg.get('treeline', 1950))
    RW, RH = int(W * 1.5), int(H * 1.5)
    im, P = render(A, col, view_az=cfg['view_az'], cam_dist=cfg['cam_dist'], cam_h=cfg['cam_h'],
                   out_w=RW, out_h=RH, fov=cfg.get('fov', 58), exag=cfg.get('exag', 1.3))
    fb = cfg['focus_bbox']
    def infocus(c):
        return any(fb[0] <= p[0] <= fb[2] and fb[1] <= p[1] <= fb[3] for p in c)
    svg = []
    add = svg.append
    global BOUNDS
    BOUNDS = []
    pistes = [w for w in OSM['ways'] if w['k'] == 'p' and infocus(w['c'])]
    sleds = [w for w in OSM['ways'] if w['k'] == 's' and infocus(w['c'])]
    lifts = [w for w in OSM['ways'] if w['k'] == 'a' and w.get('at') not in ('goods', 'zip_line', 'station', 'pylon', 'magic_carpet') and infocus(w['c'])]
    carpets = [w for w in OSM['ways'] if w['k'] == 'a' and w.get('at') == 'magic_carpet' and infocus(w['c'])]

    def path_segments(c, lift=0.0, elev=None):
        lon = np.array([p[0] for p in c]); lat = np.array([p[1] for p in c])
        # densify for occlusion accuracy
        n = len(lon); dl = []
        L, B = [lon[0]], [lat[0]]
        for i in range(1, n):
            dist = math.hypot((lon[i] - lon[i-1]) * 77000, (lat[i] - lat[i-1]) * 111000)
            k = max(1, int(dist / 25))
            for j in range(1, k + 1):
                L.append(lon[i-1] + (lon[i] - lon[i-1]) * j / k); B.append(lat[i-1] + (lat[i] - lat[i-1]) * j / k)
        L = np.array(L); B = np.array(B)
        e = None
        if elev is not None:
            e = np.interp(np.linspace(0, 1, len(L)), [0, 1], elev)
        sx, sy, vis = project(A, P, L, B, elev=e, lift=lift)
        segs, cur = [], []
        for x, y, v in zip(sx, sy, vis):
            if v: BOUNDS.append((x, y))
            if v: cur.append((x, y))
            elif cur:
                if len(cur) > 1: segs.append(cur)
                cur = []
        if len(cur) > 1: segs.append(cur)
        return segs, sx, sy, vis

    def d_of(seg):
        return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in seg)

    # pistes: casing then colour, easy first so harder runs sit on top
    order = {'novice': 0, 'easy': 0, 'intermediate': 1, 'advanced': 2, 'expert': 2, 'extreme': 2, 'freeride': 3}
    pistes.sort(key=lambda w: order.get(w.get('d'), 1))
    psegs = [(w, path_segments(w['c'])[0]) for w in pistes]
    ssegs = [(w, path_segments(w['c'])[0]) for w in sleds]
    bx = np.array(BOUNDS)
    x0, x1 = np.percentile(bx[:, 0], 1), np.percentile(bx[:, 0], 99)
    y0, y1 = np.percentile(bx[:, 1], 1), np.percentile(bx[:, 1], 99)
    mx = (x1 - x0) * 0.10 + 60
    x0 -= mx; x1 += mx; y0 -= (y1 - y0) * 0.32 + 160; y1 += (y1 - y0) * 0.08 + 60
    cw = max(x1 - x0, (y1 - y0) * W / H); ch = cw * H / W
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
    cw = min(cw, RW); ch = min(ch, RH); cw = min(cw, ch * W / H); ch = cw * H / W
    cx0 = min(max(cxm - cw / 2, 0), RW - cw); cy0 = min(max(y1 - ch * 0.97, 0), RH - ch)
    IMC = (int(cx0), int(cy0), int(cx0 + cw), int(cy0 + ch))
    #((int(cx0), int(cy0), int(cx0 + cw), int(cy0 + ch)))
    VB = f'{cx0:.1f} {cy0:.1f} {cw:.1f} {ch:.1f}'
    SC = W / cw
    K = cw / W
    for w, segs in psegs:
        for s in segs:
            add(f'<path d="{d_of(s)}" fill="none" stroke="#ffffff" stroke-opacity=".9" stroke-width="{10*K:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')
    for w, segs in psegs:
        c, _ = DIFF.get(w.get('d'), ('#d7262e', ''))
        dash = ' stroke-dasharray="{14*K:.1f} {9*K:.1f}"' if w.get('d') == 'freeride' else ''
        for s in segs:
            add(f'<path d="{d_of(s)}" fill="none" stroke="{c}" stroke-width="{5.5*K:.2f}" stroke-linecap="round" stroke-linejoin="round"{dash}/>')
    for w, segs in ssegs:
        for s in segs:
            add(f'<path d="{d_of(s)}" fill="none" stroke="#ffffff" stroke-width="{8*K:.2f}" stroke-linecap="round"/>')
            add(f'<path d="{d_of(s)}" fill="none" stroke="#e8a317" stroke-width="{4*K:.2f}" stroke-dasharray="{3*K:.1f} {7*K:.1f}" stroke-linecap="round"/>')
    # lifts: straight lines between end stations, drawn above ground
    lift_labels = []
    for w in lifts + carpets:
        c = w['c']
        ends = [c[0], c[-1]]
        lon = np.array([p[0] for p in ends]); lat = np.array([p[1] for p in ends])
        sx, sy, vis = project(A, P, lon, lat, lift=8)
        # draw if either station is visible
        if not vis.any(): continue
        gond = w.get('at') in ('gondola', 'cable_car', 'mixed_lift')
        add(f'<line x1="{sx[0]:.1f}" y1="{sy[0]:.1f}" x2="{sx[1]:.1f}" y2="{sy[1]:.1f}" stroke="#ffffff" stroke-width="{(7 if gond else 6)*K:.2f}" stroke-linecap="round"/>')
        add(f'<line x1="{sx[0]:.1f}" y1="{sy[0]:.1f}" x2="{sx[1]:.1f}" y2="{sy[1]:.1f}" stroke="#16191c" stroke-width="{(3.6 if gond else 2.6)*K:.2f}" stroke-linecap="round"/>')
        for x, y in zip(sx, sy):
            add(f'<rect x="{x-5*K:.1f}" y="{y-5*K:.1f}" width="{10*K:.1f}" height="{10*K:.1f}" rx="{2*K:.1f}" fill="#16191c" stroke="#fff" stroke-width="{2*K:.2f}"/>')
        if w.get('n') and w.get('at') != 'magic_carpet':
            lift_labels.append((w['n'], (sx[0] + sx[1]) / 2, (sy[0] + sy[1]) / 2, gond))
    # label placement (greedy, avoid overlaps). Boxes in screen px scaled by K into map units.
    taken = []
    def free(b):
        for t in taken:
            if not (b[2] < t[0] or t[2] < b[0] or b[3] < t[1] or t[3] < b[1]): return False
        return True
    def inview(x, y):
        return IMC[0] + 40 * K < x < IMC[2] - 40 * K and IMC[1] + 230 * K < y < IMC[3] - 30 * K
    labels = []
    nvil = 0
    for p in sorted(OSM['places'], key=lambda p: {'city':0,'town':1}.get(p['t'],2)):
        if not (fb[0] - .02 <= p['lon'] <= fb[2] + .02 and fb[1] - .02 <= p['lat'] <= fb[3] + .02): continue
        if p['t'] not in ('town', 'village', 'city'): continue
        if nvil >= 8: break
        if min(abs(q[0] - p['lon']) * 77 + abs(q[1] - p['lat']) * 111 for w in pistes + lifts for q in w['c'][::3]) > 1.2: continue
        sx, sy, vis = project(A, P, [p['lon']], [p['lat']])
        x, y = sx[0], sy[0]
        if not vis[0] or not inview(x, y): continue
        name = it_name(p['n']); w_ = len(name) * 13 + 34
        b = (x - w_ / 2 * K, y - 46 * K, x + w_ / 2 * K, y)
        if free(b):
            taken.append(b); nvil += 1
            labels.append(f'<g transform="translate({x:.1f},{y:.1f}) scale({K:.4f})"><circle r="6" fill="{RED}" stroke="#fff" stroke-width="2.5"/>'
                          f'<rect x="{-w_/2:.1f}" y="-46" width="{w_}" height="34" rx="4" fill="#ffffff" fill-opacity=".93" stroke="#16191c" stroke-width="1.5"/>'
                          f'<text y="-23" text-anchor="middle" class="vil">{esc(name).upper()}</text></g>')
    peaks = sorted([p for p in OSM['peaks'] if fb[0] - 0.05 <= p['lon'] <= fb[2] + 0.05 and fb[1] - 0.05 <= p['lat'] <= fb[3] + 0.05], key=lambda p: -p['e'])
    npk = 0
    for p in peaks:
        if npk >= cfg.get('max_peaks', 12): break
        nm = NAMES.get(p['n'], p['n']); nm = it_name(nm).split(' / ')[0]
        if len(nm) > 22 or nm in ('Hut',): continue
        sx, sy, vis = project(A, P, [p['lon']], [p['lat']], elev=[p['e'] - 30])
        x, y = sx[0], sy[0]
        if not vis[0] or not inview(x, y): continue
        w_ = max(len(nm) * 11.5, 70)
        b = (x - w_ / 2 * K, y - 62 * K, x + w_ / 2 * K, y - 4 * K)
        if not free(b): continue
        taken.append(b); npk += 1
        labels.append(f'<g transform="translate({x:.1f},{y:.1f}) scale({K:.4f})"><path d="M-7,-6 L0,-18 L7,-6 Z" fill="#16191c"/>'
                      f'<text y="-42" text-anchor="middle" class="pk">{esc(nm)}</text>'
                      f'<text y="-24" text-anchor="middle" class="pke">{p["e"]:,} m</text></g>')
    for name, x, y, gond in lift_labels:
        if not inview(x, y): continue
        w_ = len(name) * 9.4 + 16
        b = (x - w_ / 2 * K, y - 13 * K, x + w_ / 2 * K, y + 13 * K)
        if not free(b): continue
        taken.append(b)
        labels.append(f'<g transform="translate({x:.1f},{y:.1f}) scale({K:.4f})"><rect x="{-w_/2:.1f}" y="-13" width="{w_:.1f}" height="26" rx="3" fill="#16191c" fill-opacity=".86"/>'
                      f'<text y="5" text-anchor="middle" class="lf">{esc(name)}</text></g>')
    svg += labels

    stats = dict(pistes=len(pistes), lifts=len(lifts), sleds=len(sleds), km=round(sum(
        sum(math.hypot((w['c'][i][0]-w['c'][i-1][0])*77000, (w['c'][i][1]-w['c'][i-1][1])*111000) for i in range(1, len(w['c']))) for w in pistes) / 1000))
    # compose HTML
    im = im.crop(IMC).resize((W, H), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=90)
    bg = base64.b64encode(buf.getvalue()).decode()
    north = (-cfg['view_az']) % 360
    leg_items = [('#1f6fd1', 'Easy'), ('#d7262e', 'Intermediate'), ('#121417', 'Difficult')]
    leg = ''.join(f'<div class="li"><span class="sw" style="background:{c}"></span>{t}</div>' for c, t in leg_items)
    leg += '<div class="li"><span class="sw dash"></span>Ski route</div><div class="li"><span class="sw sled"></span>Toboggan run</div><div class="li"><span class="lift"></span>Lift</div>'
    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:{W}px;height:{H+190}px;font-family:Montserrat;background:#fff}}
.map{{position:relative;width:{W}px;height:{H}px;background:url(data:image/jpeg;base64,{bg});background-size:cover}}
svg{{position:absolute;inset:0}}
.vil{{font:800 17px Montserrat;letter-spacing:.06em;fill:#16191c}}
.pk{{font:700 19px Montserrat;fill:#16191c;paint-order:stroke;stroke:#fff;stroke-width:5px;stroke-linejoin:round}}
.pke{{font:500 15px Montserrat;fill:#3b4650;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}}
.lf{{font:600 14px Montserrat;fill:#fff}}
.logo{{position:absolute;left:56px;top:46px;line-height:.98;color:#16191c;letter-spacing:-.02em;background:rgba(255,255,255,.88);padding:18px 26px 20px;border-radius:6px}}
.logo .a{{font:500 44px Montserrat;display:block}} .logo .b{{font:800 44px Montserrat;display:block}} .logo i{{color:{RED};font-style:normal}}
.title{{position:absolute;right:56px;top:46px;text-align:right;background:rgba(255,255,255,.9);padding:22px 30px;border-radius:6px;border-top:6px solid {RED}}}
.title .e{{font:700 16px Montserrat;letter-spacing:.2em;color:{RED};text-transform:uppercase}}
.title h1{{margin:8px 0 4px;font:800 54px Montserrat;letter-spacing:-.02em;color:#16191c}}
.title p{{margin:0;font:italic 500 22px 'Playfair Display';color:#3b4650}}
.north{{position:absolute;right:70px;bottom:60px;width:84px;height:84px;border-radius:50%;background:rgba(255,255,255,.9);border:3px solid #16191c}}
.north svg{{position:absolute;inset:0}}
.strip{{height:190px;display:flex;align-items:center;gap:60px;padding:0 56px;border-top:5px solid #16191c;box-sizing:border-box}}
.strip .k{{font:700 15px Montserrat;letter-spacing:.2em;color:{RED};text-transform:uppercase;margin-bottom:12px}}
.legend{{display:grid;grid-template-columns:repeat(3,auto);gap:12px 36px}}
.li{{display:flex;align-items:center;gap:12px;font:600 20px Montserrat;color:#16191c}}
.sw{{width:44px;height:8px;border-radius:4px;box-shadow:0 0 0 2px #fff,0 0 0 3px #ccd}}
.sw.dash{{background:repeating-linear-gradient(90deg,#f08a00 0 12px,transparent 12px 20px)}}
.sw.sled{{background:repeating-linear-gradient(90deg,#e8a317 0 4px,transparent 4px 10px)}}
.lift{{width:44px;height:3px;background:#16191c;position:relative}} .lift:before,.lift:after{{content:"";position:absolute;top:-5px;width:12px;height:12px;background:#16191c;border-radius:2px}} .lift:before{{left:-4px}} .lift:after{{right:-4px}}
.stats{{display:flex;gap:44px}} .stats b{{display:block;font:800 46px Montserrat;color:{RED};letter-spacing:-.02em}} .stats span{{font:500 17px Montserrat;color:#5b6d7a}}
.fine{{margin-left:auto;max-width:520px;font:500 14px/1.5 Montserrat;color:#7b8790}}
</style></head><body><div class="map">
<svg viewBox="{VB}" width="{W}" height="{H}">{"".join(svg)}</svg>
<div class="logo"><span class="a">Discover</span><span class="b">Dolomites<i>.</i></span></div>
<div class="title"><div class="e">Ski &amp; snowboard map · Winter 2026/27</div><h1>{esc(cfg['title'])}</h1><p>{esc(cfg['subtitle'])}</p></div>
<div class="north"><svg viewBox="-42 -42 84 84"><g transform="rotate({north})"><path d="M0,-30 L9,6 L0,0 L-9,6 Z" fill="{RED}"/><path d="M0,30 L9,-6 L0,0 L-9,-6 Z" fill="#16191c"/><text y="-12" x="0" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="13" fill="#16191c" transform="translate(0,-20)">N</text></g></svg></div>
</div><div class="strip">
<div><div class="k">Legend</div><div class="legend">{leg}</div></div>
<div><div class="k">In this map</div><div class="stats"><div><b>{stats['km']} km</b><span>of runs on this map</span></div><div><b>{stats['lifts']}</b><span>lifts</span></div></div></div>
<div class="fine">Illustrated panorama by Discover Dolomites. Runs and lifts © OpenStreetMap contributors (ODbL). Terrain: Mapzen / AWS Terrain Tiles. Not for navigation: check run and lift status locally.</div>
</div></body></html>'''
    open(out_png.replace('.png', '.html'), 'w').write(page)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H + 190})
        pg.goto('file://' + out_png.replace('.png', '.html')); pg.wait_for_timeout(500)
        pg.screenshot(path=out_png); b.close()
    return stats

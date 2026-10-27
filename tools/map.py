#!/usr/bin/env python3
"""Illustrated map of the Dolomites in the Discover map layout.
Positions are real lon/lat (approximate to ~1-2 km). Relief is drawn as classic
mountain symbols; no terrain data is used or implied."""
import math, os, sys

W, MAP_H, STRIP_H = 2400, 1650, 360
H = MAP_H + STRIP_H
LON0, LON1 = 11.0, 12.7
LAT0, LAT1 = 46.04, 46.85          # south, north

PAPER = "#f2eee4"
INK = "#1d2328"
MUTED = "#6b6458"
STONE = "#e6dccb"
STONE_D = "#b7ab94"
LINE = "#5b5346"
RED = "#c8202f"
WATER = "#a9c8d6"
BG_PATH = sys.argv[2] if len(sys.argv) > 2 else ""
ATTRIB = sys.argv[3] if len(sys.argv) > 3 else ""
SAT = bool(BG_PATH)
_ORIG = (INK, PAPER, MUTED)
REGION_C, GROUP_C, LAKE_C, GRAT_C = "#c4bba6", "#8a7f68", "#4c7a91", LINE
if SAT:
    INK, PAPER, MUTED = "#f6f3ea", "#0d1613", "#d6d1c2"
    REGION_C, GROUP_C, LAKE_C, GRAT_C = "#ffffff", "#e9e3d2", "#a8d8ee", "#ffffff"
FONT = "Montserrat, Inter, 'Helvetica Neue', Arial, sans-serif"
SERIF = "'Playfair Display', Georgia, 'Times New Roman', serif"


def X(lon): return (lon - LON0) / (LON1 - LON0) * W
def Y(lat): return (LAT1 - lat) / (LAT1 - LAT0) * MAP_H


# name, lon, lat, tier (0 city, 1 town, 2 village/resort)
TOWNS = [
    ("Bolzano · Bozen", 11.355, 46.498, 0),
    ("Trento", 11.121, 46.067, 0),
    ("Belluno", 12.217, 46.140, 0),
    ("Cortina d’Ampezzo", 12.136, 46.540, 0),
    ("Brixen · Bressanone", 11.656, 46.716, 1),
    ("Bruneck · Brunico", 11.936, 46.796, 1),
    ("Merano · Meran", 11.159, 46.669, 1),
    ("Cavalese", 11.457, 46.290, 2),
    ("Predazzo", 11.603, 46.313, 2),
    ("Moena", 11.659, 46.376, 2),
    ("Canazei", 11.771, 46.477, 2),
    ("Ortisei", 11.672, 46.574, 2),
    ("Selva", 11.760, 46.556, 2),
    ("Corvara", 11.877, 46.551, 2),
    ("Arabba", 11.875, 46.499, 2),
    ("Alleghe", 12.022, 46.403, 2),
    ("Agordo", 12.034, 46.283, 2),
    ("San Martino", 11.800, 46.261, 2),
    ("Dobbiaco", 12.220, 46.733, 2),
    ("San Candido", 12.283, 46.733, 2),
    ("Sesto", 12.357, 46.703, 2),
    ("Misurina", 12.255, 46.583, 2),
    ("Auronzo", 12.443, 46.557, 2),
    ("Pieve di Cadore", 12.372, 46.430, 2),
]

# name, lon, lat, elevation (m), hero
PEAKS = [
    ("Marmolada", 11.851, 46.434, 3343, True),
    ("Antelao", 12.267, 46.464, 3264, False),
    ("Tofana", 12.063, 46.501, 3244, False),
    ("Cristallo", 12.190, 46.575, 3221, False),
    ("Civetta", 12.049, 46.378, 3220, False),
    ("Sorapiss", 12.217, 46.517, 3205, False),
    ("Cimon della Pala", 11.841, 46.280, 3184, False),
    ("Sassolungo", 11.740, 46.510, 3181, False),
    ("Pelmo", 12.135, 46.425, 3168, False),
    ("Piz Boè", 11.822, 46.508, 3152, False),
    ("Sass Rigais", 11.777, 46.634, 3025, False),
    ("Tre Cime di Lavaredo", 12.302, 46.618, 2999, False),
    ("Rosengarten", 11.637, 46.454, 2981, False),
    ("Latemar", 11.586, 46.371, 2842, False),
    ("Schlern", 11.601, 46.525, 2563, False),
    ("Seceda", 11.720, 46.602, 2519, False),
]

# group name, lon, lat (spaced italic caps, no outlines drawn)
GROUPS = [
    ("DOLOMITI DI SESTO", 12.36, 46.675),
    ("PALE DI SAN MARTINO", 11.96, 46.205),
    ("ODLE · GEISLER", 11.80, 46.695),
    ("CADINI", 12.42, 46.60),
    ("CATINACCIO", 11.60, 46.425),
]

PASSES = [
    ("Passo Pordoi", 11.814, 46.487),
    ("Passo Falzarego", 12.007, 46.519),
]

LAKES = [
    ("Lago di Braies", 12.085, 46.694),
    ("Lago di Carezza", 11.576, 46.408),
    ("Lago di Santa Croce", 12.30, 46.10),
]

# fixed region labels: text, x, y (px), size
REGIONS = [
    ("SOUTH TYROL", 330, 520, 54),
    ("ALTO ADIGE", 330, 586, 54),
    ("TRENTINO", 290, 1395, 54),
    ("VENETO", 1880, 1330, 54),
]

out = []
add = out.append


def t(txt, x, y, size, weight=600, fill=INK, anchor="start", extra="", font=FONT,
      halo=True, spacing=None, style=None):
    attrs = f'x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
    if halo:
        attrs += f' stroke="{PAPER}" stroke-width="{max(5, size/5):.1f}" stroke-linejoin="round" paint-order="stroke"'
    if spacing is not None:
        attrs += f' letter-spacing="{spacing}"'
    if style:
        attrs += f' font-style="{style}"'
    add(f'<text {attrs} {extra}>{txt}</text>')


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="Illustrated map of the Dolomites showing the main towns, peaks, passes and lakes">')
add('<title>The Dolomites: illustrated map</title>')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

# defs: paper texture-free gradient
add(f'''<defs>
<radialGradient id="paper" cx="50%" cy="48%" r="75%"><stop offset="0%" stop-color="#f6f2e8"/><stop offset="100%" stop-color="#e9e3d3"/></radialGradient>
<clipPath id="mapclip"><rect width="{W}" height="{MAP_H}"/></clipPath>
</defs>''')
if SAT:
    import base64
    ext = BG_PATH.rsplit(".", 1)[-1].lower().replace("jpg", "jpeg")
    b64 = base64.b64encode(open(BG_PATH, "rb").read()).decode()
    add(f'<image x="0" y="0" width="{W}" height="{MAP_H}" preserveAspectRatio="xMidYMid slice" href="data:image/{ext};base64,{b64}"/>')
    add(f'<rect width="{W}" height="{MAP_H}" fill="#0a120f" fill-opacity=".38"/>')
else:
    add(f'<rect width="{W}" height="{MAP_H}" fill="url(#paper)"/>')
add('<g clip-path="url(#mapclip)">')

# graticule
for lon in (11.5, 12.0, 12.5):
    add(f'<line x1="{X(lon):.1f}" y1="0" x2="{X(lon):.1f}" y2="{MAP_H}" stroke="{GRAT_C}" stroke-opacity="{0.28 if SAT else 0.16}" stroke-width="2" stroke-dasharray="3 12"/>')
for lat in (46.0, 46.5):
    add(f'<line x1="0" y1="{Y(lat):.1f}" x2="{W}" y2="{Y(lat):.1f}" stroke="{GRAT_C}" stroke-opacity="{0.28 if SAT else 0.16}" stroke-width="2" stroke-dasharray="3 12"/>')

PEAK_PREFS = {"Sassolungo": ["l", "bl", "al"], "Tofana": ["b", "bl", "l"], "Sorapiss": ["r", "br"], "Cristallo": ["a", "al"], "Seceda": ["l", "al"]}
TOWN_PREFS = {"Selva": ["r", "br", "b"], "Ortisei": ["l", "al", "a"], "Misurina": ["r", "br"]}
CITY_PREFS = {"Cortina d’Ampezzo": ["a", "ar", "al", "b"]}

# ---------- geometry helpers & label placer ----------
def tw(text, size, weight=600, spacing=0, caps=False):
    k = 0.70 if caps else (0.60 if weight >= 700 else 0.56)
    return len(text) * (size * k + spacing)

obstacles = []   # (x0, y0, x1, y1)

def box_hit(a, b, pad=6):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])

def overlap_area(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[1], b[1])
    return max(0, w) * max(0, h)

def place(marker, lines, prefs):
    prefs = [p for p in prefs]
    """marker: bbox of the symbol. lines: [(text,size,weight)]. Returns (x, ybaseline-list, anchor, bbox)."""
    wmax = max(tw(tx, sz, wt) for tx, sz, wt in lines)
    hs = [sz * 1.18 for _, sz, _ in lines]
    h = sum(hs)
    mx0, my0, mx1, my1 = marker
    cx, cy = (mx0 + mx1) / 2, (my0 + my1) / 2
    g = 10
    cands = {}
    for tag, gg in (("", g), ("2", g + 26), ("3", g + 52)):
        cands.update({
            "r" + tag:  (mx1 + gg, cy - h / 2, "start"),
            "l" + tag:  (mx0 - gg, cy - h / 2, "end"),
            "b" + tag:  (cx, my1 + gg, "middle"),
            "a" + tag:  (cx, my0 - gg - h, "middle"),
            "br" + tag: (mx1 + gg - 8, my1 + gg - 8, "start"),
            "bl" + tag: (mx0 - gg + 8, my1 + gg - 8, "end"),
            "ar" + tag: (mx1 + gg - 8, my0 - gg + 8 - h, "start"),
            "al" + tag: (mx0 - gg + 8, my0 - gg + 8 - h, "end"),
        })
    prefs = list(prefs) + [k + n for n in ("2",) for k in ("r", "l", "b", "a", "br", "bl", "ar", "al")]
    best = None
    for key in prefs:
        x, y, anc = cands[key]
        x0 = x if anc == "start" else (x - wmax if anc == "end" else x - wmax / 2)
        bb = (x0, y, x0 + wmax, y + h)
        if bb[0] < 40 or bb[2] > W - 40 or bb[1] < 70 or bb[3] > MAP_H - 70:
            penalty = 10 ** 7
        else:
            penalty = 0
        for ob in obstacles:
            if box_hit(bb, ob):
                penalty += 1000 + overlap_area(bb, ob)
        if best is None or penalty < best[0]:
            best = (penalty, x, y, anc, bb)
        if penalty == 0:
            break
    pen, x, y, anc, bb = best
    if pen: print('CONFLICT', lines[0][0], int(pen), file=sys.stderr)
    obstacles.append(bb)
    ys, yy = [], y
    for (_, sz, _), hh in zip(lines, hs):
        ys.append(yy + sz * 0.95); yy += hh
    return x, ys, anc, bb

# reserve fixed furniture first
obstacles.append((50, 60, 470, 190))                          # logo
obstacles.append((W - 330, MAP_H - 330, W - 20, MAP_H - 20))  # compass + scale

# region + group labels (fixed)
for name, x, y, size in REGIONS:
    t(name, x, y, size, 700, REGION_C, "start", halo=False, spacing=12, extra='fill-opacity="0.55"' if SAT else "")
    obstacles.append((x, y - size, x + tw(name, size, 700, 12, True) * 0.86, y + 6))
for name, lon, lat in GROUPS:
    x, y = X(lon), Y(lat)
    t(name, x, y, 26, 600, GROUP_C, "middle", halo=True, spacing=6, style="italic")
    wd = tw(name, 26, 600, 6, True) * 0.9
    obstacles.append((x - wd / 2, y - 26, x + wd / 2, y + 8))

# lakes (marker first, label via placer)
lake_items = []
for name, lon, lat in LAKES:
    x, y = X(lon), Y(lat)
    add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="15" ry="9" fill="{WATER}" stroke="#6f9bb0" stroke-width="2.5"/>')
    obstacles.append((x - 17, y - 11, x + 17, y + 11))
    lake_items.append((name, (x - 17, y - 11, x + 17, y + 11)))


def mountain(x, y, elev, hero=False):
    w = 32 + (elev - 2400) * 0.026
    h = w * 0.95
    ax, ay = x, y - h
    lx, rx = x - w / 2, x + w / 2
    body = (f"M{lx:.1f},{y:.1f} L{x - w*.28:.1f},{y - h*.55:.1f} L{x - w*.17:.1f},{y - h*.62:.1f} "
            f"L{ax:.1f},{ay:.1f} L{x + w*.12:.1f},{y - h*.7:.1f} L{x + w*.2:.1f},{y - h*.74:.1f} "
            f"L{x + w*.3:.1f},{y - h*.45:.1f} L{rx:.1f},{y:.1f} Z")
    shade = (f"M{ax:.1f},{ay:.1f} L{x + w*.12:.1f},{y - h*.7:.1f} L{x + w*.2:.1f},{y - h*.74:.1f} "
             f"L{x + w*.3:.1f},{y - h*.45:.1f} L{rx:.1f},{y:.1f} L{x + w*.02:.1f},{y:.1f} L{x - w*.06:.1f},{y - h*.4:.1f} Z")
    sp1 = f"M{x - w*.62:.1f},{y:.1f} L{x - w*.38:.1f},{y - h*.42:.1f} L{x - w*.12:.1f},{y:.1f} Z"
    sp2 = f"M{x + w*.1:.1f},{y:.1f} L{x + w*.46:.1f},{y - h*.36:.1f} L{x + w*.7:.1f},{y:.1f} Z"
    add(f'<path d="{sp1}" fill="{STONE}" stroke="{LINE}" stroke-width="2.5" stroke-linejoin="round"/>')
    add(f'<path d="{sp2}" fill="{STONE_D}" stroke="{LINE}" stroke-width="2.5" stroke-linejoin="round"/>')
    add(f'<path d="{body}" fill="{RED if hero else STONE}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>')
    add(f'<path d="{shade}" fill="{"#8f1722" if hero else STONE_D}"/>')
    add(f'<path d="{body}" fill="none" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>')
    return (x - w * 0.62, y - h, x + w * 0.7, y)


# draw peak symbols north to south so southern symbols overlap northern ones
peak_boxes = {}
for name, lon, lat, elev, hero in sorted(PEAKS, key=lambda p: -p[2]):
    peak_boxes[name] = mountain(X(lon), Y(lat), elev, hero)
    obstacles.append(peak_boxes[name])

# pass + town symbols (obstacles first so labels avoid every marker)
pass_boxes = []
for name, lon, lat in PASSES:
    x, y = X(lon), Y(lat)
    add(f'<path d="M{x-9:.1f},{y+7:.1f} L{x:.1f},{y-9:.1f} L{x+9:.1f},{y+7:.1f} Z" fill="{PAPER}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>')
    bb = (x - 11, y - 11, x + 11, y + 9)
    obstacles.append(bb); pass_boxes.append((name, bb))

town_boxes = []
for name, lon, lat, tier in TOWNS:
    x, y = X(lon), Y(lat)
    r = (11, 8, 5.5)[tier]
    if tier == 0:
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+6}" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>')
        rr = r + 7
    elif tier == 1:
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}" stroke="{PAPER}" stroke-width="3"/>')
        rr = r + 3
    else:
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
        rr = r + 3
    bb = (x - rr, y - rr, x + rr, y + rr)
    obstacles.append(bb); town_boxes.append((name, tier, bb))

# labels, most important first
for name, tier, bb in sorted(town_boxes, key=lambda z: z[1]):
    if tier != 0:
        continue
    x, ys, anc, _ = place(bb, [(name, 33, 800)], CITY_PREFS.get(name, ["r", "l", "a", "b", "ar", "br", "al", "bl"]))
    t(name, x, ys[0], 33, 800, INK, anc)

for name, lon, lat, elev, hero in sorted(PEAKS, key=lambda p: -p[3]):
    bb = peak_boxes[name]
    lines = [(name, 24, 700), (f"{elev:,} m", 19, 500)]
    x, ys, anc, _ = place(bb, lines, PEAK_PREFS.get(name, ["b", "a", "r", "l", "br", "bl", "ar", "al"]))
    t(name, x, ys[0], 24, 700, RED if hero else INK, anc)
    t(f"{elev:,} m", x, ys[1], 19, 500, RED if hero else MUTED, anc)

for name, tier, bb in sorted(town_boxes, key=lambda z: z[1]):
    if tier == 0:
        continue
    fs, fw = (27, 700) if tier == 1 else (21, 600)
    x, ys, anc, _ = place(bb, [(name, fs, fw)], TOWN_PREFS.get(name, ["r", "l", "b", "a", "br", "bl", "ar", "al"]))
    t(name, x, ys[0], fs, fw, INK, anc)

for name, bb in pass_boxes:
    x, ys, anc, _ = place(bb, [(name, 18, 500)], ["a", "b", "r", "l", "ar", "al", "br", "bl"])
    t(name, x, ys[0], 18, 500, MUTED, anc, style="italic")

for name, bb in lake_items:
    x, ys, anc, _ = place(bb, [(name, 19, 500)], ["a", "b", "r", "l", "ar", "al", "br", "bl"])
    t(name, x, ys[0], 19, 500, LAKE_C, anc, style="italic")

add('</g>')

# frame + edge coordinates
add(f'<rect x="14" y="14" width="{W-28}" height="{MAP_H-28}" fill="none" stroke="{INK}" stroke-width="3"/>')
for lon in (11.5, 12.0, 12.5):
    x = X(lon)
    add(f'<line x1="{x:.1f}" y1="14" x2="{x:.1f}" y2="34" stroke="{INK}" stroke-width="3"/>')
    add(f'<line x1="{x:.1f}" y1="{MAP_H-34}" x2="{x:.1f}" y2="{MAP_H-14}" stroke="{INK}" stroke-width="3"/>')
    t(f"{lon:.1f}°E", x, 62, 22, 600, MUTED, "middle", halo=False)
for lat in (46.0, 46.5):
    y = Y(lat)
    add(f'<line x1="14" y1="{y:.1f}" x2="34" y2="{y:.1f}" stroke="{INK}" stroke-width="3"/>')
    add(f'<line x1="{W-34}" y1="{y:.1f}" x2="{W-14}" y2="{y:.1f}" stroke="{INK}" stroke-width="3"/>')
    add(f'<text x="48" y="{y-8:.1f}" font-family="{FONT}" font-size="22" font-weight="600" fill="{MUTED}">{lat:.1f}°N</text>')

# logo
add(f'<text x="64" y="110" font-family="{FONT}" font-size="46" font-weight="500" fill="{INK}" letter-spacing="-1.5">Discover</text>')
add(f'<text x="64" y="158" font-family="{FONT}" font-size="46" font-weight="800" fill="{INK}" letter-spacing="-1.5">Dolomites<tspan fill="{RED}">.</tspan></text>')

# compass rose
cx, cy = W - 170, MAP_H - 190
add(f'<g transform="translate({cx},{cy})">')
add(f'<circle r="74" fill="{PAPER}" fill-opacity=".85" stroke="{INK}" stroke-width="3"/>')
add(f'<path d="M0,-66 L12,0 L0,66 L-12,0 Z" fill="{INK}"/>')
add(f'<path d="M-66,0 L0,-12 L66,0 L0,12 Z" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
add(f'<path d="M0,-66 L12,0 L-12,0 Z" fill="{RED}"/>')
add(f'<text y="-92" font-family="{FONT}" font-size="30" font-weight="800" fill="{INK}" text-anchor="middle">N</text>')
add('</g>')

# scale bar: 25 km
kmpx = W / ((LON1 - LON0) * 111.32 * math.cos(math.radians(46.45)))
bar = 25 * kmpx
sx, sy = W - 170 - bar / 2 - 0, MAP_H - 80
sx = W - 90 - bar
add(f'<g transform="translate({sx:.1f},{sy})">')
add(f'<rect x="0" y="0" width="{bar/2:.1f}" height="12" fill="{INK}"/><rect x="{bar/2:.1f}" y="0" width="{bar/2:.1f}" height="12" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
add(f'<rect x="0" y="0" width="{bar:.1f}" height="12" fill="none" stroke="{INK}" stroke-width="3"/>')
for i, lab in ((0, "0"), (bar / 2, "12.5"), (bar, "25 km")):
    add(f'<text x="{i:.1f}" y="40" font-family="{FONT}" font-size="22" font-weight="600" fill="{INK}" text-anchor="middle">{lab}</text>')
add('</g>')

# ---------- bottom strip ----------
INK, PAPER, MUTED = _ORIG
y0 = MAP_H
add(f'<rect x="0" y="{y0}" width="{W}" height="{STRIP_H}" fill="#ffffff"/>')
add(f'<line x1="0" y1="{y0}" x2="{W}" y2="{y0}" stroke="{INK}" stroke-width="4"/>')
add(f'<text x="64" y="{y0+58}" font-family="{FONT}" font-size="20" font-weight="700" fill="{RED}" letter-spacing="3">MAP · THE DOLOMITES</text>')
add(f'<text x="64" y="{y0+130}" font-family="{FONT}" font-size="64" font-weight="800" fill="{INK}" letter-spacing="-1.5">The Dolomites</text>')
add(f'<text x="64" y="{y0+178}" font-family="{FONT}" font-size="26" font-weight="500" fill="{MUTED}">Northern Italy · nine mountain groups</text>')
add(f'<text x="64" y="{y0+212}" font-family="{FONT}" font-size="26" font-weight="500" fill="{MUTED}">UNESCO World Heritage Site since 2009</text>')

# legend
lx = 880
add(f'<text x="{lx}" y="{y0+58}" font-family="{FONT}" font-size="20" font-weight="700" fill="{INK}" letter-spacing="3">LEGEND</text>')
leg = [
    ("city", "Main city"), ("town", "Town"), ("village", "Village / resort"),
    ("peak", "Peak with height"), ("pass", "Mountain pass"), ("lake", "Lake"),
]
for i, (kind, label) in enumerate(leg):
    col, row = divmod(i, 3)
    x = lx + col * 360
    y = y0 + 106 + row * 52
    if kind == "city":
        add(f'<circle cx="{x+14}" cy="{y-8}" r="17" fill="{PAPER}" stroke="{INK}" stroke-width="3"/><circle cx="{x+14}" cy="{y-8}" r="11" fill="{INK}"/>')
    elif kind == "town":
        add(f'<circle cx="{x+14}" cy="{y-8}" r="8" fill="{INK}"/>')
    elif kind == "village":
        add(f'<circle cx="{x+14}" cy="{y-8}" r="5.5" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
    elif kind == "peak":
        add(f'<path d="M{x-6},{y} L{x+14},{y-34} L{x+34},{y} Z" fill="{STONE}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/><path d="M{x+14},{y-34} L{x+34},{y} L{x+16},{y} Z" fill="{STONE_D}"/>')
    elif kind == "pass":
        add(f'<path d="M{x+4},{y} L{x+14},{y-18} L{x+24},{y} Z" fill="{PAPER}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>')
    elif kind == "lake":
        add(f'<ellipse cx="{x+14}" cy="{y-8}" rx="17" ry="10" fill="{WATER}" stroke="#6f9bb0" stroke-width="2.5"/>')
    add(f'<text x="{x+56}" y="{y}" font-family="{FONT}" font-size="26" font-weight="500" fill="{INK}">{label}</text>')

# stats
stats = [("3,343 m", "Marmolada, the highest peak"), ("18", "peaks above 3,000 metres"), ("5", "provinces share the range")]
for i, (big, small) in enumerate(stats):
    y = y0 + 84 + i * 84
    add(f'<text x="1700" y="{y}" font-family="{FONT}" font-size="52" font-weight="800" fill="{RED}" letter-spacing="-1">{big}</text>')
    add(f'<text x="1990" y="{y-4}" font-family="{FONT}" font-size="24" font-weight="500" fill="{MUTED}">{small}</text>')

add(f'<text x="64" y="{H-34}" font-family="{FONT}" font-size="18" font-weight="500" fill="#8a8478">Illustrated map by Discover Dolomites. Positions are approximate and the map is not for navigation. Check route and lift status locally.{(' ' + ATTRIB) if ATTRIB else ''}</text>')

add('</svg>')

svg = "\n".join(out)
dest = sys.argv[1] if len(sys.argv) > 1 else "dolomites-map.svg"
os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
open(dest, "w", encoding="utf-8").write(svg)
print("wrote", dest, len(svg), "bytes", f"scale {kmpx:.2f} px/km")

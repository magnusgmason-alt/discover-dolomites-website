"""Painted-panorama terrain renderer for Discover Dolomites ski maps.
Elevation: Mapzen/AWS Terrain Tiles (terrarium, z12). Pure numpy/scipy."""
import json, math, numpy as np
from scipy import ndimage as nd
from PIL import Image

DEM = np.load('/home/claude/skimaps/dem.npy').astype(np.float32)
M = json.load(open('/home/claude/skimaps/dem.json'))
Z = M['z']

def lonlat_to_px(lon, lat):
    x = (np.asarray(lon) + 180) / 360 * 2**Z
    r = np.radians(lat)
    y = (1 - np.log(np.tan(r) + 1/np.cos(r)) / np.pi) / 2 * 2**Z
    return (x - M['x0']) * 256, (y - M['y0']) * 256

class Area:
    def __init__(self, lon0, lat0, lon1, lat1, res=12.0):
        self.lat_c = (lat0 + lat1) / 2; self.lon_c = (lon0 + lon1) / 2
        self.kx = 111320 * math.cos(math.radians(self.lat_c)); self.ky = 110540
        self.res = res
        self.x0 = (lon0 - self.lon_c) * self.kx; self.x1 = (lon1 - self.lon_c) * self.kx
        self.y0 = (lat0 - self.lat_c) * self.ky; self.y1 = (lat1 - self.lat_c) * self.ky
        nx = int((self.x1 - self.x0) / res) + 1; ny = int((self.y1 - self.y0) / res) + 1
        xs = self.x0 + np.arange(nx) * res; ys = self.y0 + np.arange(ny) * res
        X, Y = np.meshgrid(xs, ys)
        px, py = lonlat_to_px(self.lon_c + X / self.kx, self.lat_c + Y / self.ky)
        self.h = nd.map_coordinates(DEM, [py, px], order=1, mode='nearest')
        self.h = nd.gaussian_filter(self.h, 0.8)
        self.nx, self.ny = nx, ny
    def to_xy(self, lon, lat):
        return (np.asarray(lon) - self.lon_c) * self.kx, (np.asarray(lat) - self.lat_c) * self.ky
    def grid_idx(self, x, y):
        return (np.asarray(y) - self.y0) / self.res, (np.asarray(x) - self.x0) / self.res

def cast_shadow(h, res, light_az, elev_deg):
    # rotate so light travels along +columns, sweep running horizon
    ang = -(light_az - 270)  # light from light_az; rotate grid so it comes from the left
    hr = nd.rotate(h, ang, order=1, reshape=True, cval=-9999)
    tanE = math.tan(math.radians(elev_deg))
    n = hr.shape[1]
    hz = np.full(hr.shape[0], -1e9, np.float32); sh = np.zeros_like(hr)
    for c in range(n):
        hz = np.maximum(hz - res * tanE, hr[:, c]); sh[:, c] = (hr[:, c] < hz - 2).astype(np.float32)
    sb = nd.rotate(sh, -ang, order=1, reshape=True)
    # crop back to original size (centre)
    oy = (sb.shape[0] - h.shape[0]) // 2; ox = (sb.shape[1] - h.shape[1]) // 2
    sb = sb[oy:oy + h.shape[0], ox:ox + h.shape[1]]
    return nd.gaussian_filter(np.clip(sb, 0, 1), 1.2)

def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def paint(area, light_az, treeline=2050, seed=1):
    h = area.h; r = area.res
    gy, gx = np.gradient(h, r)          # gy along +rows (north), gx east
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    la = math.radians(light_az); le = math.radians(32)
    lx, ly, lz = math.sin(la) * math.cos(le), math.cos(la) * math.cos(le), math.sin(le)
    ex = 2.2
    nx_, ny_, nz_ = -gx * ex, -gy * ex, np.ones_like(h)
    nn = np.sqrt(nx_**2 + ny_**2 + 1)
    lam = np.clip((nx_ * lx + ny_ * ly + nz_ * lz) / nn, 0, 1)
    # broad-scale relief (valleys darker) + local lambert
    hb = nd.gaussian_filter(h, 25)
    ao = np.clip((h - hb) / 250, -1, 1)
    shadow = cast_shadow(h, r, light_az, 26)
    shade = np.clip(0.14 + 0.9 * (lam ** 1.2) * (1 - 0.6 * shadow) + 0.10 * ao, 0, 1)
    rng = np.random.default_rng(seed)
    noise = nd.gaussian_filter(rng.standard_normal(h.shape), 3.0); noise /= noise.std()
    fine = nd.gaussian_filter(rng.standard_normal(h.shape), 0.45); fine /= fine.std()
    # snow base, blue shadows
    snow_lit = np.array([250, 252, 255], np.float32); snow_sh = np.array([108, 138, 182], np.float32)
    s = shade[..., None] ** 0.9
    col = snow_sh + (snow_lit - snow_sh) * s
    # rock on steep slopes (pale dolomite, warm), with snow ledges
    rock_lit = np.array([214, 198, 176], np.float32); rock_sh = np.array([104, 100, 110], np.float32)
    rock = rock_sh + (rock_lit - rock_sh) * s
    rk = smooth(36, 50, slope + noise * 2.5)[..., None] * (1 - 0.25 * smooth(0.8, 1.8, fine)[..., None])
    col = col * (1 - rk) + rock * rk
    # forest below treeline, speckled
    tl = treeline + noise * 60
    fd = smooth(tl + 40, tl - 160, h) * (1 - smooth(36, 46, slope)) * (0.25 + 0.75 * smooth(5, 16, slope + noise * 4))
    speck = smooth(-0.1, 1.0, fine)
    tree = np.array([24, 50, 44], np.float32) * (0.65 + 0.55 * s)
    fk = (fd * (0.4 + 0.55 * speck))[..., None]
    col = col * (1 - fk) + tree * fk
    return np.clip(col, 0, 255), slope

def render(area, col, view_az, cam_dist, cam_h, out_w=2400, out_h=1600, fov=38, depth=None,
           exag=1.25, horizon_frac=0.16, pitch_target=None, haze=(222, 232, 242), sky=((150, 190, 228), (236, 243, 249))):
    """Camera stands cam_dist metres behind the area centre (opposite view_az), cam_h metres above sea,
    looking toward view_az. Returns image, plus projection data for overlays."""
    az = math.radians(view_az)
    fwd = np.array([math.sin(az), math.cos(az)]); right = np.array([math.cos(az), -math.sin(az)])
    cx, cy = 0.0, 0.0
    cam = np.array([cx, cy]) - fwd * cam_dist
    if depth is None:
        depth = cam_dist + 0.75 * max(area.x1 - area.x0, area.y1 - area.y0)
    f = out_w / 2 / math.tan(math.radians(fov / 2))
    # pitch: aim at centre ground
    tgt_h = float(np.median(area.h)) if pitch_target is None else pitch_target
    pitch = math.atan2(cam_h - tgt_h * exag, cam_dist)
    horizon = out_h * horizon_frac
    near = max(200.0, cam_dist - 0.75 * max(area.x1 - area.x0, area.y1 - area.y0))
    K = 2600
    ds = near + (depth - near) * (np.linspace(0, 1, K) ** 1.15)
    cols = np.arange(out_w) - out_w / 2 + 0.5
    D = ds[:, None]
    U = cols[None, :] * D / f
    X = cam[0] + fwd[0] * D + right[0] * U
    Y = cam[1] + fwd[1] * D + right[1] * U
    gi = (Y - area.y0) / area.res; gj = (X - area.x0) / area.res
    inside = (gi >= 0) & (gi <= area.ny - 1) & (gj >= 0) & (gj <= area.nx - 1)
    Hs = nd.map_coordinates(area.h, [gi, gj], order=1, mode='nearest') * exag
    # perspective with pitch: screen y = centre - f*tan(angle)
    ang = np.arctan2(Hs - cam_h, D) + pitch
    SY = out_h / 2 - f * np.tan(ang) + (horizon - out_h / 2) * 0  # centre-based
    SY = np.where(inside, SY, out_h * 3)
    run = np.minimum.accumulate(SY, axis=0)
    img = np.zeros((out_h, out_w, 3), np.float32)
    kidx = np.full((out_h, out_w), -1, np.int32)
    ys = np.arange(out_h)
    for c in range(out_w):
        r = run[:, c]
        k = np.searchsorted(-r, -ys, side='left')    # first k with r[k] <= y
        k = np.where(k < K, k, -1)
        kidx[:, c] = k
    valid = kidx >= 0
    kk = np.where(valid, kidx, 0)
    cc = np.broadcast_to(np.arange(out_w)[None, :], kk.shape)
    gI = gi[kk, cc]; gJ = gj[kk, cc]
    for ch in range(3):
        img[..., ch] = nd.map_coordinates(col[..., ch], [gI, gJ], order=1, mode='nearest')
    # aerial haze by depth
    dfrac = ((ds[kk] - near) / (depth - near))
    hz = (np.clip(dfrac, 0, 1) ** 1.6 * 0.55)[..., None]
    img = img * (1 - hz) + np.array(haze, np.float32) * hz
    # sky
    t = (ys / out_h)[:, None, None]
    skyc = np.array(sky[0], np.float32) * (1 - t) + np.array(sky[1], np.float32) * t
    img = np.where(valid[..., None], img, np.broadcast_to(skyc, img.shape))
    blur = np.stack([nd.gaussian_filter(img[..., c], 2.0) for c in range(3)], -1)
    img = img + 0.55 * (img - blur)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    proj = dict(cam=cam, fwd=fwd, right=right, f=f, pitch=pitch, cam_h=cam_h, exag=exag, out_w=out_w, out_h=out_h,
                run=run, ds=ds)
    return im, proj

def project(area, proj, lon, lat, elev=None, lift=0.0, tol=6.0):
    """Project lon/lat points; returns sx, sy, visible."""
    x, y = area.to_xy(lon, lat)
    x = np.atleast_1d(x); y = np.atleast_1d(y)
    if elev is None:
        gi, gj = area.grid_idx(x, y)
        elev = nd.map_coordinates(area.h, [gi, gj], order=1, mode='nearest')
    dx = x - proj['cam'][0]; dy = y - proj['cam'][1]
    D = dx * proj['fwd'][0] + dy * proj['fwd'][1]
    U = dx * proj['right'][0] + dy * proj['right'][1]
    sx = proj['out_w'] / 2 + U * proj['f'] / D - 0.5 + 0.5
    ang = np.arctan2(np.asarray(elev) * proj['exag'] + lift - proj['cam_h'], D) + proj['pitch']
    sy = proj['out_h'] / 2 - proj['f'] * np.tan(ang)
    # occlusion: compare with running min of terrain in front
    ds = proj['ds']; run = proj['run']
    k = np.clip(np.searchsorted(ds, D) - 3, 0, len(ds) - 1)
    c = np.clip(np.round(sx).astype(int), 0, proj['out_w'] - 1)
    vis = (sy <= run[k, c] + tol) & (sx >= 0) & (sx < proj['out_w']) & (D > ds[0])
    return sx, sy, vis

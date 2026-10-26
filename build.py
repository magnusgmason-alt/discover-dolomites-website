#!/usr/bin/env python3
"""Cloudflare Pages build for discoverdolomites.org.

Copies the static site into dist/ and makes the web-sized images the page
uses (name-800.jpg and name-1800.jpg) from the original photos in photos/.

Cloudflare Pages settings:
  Build command:          pip install pillow && python3 build.py
  Build output directory: dist
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(ROOT, "photos")
DIST = os.path.join(ROOT, "dist")
IMG = os.path.join(DIST, "assets", "img")

# original photo file -> name used by index.html
PHOTO_NAMES = {
    "61b31f16-image.jpg": "autumn-ridge-dusk",
    "7e7eaae4-image.jpg": "averau-portrait",
    "a1323e48-image.jpg": "cable-car",
    "f5325674-image.jpg": "cadini-hero",
    "6c11777b-image.jpg": "cloud-spire",
    "60f3f66b-image.jpg": "forest-mist-peaks",
    "b2f1a631-image.jpg": "hiker-green-slope",
    "3ed35bf5-image.jpg": "pass-road-clouds",
    "7b216c66-image.jpg": "path-hiker",
    "ef2d11a1-image.jpg": "peaks-alpenglow-dark",
    "a3482292-image.jpg": "seceda-aerial",
    "fdce4dc7-image.jpg": "seceda-clouds",
    "46d4b1cd-image.jpg": "seceda-moody",
    "ff3d9055-image.jpg": "ski-hut-siusi",
    "4208be42-image.jpg": "snow-fence-walker",
    "f2bd7901-image.jpg": "spires-cloud-mist",
    "b3886513-image.jpg": "tre-cime-clouds",
    "cc4c1298-image.jpg": "winter-alpenglow",
    "5a332100-image.jpg": "winter-cabin-dusk",
}
SHARE_SOURCE = "f5325674-image.jpg"

# Real covers: put cover-summer.png / cover-winter.png (or .jpg) in photos/.
# Until then a plain placeholder cover is generated from a photo.
COVERS = {
    "cover-summer": ("seceda-aerial", "Summer Edition", "Hiking trails, huts & maps"),
    "cover-winter": ("ski-hut-siusi", "Winter Edition", "Skiing, snowboarding & maps"),
}


def save_sizes(im, name, sizes, quality):
    w, h = im.size
    for target, q in zip(sizes, quality):
        s = min(1.0, target / max(w, h))
        r = im.resize((round(w * s), round(h * s)), Image.LANCZOS) if s < 1 else im
        r.save(os.path.join(IMG, f"{name}-{target}.jpg"), "JPEG", quality=q, optimize=True, progressive=True)


def font(size, bold=False):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def placeholder_cover(photo_name, edition, subtitle):
    src = next(k for k, v in PHOTO_NAMES.items() if v == photo_name)
    im = ImageOps.exif_transpose(Image.open(os.path.join(PHOTOS, src))).convert("RGB")
    im = ImageOps.fit(im, (900, 1350), Image.LANCZOS)
    shade = Image.new("RGBA", im.size, (8, 12, 16, 0))
    d = ImageDraw.Draw(shade)
    for y in range(im.size[1]):
        a = int(150 * (1 - y / 520)) if y < 520 else (int(170 * (y - 900) / 450) if y > 900 else 0)
        d.line([(0, y), (im.size[0], y)], fill=(8, 12, 16, max(0, a)))
    im = Image.alpha_composite(im.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(im)
    d.text((70, 90), "Discover", font=font(64), fill="white")
    d.text((70, 160), "Dolomites", font=font(104, True), fill="white")
    d.rectangle([70, 300, 160, 310], fill=(200, 32, 47))
    d.text((70, 1150), edition.upper(), font=font(46, True), fill="white")
    d.text((70, 1215), subtitle, font=font(34), fill="white")
    return im


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(ROOT, DIST, ignore=shutil.ignore_patterns(
        "dist", "photos", ".git", ".github", "build.py", "README.md", "*.pyc", "__pycache__"))
    os.makedirs(IMG, exist_ok=True)

    for src, name in PHOTO_NAMES.items():
        path = os.path.join(PHOTOS, src)
        if not os.path.exists(path):
            print("MISSING photo:", src, "->", name)
            continue
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        save_sizes(im, name, (1800, 800), (80, 78))
        if src == SHARE_SOURCE:
            ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.45)).save(
                os.path.join(IMG, "share-home.jpg"), "JPEG", quality=84, optimize=True)

    for name, (photo, edition, subtitle) in COVERS.items():
        real = next((os.path.join(PHOTOS, name + ext) for ext in (".png", ".jpg", ".jpeg")
                     if os.path.exists(os.path.join(PHOTOS, name + ext))), None)
        im = Image.open(real).convert("RGB") if real else placeholder_cover(photo, edition, subtitle)
        w, h = im.size
        for tw in (900, 500):
            im.resize((tw, round(h * tw / w)), Image.LANCZOS).save(
                os.path.join(IMG, f"{name}-{tw}.jpg"), "JPEG", quality=86, optimize=True, progressive=True)
        print(name, "real" if real else "placeholder")

    print("built", sum(len(f) for _, _, f in os.walk(DIST)), "files into dist/")


if __name__ == "__main__":
    main()

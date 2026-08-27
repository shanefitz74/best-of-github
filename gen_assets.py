#!/usr/bin/env python3
"""Generate the favicon (SVG) and the social-share OG image (PNG, 1200x630).

Run by build.py so assets stay in sync. Pure stdlib + PIL — no network, no secrets.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
os.makedirs(ASSETS, exist_ok=True)

CYAN = (70, 224, 255)
VIOLET = (168, 120, 255)
INK = (234, 252, 255)
BG = (5, 7, 13)

# ---------------------------------------------------------------------------
# Favicon: the neural glyph as an SVG (tiny, crisp, portable)
# ---------------------------------------------------------------------------
GLYPH = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
  <defs><radialGradient id="cg" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#eafcff"/><stop offset="55%" stop-color="#46e0ff"/><stop offset="100%" stop-color="#a878ff"/>
  </radialGradient></defs>
  <rect width="120" height="120" rx="26" fill="#05070d"/>
  <g stroke="url(#cg)" stroke-width="1.4" opacity=".55" fill="none">
    <path d="M60 60 L60 20 M60 60 L60 100 M60 60 L20 60 M60 60 L100 60 M60 60 L30 30 M60 60 L90 30 M60 60 L30 90 M60 60 L90 90 M30 30 L90 30 M30 30 L30 90 M90 30 L90 90 M30 90 L90 90 M20 60 L100 60"/>
  </g>
  <g fill="url(#cg)">
    <circle cx="60" cy="60" r="8"/><circle cx="60" cy="20" r="4"/><circle cx="60" cy="100" r="4"/>
    <circle cx="20" cy="60" r="4"/><circle cx="100" cy="60" r="4"/>
    <circle cx="30" cy="30" r="3"/><circle cx="90" cy="30" r="3"/><circle cx="30" cy="90" r="3"/><circle cx="90" cy="90" r="3"/>
  </g>
</svg>"""
with open(os.path.join(ASSETS, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(GLYPH)

# ---------------------------------------------------------------------------
# OG image: 1200x630 neon card
# ---------------------------------------------------------------------------
W, H = 1200, 630
img = Image.new("RGB", (W, H), BG)

# soft glows (drawn directly onto img so we keep one draw handle)
d = ImageDraw.Draw(img)
for (cx, cy, r, col) in [(1180, -220, 560, (70, 224, 255)), (-120, 820, 460, (168, 120, 255))]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
# dim the glows back toward the background (composite at low alpha over BG)
glow_layer = Image.new("RGB", (W, H), BG)
d2 = ImageDraw.Draw(glow_layer)
for (cx, cy, r, col) in [(1180, -220, 560, (70, 224, 255)), (-120, 820, 460, (168, 120, 255))]:
    d2.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
img = Image.blend(img, glow_layer, 0.88)  # keep ~12% of the glow tint
d = ImageDraw.Draw(img)                    # RE-BIND draw handle to the final image

# border frame
d.rounded_rectangle([24, 24, W - 24, H - 24], radius=28, outline=(70, 224, 255, 120), width=2)

# glyph (top-left, compact)
gx, gy, gr = 96, 120, 46
d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=CYAN, width=2)
for ang in [0, 45, 90, 135]:
    rad = math.radians(ang)
    ex, ey = gx + gr * math.cos(rad), gy + gr * math.sin(rad)
    d.line([gx, gy, ex, ey], fill=CYAN, width=2)
d.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], fill=INK)

# fonts (prefer Orbitron, fall back to a bundled TTF, then bitmap default)
def load_font(size):
    for path in [
        os.path.join(ASSETS, "fonts", "Orbitron-Variable.ttf"),
        os.path.join(os.path.dirname(__import__("PIL").__file__), "fonts", "DejaVuSans-Bold.ttf"),
        os.path.join(os.path.dirname(__import__("PIL").__file__), "fonts", "DejaVuSans.ttf"),
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

big = load_font(86)
med = load_font(30)

d.text((200, 92), "BEST OF GITHUB", font=big, fill=INK)
d.text((202, 196), "The Week in Code", font=med, fill=INK)
d.text((202, 262),
       "The repositories that gained the most stars this week -", font=med, fill=(159, 178, 214))
d.text((202, 300),
       "ranked by signal, rendered in neon.", font=med, fill=(159, 178, 214))

# footer chip
d.rounded_rectangle([200, 538, 558, 596], radius=20, outline=(70, 224, 255, 150), width=2)
d.text((228, 552), "WEEKLY  -  FRESH  -  ON FIRE  -  NEURAL MAP", font=med, fill=CYAN)

img.save(os.path.join(ASSETS, "og-image.png"), "PNG")
print("wrote assets/favicon.svg and assets/og-image.png")

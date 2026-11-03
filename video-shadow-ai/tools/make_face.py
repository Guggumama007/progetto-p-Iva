"""Texture 'volto' del contratto: inchiostro su trasparente (righe, titolo, firma, occhi).
Varianti degli occhi per le espressioni: aperti, chiusi (blink), preoccupati."""
from PIL import Image, ImageDraw, ImageFilter
import math, sys
W, H = 840, 1188  # A4 in proporzione

def face(eyes="open", out="blender/tex/face_open.png"):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ink = (22, 26, 38, 255); soft = (22, 26, 38, 150); copper = (170, 70, 30, 255)
    # titolo e righe del testo (sotto gli occhi)
    d.rounded_rectangle((250, 120, 590, 142), 10, fill=ink)
    for i, wdt in enumerate([520, 560, 500, 545, 470, 530, 380]):
        y = 610 + i * 52; x0 = (W - 560) // 2
        d.rounded_rectangle((x0, y, x0 + wdt, y + 14), 7, fill=soft)
    # firma ramata
    pts = [(470 + t * 4, 1035 + 22 * math.sin(t / 5.5) - t * 0.6) for t in range(60)]
    d.line(pts, fill=copper, width=7, joint="curve")
    d.line((440, 1075, 740, 1075), fill=soft, width=4)
    # occhi
    cx = (W // 2 - 120, W // 2 + 120); cy = 380
    for x in cx:
        if eyes == "open":
            d.ellipse((x - 42, cy - 62, x + 42, cy + 62), fill=ink)
            d.ellipse((x + 6, cy - 40, x + 26, cy - 18), fill=(255, 255, 255, 255))
        elif eyes == "closed":
            d.arc((x - 46, cy - 20, x + 46, cy + 40), 200, 340, fill=ink, width=14)
        elif eyes == "worried":
            d.ellipse((x - 40, cy - 52, x + 40, cy + 60), fill=ink)
            d.ellipse((x + 4, cy - 30, x + 22, cy - 12), fill=(255, 255, 255, 255))
            s = -1 if x < W // 2 else 1  # sopracciglia inclinate
            d.line((x - 50, cy - 95 - 18 * s, x + 50, cy - 95 + 18 * s), fill=ink, width=14)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    im.save(out)

for e in ("open", "closed", "worried"):
    face(e, f"blender/tex/face_{e}.png")
print("ok")

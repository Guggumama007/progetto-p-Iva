"""Texture degli schermi di carta: il chatbot 'gratis' trovato online e l'assistente aziendale approvato.
Marchi di fantasia, nessun prodotto reale."""
from PIL import Image, ImageDraw, ImageFont
W, H = 1024, 640
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def bubble(d, box, fill, r=26): d.rounded_rectangle(box, r, fill=fill)
def lines(d, x, y, n, w, col, step=26):
    for i in range(n): d.rounded_rectangle((x, y + i * step, x + w - (i % 3) * 60, y + i * step + 10), 5, fill=col)

# 1) chatbot gratis: colori sgargianti, stelline, "100% GRATIS"
im = Image.new("RGB", (W, H), (250, 246, 236)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 92), fill=(255, 214, 64))
d.text((36, 22), "ChatGratis", font=ImageFont.truetype(F, 46), fill=(30, 30, 40))
d.text((330, 34), "✦ AI ✦  100% GRATIS!", font=ImageFont.truetype(F, 30), fill=(200, 40, 90))
bubble(d, (40, 130, 600, 230), (235, 228, 255)); d.text((70, 160), "Ciao! Incollami pure tutto :)", font=ImageFont.truetype(FR, 32), fill=(60, 40, 120))
bubble(d, (380, 270, 984, 470), (220, 232, 245)); lines(d, 410, 300, 6, 540, (110, 120, 140))
d.rounded_rectangle((40, 520, 984, 600), 30, outline=(200, 190, 170), width=4, fill=(255, 255, 255))
d.text((76, 540), "Incolla qui il tuo testo...", font=ImageFont.truetype(FR, 30), fill=(160, 150, 140))
im.save("blender/tex/screen_gratis.png")

# 2) assistente aziendale: sobrio, lucchetto, "dati in sede"
im = Image.new("RGB", (W, H), (244, 241, 234)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 92), fill=(20, 31, 46))
d.text((36, 24), "Assistente aziendale", font=ImageFont.truetype(F, 40), fill=(244, 241, 234))
d.rounded_rectangle((690, 26, 984, 66), 20, fill=(181, 86, 42)); d.text((712, 30), "🔒 dati in sede", font=ImageFont.truetype(F, 26), fill=(255, 255, 255))
bubble(d, (40, 130, 640, 230), (230, 224, 212)); d.text((70, 160), "Approvato dall'azienda.", font=ImageFont.truetype(FR, 32), fill=(20, 31, 46))
bubble(d, (380, 270, 984, 470), (228, 234, 240)); lines(d, 410, 300, 6, 540, (90, 100, 120))
d.rounded_rectangle((40, 520, 984, 600), 30, outline=(181, 86, 42), width=4, fill=(255, 255, 255))
d.text((76, 540), "Scrivi qui. Restiamo in azienda.", font=ImageFont.truetype(FR, 30), fill=(140, 130, 120))
im.save("blender/tex/screen_azienda.png")
print("ok")

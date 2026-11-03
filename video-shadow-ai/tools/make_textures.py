"""Texture procedurali per Blender: pagina di contratto."""
from PIL import Image, ImageDraw, ImageFont
import random
random.seed(7)
W,H=1240,1754
im=Image.new("RGB",(W,H),(246,244,238)); d=ImageDraw.Draw(im)
fb=ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",46)
fr=ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",24)
d.text((W//2,150),"CONTRATTO DI FORNITURA",font=fb,fill=(30,32,40),anchor="mm")
d.text((W//2,210),"tra Alfa S.r.l. e Beta S.p.A.",font=fr,fill=(70,70,80),anchor="mm")
y=300
words="il presente accordo disciplina le condizioni di fornitura dei servizi tra le parti secondo quanto previsto dagli articoli seguenti e nel rispetto della normativa vigente in materia di riservatezza dei dati".split()
for art in range(1,7):
    d.text((120,y),f"Art. {art}",font=fb.font_variant(size=28),fill=(30,32,40)); y+=50
    for _ in range(random.randint(4,7)):
        line=" ".join(random.choice(words) for _ in range(random.randint(11,14)))
        d.text((120,y),line[:92],font=fr,fill=(60,62,72)); y+=36
    y+=24
    if y>H-260: break
d.line((760,H-180,1100,H-180),fill=(40,40,60),width=2)
d.text((760,H-165),"Firma",font=fr,fill=(90,90,100))
# firma a mano
pts=[(790+i*6, H-205+int(18*__import__('math').sin(i/3.0))) for i in range(45)]
d.line(pts,fill=(25,35,90),width=3)
im.save("blender/tex/contratto.png")
print("ok")

"""Genera il progetto HyperFrames (montaggio finale) da timeline.json.
Ricalcola tutto quando cambia la voce: python3 tools/build_hyperframes.py
Struttura: index.html (clip video, audio, host delle scene) + compositions/*.html (grafiche GSAP).
Linguaggio visivo: cartellini di carta ritagliata (crema #f1ebde, inchiostro #1c2230, rame #b5562a),
EB Garamond per i titoli, Inter per etichette e sottotitoli, IBM Plex Mono per l'orologio."""
import json, os, re, html

ROOT = "/home/user/APEX-AI-Terminal/video-shadow-ai"
HF = f"{ROOT}/hyperframes"
os.makedirs(f"{HF}/compositions", exist_ok=True)
tl = json.load(open(f"{ROOT}/timeline.json"))
src = open(f"{ROOT}/blender/paperlib.py").read()   # stessa funzione word_time usata nelle scene Blender
exec(src[src.index("def word_time"):src.index("def tag_card")])

S = {s["id"]: s for s in tl["scenes"]}
LN = lambda sid: [l for l in tl["lines"] if l["scene"] == sid]
D = tl["duration"]
r3 = lambda x: f"{x:.3f}"

PAPER_CSS = """
  .tag { position:absolute; background:#f1ebde url(assets/paper.png); background-blend-mode:multiply; color:#1c2230;
         box-shadow: 0 3px 0 rgba(60,40,20,.25), 0 14px 30px rgba(0,0,0,.28); border-radius:3px; }
  .tag.cu { background-color:#b5562a; color:#fbf4ea; }
  .tag.navy { background-color:#16233a; color:#f1ebde; }
  .lbl { font-family:'Inter'; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }
  .ttl { font-family:'EB Garamond'; font-weight:700; letter-spacing:-.01em; }
"""

def scene_file(cid, dur, body, script, extra_css=""):
    open(f"{HF}/compositions/{cid}.html", "w").write(f"""<template>
<style>
  #{cid} {{ position:absolute; inset:0; overflow:visible; }}
{PAPER_CSS}{extra_css}
</style>
<div id="{cid}" data-composition-id="{cid}" data-width="1920" data-height="1080">
{body}
</div>
<script>
  const tl = gsap.timeline({{ paused: true }});
{script}
  window.__timelines["{cid}"] = tl;
</script>
</template>
""")

hosts = []  # (id, start, duration, kind)
def host(cid, start, dur, kind="graphics"): hosts.append((cid, start, dur, kind))

# ---------------------------------------------------------------- 1. etichetta del corso (tutto il film tranne il cartello)
hud_d = S["cartello"]["start"]
scene_file("hud", hud_d, """  <div id="hud-tag" class="tag navy lbl" style="left:84px; top:70px; padding:12px 20px; font-size:28px; transform:rotate(-1.5deg)">Usare l'IA in sicurezza · Lezione 3</div>""",
f"""  tl.fromTo("#hud-tag", {{opacity:0, filter:"blur(6px)"}}, {{opacity:1, filter:"blur(0px)", duration:0.2, ease:"power4.out"}}, 0.4);
  tl.to("#hud-tag", {{opacity:0, duration:0.15}}, {r3(hud_d - 0.3)});""")
host("hud", 0, hud_d)

# ---------------------------------------------------------------- 2. orologio 09:15 (buongiorno)
b0 = S["buongiorno"]
digits = "".join(f'<span class="dg" id="clk-d{i}" style="display:inline-block">{c}</span>' for i, c in enumerate("09:15"))
scene_file("clock", b0["end"] - b0["start"], f"""  <div id="clk" class="tag" style="right:110px; top:90px; padding:18px 34px 14px; transform:rotate(2deg); font-family:'IBM Plex Mono'; font-weight:700; font-size:118px; line-height:1">{digits}</div>""",
"""  tl.fromTo("#clk", {opacity:0, y:-40, rotation:8}, {opacity:1, y:0, rotation:2, duration:0.55, ease:"back.out(1.5)"}, 0.15);
  ["#clk-d0","#clk-d1","#clk-d2","#clk-d3","#clk-d4"].forEach((s,i)=> tl.fromTo(s, {opacity:0, y:22}, {opacity:1, y:0, duration:0.14, ease:"power3.out"}, 0.35 + i*0.06));
  tl.to("#clk-d2", {opacity:0.25, duration:0.01, yoyo:true, repeat:5, repeatDelay:0.49}, 1.0);
  tl.to("#clk", {opacity:0, y:-24, filter:"blur(6px)", duration:0.2, ease:"power2.in"}, 4.6);""")
host("clock", b0["start"], b0["end"] - b0["start"])

# ---------------------------------------------------------------- 3. "Nessuno": cartellini con punto interrogativo che cade
n0 = S["nessuno"]; nl = LN("nessuno"); loc = lambda t: t - n0["start"]
tv = loc(word_time(nl[0], "vietato", "start")) - 0.1; ta = loc(word_time(nl[0], "autorizzato", "start")) - 0.1
shrug = loc(nl[0]["end"]) + 0.05; tc = loc(word_time(nl[1], "chiesto", "start"))
scene_file("nessuno", n0["end"] - n0["start"], """
  <div id="ns-a" class="tag lbl" style="left:180px; top:300px; padding:22px 30px; font-size:54px; transform-origin:50% -60px">Vietato<span id="ns-qa" style="display:inline-block; color:#9a3f17">?</span></div>
  <div id="ns-b" class="tag lbl" style="right:150px; top:360px; padding:22px 30px; font-size:54px; transform-origin:50% -60px">Autorizzato<span id="ns-qb" style="display:inline-block; color:#9a3f17">?</span></div>
  <div id="ns-c" class="tag cu ttl" style="left:0; right:0; margin:auto; width:560px; top:150px; padding:16px 0; text-align:center; font-size:64px; font-style:italic">…nessuno ha chiesto.</div>""",
f"""  tl.fromTo("#ns-a", {{opacity:0, y:-260, rotation:-14}}, {{opacity:1, y:0, rotation:-4, duration:0.6, ease:"back.out(1.7)"}}, {r3(tv)});
  tl.fromTo("#ns-b", {{opacity:0, y:-260, rotation:14}}, {{opacity:1, y:0, rotation:3, duration:0.6, ease:"back.out(1.7)"}}, {r3(ta)});
  // spallucce: i punti interrogativi cadono
  tl.fromTo("#ns-qa", {{y:0, rotation:0}}, {{y:520, rotation:-160, duration:0.7, ease:"power2.in"}}, {r3(shrug)});
  tl.fromTo("#ns-qb", {{y:0, rotation:0}}, {{y:480, rotation:190, duration:0.75, ease:"power2.in"}}, {r3(shrug + 0.08)});
  tl.to(["#ns-a","#ns-b"], {{rotation:"+=6", duration:0.18, yoyo:true, repeat:1, ease:"sine.inOut"}}, {r3(shrug)});
  tl.to(["#ns-a","#ns-b"], {{opacity:0, y:-30, filter:"blur(6px)", duration:0.2, ease:"power2.in", stagger:0.05}}, {r3(tc - 0.6)});
  tl.fromTo("#ns-c", {{opacity:0, scale:1.08, filter:"blur(8px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:0.18, ease:"power4.out"}}, {r3(tc - 0.35)});
  tl.to("#ns-c", {{opacity:0, filter:"blur(6px)", duration:0.18}}, {r3(n0["end"] - n0["start"] - 0.25)});""")
host("nessuno", n0["start"], n0["end"] - n0["start"])

# ---------------------------------------------------------------- 4. lampo bianco tunnel -> sala server
v0 = S["viaggio"]; tsrv = v0["start"] + 3.3
scene_file("flash", 0.8, """  <div id="fl" style="position:absolute; inset:0; background:#f6efe2"></div>""",
"""  tl.fromTo("#fl", {opacity:0}, {opacity:1, duration:0.18, ease:"power3.in"}, 0.0);
  tl.to("#fl", {opacity:0, duration:0.45, ease:"power2.out"}, 0.3);""")
host("flash", tsrv - 0.3, 0.8)

# ---------------------------------------------------------------- 5. SHADOW AI, lettere di carta ritagliata
m0 = S["nome"]; ml = LN("nome")[0]
tw = word_time(ml, "Shadow", "start") - m0["start"]
letters = ""; js = ""
for i, ch in enumerate("SHADOW AI"):
    if ch == " ": letters += '<span style="display:inline-block; width:46px"></span>'; continue
    rot = [-6, 4, -3, 7, -5, 3, 0, -4, 6][i]; col = "cu" if ch in "AI" and i > 6 else ""
    letters += f'<span id="sh-{i}" class="tag ttl {col}" style="position:relative; display:inline-block; margin:0 6px; padding:6px 22px 0; font-size:190px; line-height:1.05; transform:rotate({rot}deg)">{ch}</span>'
    js += f'  tl.fromTo("#sh-{i}", {{opacity:0, y:-120, scale:1.25}}, {{opacity:1, y:0, scale:1, duration:0.32, ease:"back.out(2)"}}, {r3(tw + i * 0.055)});\n'
scene_file("shadow", m0["end"] - m0["start"], f"""  <div id="sh-row" style="position:absolute; left:0; right:0; top:330px; text-align:center; white-space:nowrap">{letters}</div>
  <div id="sh-sub" class="tag lbl" style="left:0; right:0; margin:auto; width:620px; top:640px; padding:14px 0; text-align:center; font-size:34px">IA usata senza permesso</div>""",
js + f"""  tl.fromTo("#sh-sub", {{opacity:0, filter:"blur(6px)"}}, {{opacity:1, filter:"blur(0px)", duration:0.2}}, {r3(tw + 0.3)});
  tl.to(["#sh-row","#sh-sub"], {{opacity:0, filter:"blur(8px)", duration:0.2, ease:"power2.in"}}, {r3(m0["end"] - m0["start"] - 0.25)});""",
"\n  #sh-row .tag { position: relative; }")
host("shadow", m0["start"], m0["end"] - m0["start"])

# ---------------------------------------------------------------- 6. Il rischio è doppio: due colonne di cartellini
r0 = S["rischio"]; rl = LN("rischio"); loc = lambda t: t - r0["start"]
items = [  # (id, testo, classe, x, y, rot, istante)
    ("rk-h", "Il rischio è doppio", "ttl", None, 120, -1, loc(rl[0]["start"]) + 0.1),
    ("rk-a", "Per l'azienda", "cu lbl", 150, 300, -2, loc(word_time(rl[1], "azienda", "start")) - 0.15),
    ("rk-a1", "Dati dei clienti esposti", "ttl", 150, 400, 1.5, loc(word_time(rl[1], "dati", "start"))),
    ("rk-a2", "Informazioni riservate fuori controllo", "ttl", 150, 500, -1, loc(word_time(rl[1], "informazioni", "start"))),
    ("rk-b", "Per te", "cu lbl", 1180, 300, 2, loc(word_time(rl[2], "Per te", "start")) - 0.1),
    ("rk-b1", "Errori che firmi tu", "ttl", 1180, 400, -1.5, loc(word_time(rl[2], "errori", "start"))),
    ("rk-b2", "Regole aziendali violate", "ttl", 1180, 500, 1, loc(word_time(rl[2], "regole", "start"))),
]
body = ""; js = ""
for (i, t, c, x, y, rot, at) in items:
    pos = f"left:{x}px;" if x is not None else "left:0; right:0; margin:auto; width:820px; text-align:center;"
    size = "font-size:76px; padding:10px 34px 6px;" if i == "rk-h" else ("font-size:30px; padding:12px 22px;" if "lbl" in c else "font-size:44px; padding:12px 26px 8px; max-width:600px;")
    body += f'  <div id="{i}" class="tag {c}" style="{pos} top:{y}px; {size} transform:rotate({rot}deg)">{html.escape(t)}</div>\n'
    js += f'  tl.fromTo("#{i}", {{opacity:0, x:{-40 if (x or 0) < 960 else 40}, filter:"blur(8px)"}}, {{opacity:1, x:0, filter:"blur(0px)", duration:0.35, ease:"expo.out"}}, {r3(at)});\n'
ts = loc(rl[3]["start"]) - 0.05
body += '  <div id="rk-st" class="lbl" style="position:absolute; left:1240px; top:640px; padding:14px 26px; font-size:34px; color:#b5562a; border:7px solid #b5562a; border-radius:10px; transform:rotate(-9deg); opacity:0; background:rgba(241,235,222,.85)">Firmato: tu</div>\n'
js += f"""  tl.to("#rk-h", {{opacity:0, y:-20, filter:"blur(6px)", duration:0.2}}, {r3(items[1][6] - 0.3)});
  tl.fromTo("#rk-st", {{opacity:0, scale:2.2, rotation:-20}}, {{opacity:1, scale:1, rotation:-9, duration:0.16, ease:"power4.in"}}, {r3(ts + 0.35)});
  tl.to(["#rk-a","#rk-a1","#rk-a2","#rk-b","#rk-b1","#rk-b2","#rk-st"], {{opacity:0, filter:"blur(8px)", duration:0.22, ease:"power2.in", stagger:0.03}}, {r3(r0["end"] - r0["start"] - 0.45)});"""
scene_file("rischio", r0["end"] - r0["start"], body, js)
host("rischio", r0["start"], r0["end"] - r0["start"])

# ---------------------------------------------------------------- 7. Riavvolgiamo
w0 = S["riavvolgi"]; wd = w0["end"] - w0["start"]
scene_file("rewind", wd, """
  <div id="rw-veil" style="position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(255,255,255,.06) 0 2px, transparent 2px 6px)"></div>
  <div id="rw-tag" class="tag ttl" style="left:0; right:0; margin:auto; width:760px; top:380px; padding:18px 0 10px; text-align:center; font-size:110px"><span style="color:#9a3f17">◀◀</span> Riavvolgiamo</div>
  <div id="rw-clk" class="tag" style="right:110px; top:90px; padding:14px 30px 10px; font-family:'IBM Plex Mono'; font-weight:700; font-size:96px; transform:rotate(2deg)"><span id="rw-t">09:47</span></div>""",
f"""  tl.fromTo("#rw-veil", {{opacity:0}}, {{opacity:1, duration:0.1}}, 0);
  tl.fromTo("#rw-tag", {{opacity:0, x:120, filter:"blur(14px)"}}, {{opacity:1, x:0, filter:"blur(0px)", duration:0.3, ease:"expo.out"}}, 0.25);
  tl.fromTo("#rw-clk", {{opacity:0}}, {{opacity:1, duration:0.15}}, 0.1);
  const clock = {{m: 47}};
  tl.fromTo(clock, {{m: 47}}, {{m: 15, duration: {r3(wd - 0.6)}, ease:"power2.out", onUpdate: () => {{ document.getElementById("rw-t").textContent = "09:" + String(Math.round(clock.m)).padStart(2, "0"); }} }}, 0.1);
  tl.to(["#rw-tag","#rw-veil","#rw-clk"], {{opacity:0, filter:"blur(8px)", duration:0.18, ease:"power2.in"}}, {r3(wd - 0.25)});""")
host("rewind", w0["start"], wd)

# ---------------------------------------------------------------- 8. "Stessi 30 secondi" (finale)
f0 = S["finale"]; fl = LN("finale"); loc = lambda t: t - f0["start"]
t30 = loc(word_time(fl[0], "trenta", "start"))
scene_file("trenta", f0["end"] - f0["start"], """  <div id="tr-tag" class="tag" style="right:130px; top:110px; padding:16px 28px 12px; transform:rotate(-2deg)">
    <div class="lbl" style="font-size:28px; color:#9a3f17">Stesso tempo</div>
    <div style="font-family:'IBM Plex Mono'; font-weight:700; font-size:84px; line-height:1">00:30 <svg width="62" height="56" viewBox="0 0 62 56" style="vertical-align:-4px"><path d="M6 30 L24 48 L56 8" fill="none" stroke="#9a3f17" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>""",
f"""  tl.fromTo("#tr-tag", {{opacity:0, y:-50, rotation:-10}}, {{opacity:1, y:0, rotation:-2, duration:0.5, ease:"back.out(1.6)"}}, {r3(t30 - 0.2)});
  tl.to("#tr-tag", {{opacity:0, filter:"blur(6px)", duration:0.18}}, {r3(loc(fl[1]["start"]) - 0.1)});""")
host("trenta", f0["start"], f0["end"] - f0["start"])

# ---------------------------------------------------------------- 9. cartello finale (solo il corso)
c0 = S["cartello"]; cd = D - c0["start"]
ecbg = "#141f2e url(assets/endcard_bg.png) center/cover" if os.path.exists(f"{HF}/assets/endcard_bg.png") else "#141f2e"   # fondale ComfyUI
scene_file("endcard", cd, f"""
  <div id="ec-bg" style="position:absolute; inset:0; background:{ecbg}"></div>
  <div id="ec-k" class="lbl" style="position:absolute; left:160px; top:320px; font-size:30px; color:#d58a52">Corso · Lezione 3</div>
  <div id="ec-t" class="ttl" style="position:absolute; left:160px; top:380px; font-size:118px; color:#f4f1ea; line-height:1.02">Usare l'IA<br>in sicurezza</div>
  <div id="ec-r" style="position:absolute; left:160px; top:660px; width:0; height:6px; background:#b5562a"></div>
  <div id="ec-s" style="position:absolute; left:160px; top:690px; font-family:'Inter'; font-size:34px; color:#c8cdd6">Shadow AI: il contratto che resta a casa.</div>""",
"""  tl.fromTo("#ec-bg", {opacity:0}, {opacity:1, duration:0.35, ease:"power2.inOut"}, 0);
  tl.fromTo("#ec-k", {opacity:0, filter:"blur(6px)"}, {opacity:1, filter:"blur(0px)", duration:0.18}, 0.35);
  tl.fromTo("#ec-t", {opacity:0, filter:"blur(8px)"}, {opacity:1, filter:"blur(0px)", duration:0.2, ease:"power4.out"}, 0.45);
  tl.fromTo("#ec-r", {width:0}, {width:420, duration:0.5, ease:"expo.out"}, 0.7);
  tl.fromTo("#ec-s", {opacity:0, filter:"blur(6px)"}, {opacity:1, filter:"blur(0px)", duration:0.2}, 0.9);""")
host("endcard", c0["start"], cd)

# ---------------------------------------------------------------- 10. sottotitoli: gruppi di 3-6 parole, uno alla volta
groups = []
for l in tl["lines"]:
    words = l["caption"].split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 6 or (len(cur) >= 3 and re.search(r"[.,:;!?…]$", w)): chunks.append(cur); cur = []
    if cur:
        if chunks and len(cur) < 2: chunks[-1] += cur
        else: chunks.append(cur)
    pos = 0; text = l["caption"]; wi = 0
    W = l.get("words") if l.get("words") and len(l["words"]) == len(words) else None   # tempi faster-whisper
    for ch in chunks:
        first, last = ch[0], ch[-1]
        i0 = text.find(first, pos); i1 = text.find(last, i0) + len(last); pos = i1
        # tempi per proporzione di caratteri dentro i segmenti VAD della battuta
        def at(ci):
            segs = l.get("pauses") or [[0, l["speech"]]]; total = sum(b - a for a, b in segs); target = ci / len(text) * total; acc = 0
            for a, b in segs:
                if acc + (b - a) >= target: return l["start"] + a + (target - acc)
                acc += b - a
            return l["end"]
        if W: groups.append((" ".join(ch), W[wi]["start"], W[wi + len(ch) - 1]["end"]))
        else: groups.append((" ".join(ch), at(i0), at(i1)))
        wi += len(ch)
cap_body = ""; cap_js = ""
for k, (txt, a, b) in enumerate(groups):
    nxt = groups[k + 1][1] if k + 1 < len(groups) else D
    end = min(b + 0.35, nxt - 0.02)
    cap_body += f'  <div id="cg{k}" class="cg"><span>{html.escape(txt)}</span></div>\n'
    cap_js += (f'  tl.fromTo("#cg{k}", {{opacity:0}}, {{opacity:1, duration:0.1}}, {r3(max(0.1, a - 0.05))});\n'
               f'  tl.to("#cg{k}", {{opacity:0, duration:0.1, ease:"power2.in"}}, {r3(end - 0.1)});\n'
               f'  tl.set("#cg{k}", {{opacity:0, visibility:"hidden"}}, {r3(end)});\n')
scene_file("captions", D, cap_body, cap_js, """
  .cg { position:absolute; left:0; right:0; bottom:92px; text-align:center; }
  .cg span { display:inline-block; font-family:'Inter'; font-weight:600; font-size:40px; color:#fbf6ec; padding:10px 22px; border-radius:10px;
             background:rgba(16,24,40,.62); }""")

# ---------------------------------------------------------------- index.html: clip, audio, host
clips = [("buongiorno", S["buongiorno"]["start"], S["buongiorno"]["end"]), ("fretta", S["fretta"]["start"], S["fretta"]["end"]),
         ("nessuno", S["nessuno"]["start"], S["nessuno"]["end"]), ("tunnel", S["viaggio"]["start"], tsrv + 0.05),
         ("server", tsrv, S["nome"]["end"]), ("copie", S["rischio"]["start"], S["rischio"]["end"]),
         ("rewind", S["riavvolgi"]["start"], S["riavvolgi"]["end"]), ("giusta", S["giusta"]["start"], S["finale"]["end"] + 0.4)]
z = 1; media = ""
for cid, a, b in clips:
    media += (f'      <video id="v-{cid}" class="clip" src="assets/clips/{cid}.mp4" data-start="{r3(a)}" data-duration="{r3(b - a)}" '
              f'data-track-index="1" muted playsinline style="position:absolute; left:0; top:0; width:1920px; height:1080px; object-fit:cover; z-index:{z}"></video>\n'); z += 1
for aid, vol in (("voice", 1), ("music", 0.55), ("sfx", 0.9)):
    media += f'      <audio id="a-{aid}" class="clip" src="assets/audio/{aid}.wav" data-start="0" data-duration="{r3(D)}" data-track-index="{10 + z}" data-volume="{vol}"></audio>\n'; z += 1
hs = ""
for cid, a, d, kind in hosts + [("captions", 0, D, "captions")]:
    hs += (f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{r3(a)}" '
           f'data-duration="{r3(d)}" data-track-index="{20 + z}" data-track-kind="{kind}" data-width="1920" data-height="1080" style="z-index:{50 + z}"></div>\n'); z += 1
open(f"{HF}/index.html", "w").write(f"""<!doctype html>
<html lang="it">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Sono un contratto · Usare l'IA in sicurezza · Lezione 3</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ width:1920px; height:1080px; overflow:hidden; background:#141f2e; }}
      #root {{ position:relative; width:1920px; height:1080px; overflow:hidden; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{r3(D)}" data-width="1920" data-height="1080" data-fps="30">
{media}{hs}    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""")
json.dump({"id": "sono-un-contratto", "name": "Sono un contratto · Lezione 3"}, open(f"{HF}/meta.json", "w"))
json.dump({"paths": {"blocks": "compositions", "assets": "assets"}, "media": {"autoProxy": True}}, open(f"{HF}/hyperframes.json", "w"), indent=2)
print(f"index.html: {len(clips)} clip, {len(hosts) + 1} scene grafiche, {len(groups)} gruppi di sottotitoli, durata {D:.2f}s")

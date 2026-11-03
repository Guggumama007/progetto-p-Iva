"""Musica ed effetti sonori sintetizzati da codice (nessun campione esterno), sincronizzati a timeline.json.
- musica: pizzicati ironici in Do maggiore per "casa"; bordone in La minore per "fuori"; ta-da nel finale
- effetti: fruscio di carta, clic, risucchio, lampi della fotocopiatrice, timbri, cupola, riavvolgimento
Quando yt-dlp potra' scaricare suoni con licenza libera (archive.org / Wikimedia Commons) alcuni effetti
verranno sostituiti da registrazioni vere. Uscita: audio/music.wav, audio/sfx.wav (48 kHz, mono)."""
import json, math, sys
import numpy as np
import soundfile as sf

SR = 48000
tl = json.load(open("timeline.json")); D = tl["duration"]
N = int(D * SR) + SR
rng = np.random.default_rng(3)
scene = {s["id"]: s for s in tl["scenes"]}
lines = tl["lines"]

def env(n, a=0.005, r=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)

def note(f, dur, vol=0.2, kind="pluck"):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "pluck":   # pizzicato: armoniche smorzate
        y = sum(np.sin(2 * np.pi * f * k * t) * (0.6 ** (k - 1)) for k in range(1, 5)) * env(n, 0.003, 0.18)
    elif kind == "bass":
        y = np.sin(2 * np.pi * f * t) * env(n, 0.01, 0.35) + 0.3 * np.sin(4 * np.pi * f * t) * env(n, 0.01, 0.2)
    elif kind == "pad":
        y = sum(np.sin(2 * np.pi * f * (1 + d) * t) for d in (-0.003, 0, 0.004)) / 3
        y *= np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    elif kind == "bell":
        y = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * env(n, 0.002, 0.6)
    return (y * vol).astype(np.float32)

def put(buf, t, y):
    i = int(t * SR)
    if i >= len(buf) or i + len(y) <= 0: return
    j = min(len(buf), i + len(y)); buf[max(0, i):j] += y[max(0, -i):j - i]

midi = lambda m: 440 * 2 ** ((m - 69) / 12)
music = np.zeros(N, np.float32)
BPM = 104; beat = 60 / BPM

def home_groove(t0, t1, vol=1.0, root=60):
    """Pizzicati staccati + basso, in maggiore (tono leggero, un po' da cartone)."""
    prog = [(0, [0, 4, 7]), (5, [5, 9, 12]), (7, [7, 11, 14]), (0, [0, 4, 7])]
    t, k = t0, 0
    while t < t1 - 0.05:
        bass, ch = prog[(k // 8) % 4]
        if k % 4 == 0: put(music, t, note(midi(root - 24 + bass), beat * 1.8, 0.16 * vol, "bass"))
        pat = [0, None, 1, 2, None, 1, 0, 2][k % 8]
        if pat is not None: put(music, t, note(midi(root + ch[pat]), beat, 0.07 * vol))
        t += beat / 2; k += 1

def out_drone(t0, t1, vol=1.0):
    """Fuori: bordone in La minore, battito basso lento, campanelle fredde ogni tanto."""
    for m in (45, 52, 57):
        put(music, t0, note(midi(m), t1 - t0, 0.05 * vol, "pad"))
    t = t0
    while t < t1:
        put(music, t, note(midi(33), 0.5, 0.18 * vol, "bass")); t += beat * 2
    for k, t in enumerate(np.arange(t0 + 0.5, t1 - 0.5, beat * 3)):
        put(music, t, note(midi([69, 72, 76, 74][k % 4]), 1.2, 0.035 * vol, "bell"))

s = scene
home_groove(0, s["viaggio"]["start"] + 0.4)
out_drone(s["viaggio"]["start"] + 0.2, s["riavvolgi"]["start"])
home_groove(s["giusta"]["start"] + 0.3, s["cartello"]["start"], vol=1.1)
# ta-da finale + accordo sul cartello
tf = s["cartello"]["start"]
for i, m in enumerate((72, 76, 79, 84)): put(music, tf - 0.4 + i * 0.06, note(midi(m), 1.6, 0.08, "bell"))
for m in (48, 60, 64, 67): put(music, tf, note(midi(m), 3.0, 0.05, "pad"))
# ducking sotto la voce
duck = np.ones(N, np.float32)
for l in lines:
    a, b = int((l["start"] - 0.1) * SR), int((l["end"] + 0.15) * SR); duck[a:b] = 0.55
k = int(0.08 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same").astype(np.float32)
music *= duck

# ---------------------------------------------------------------- effetti
sfx = np.zeros(N, np.float32)
def noise(n): return rng.standard_normal(n).astype(np.float32)
def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def rustle(dur=0.35, vol=0.25):   # fruscio di carta: rumore filtrato a raffiche
    n = int(dur * SR); x = bandpass(noise(n), 1800, 9000)
    gr = np.repeat(rng.uniform(0.2, 1, n // 400 + 1), 400)[:n]
    return x * gr * env(n, 0.01, dur / 2.5) * vol
def click(vol=0.4):
    n = int(0.03 * SR); return bandpass(noise(n), 2000, 7000) * env(n, 0.0005, 0.006) * vol
def whoosh(dur, up=True, vol=0.4):
    n = int(dur * SR); x = noise(n); out = np.zeros(n, np.float32); seg = n // 24
    for i in range(24):
        f0 = 300 + (i / 24 if up else 1 - i / 24) * 4000
        out[i * seg:(i + 1) * seg] = bandpass(x[i * seg:(i + 1) * seg], f0 * 0.6, f0 * 1.4)
    t = np.arange(n) / n; return out * np.sin(np.pi * t) ** 1.5 * vol
def thud(vol=0.6):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (90 - 40 * t / 0.25) * t) * env(n, 0.001, 0.07) + bandpass(noise(n), 200, 2500) * env(n, 0.0005, 0.02) * 0.6) * vol
def zap(vol=0.18):  # lampo della fotocopiatrice
    n = int(0.12 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (1200 + 3000 * t / 0.12) * t) * env(n, 0.002, 0.05) * vol

# suoni reali (yt-dlp, Wikimedia Commons, licenza libera) se disponibili, altrimenti quelli sintetizzati
import glob, subprocess
def cc(key, dur=None, vol=0.5):
    f = glob.glob(f"audio/sfx_cc/{key}.*")
    if not f: return None
    raw = subprocess.run(["/opt/ffmpeg-src/bin/ffmpeg", "-v", "error", "-i", f[0], "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    y = np.frombuffer(raw, np.float32).copy()
    if dur: y = y[: int(dur * SR)] * env(min(len(y), int(dur * SR)), 0.01, dur / 2)
    return y / (np.abs(y).max() + 1e-6) * vol
_rustle, _thud = rustle, thud
rustle = lambda dur=0.35, vol=0.25: cc("paper", dur, vol * 1.4) if cc("paper") is not None else _rustle(dur, vol)
thud = lambda vol=0.6: cc("stamp", 0.4, vol) if cc("stamp") is not None else _thud(vol)
T = lambda sid, dt=0.0: s[sid]["start"] + dt
put(sfx, T("buongiorno", 0.7), rustle(0.6, 0.22))                       # stiracchiata
put(sfx, T("buongiorno", 1.4), rustle(0.25, 0.15))
fl = [l for l in lines if l["scene"] == "fretta"]
put(sfx, fl[1]["start"] + 0.15, click(0.5)); put(sfx, fl[1]["start"] + 0.2, rustle(0.3, 0.2))   # "Mi copia"
put(sfx, fl[1]["start"] + 1.25, whoosh(0.5, True, 0.25))                                      # "...e mi incolla"
nl = [l for l in lines if l["scene"] == "nessuno"]
put(sfx, nl[0]["end"] - 0.05, rustle(0.3, 0.25))                                               # spallucce
put(sfx, T("viaggio", 0.25), whoosh(3.3, True, 0.5))                                           # risucchiato nel cavo
put(sfx, T("viaggio", 3.3), thud(0.35))                                                        # atterraggio nella sala server
hum = (np.sin(2 * np.pi * 60 * np.arange(int((T("riavvolgi") - T("viaggio", 3.3)) * SR)) / SR) * 0.03).astype(np.float32)
put(sfx, T("viaggio", 3.3), hum)
tb = T("rischio", 0.85)
for w in range(8): put(sfx, tb + w * 0.22, zap(0.12 + w * 0.015))                              # fotocopie a raddoppio
put(sfx, tb + 8 * 0.22 + 0.15, whoosh(1.2, False, 0.45))                                       # esplosione di copie
put(sfx, T("riavvolgi", 0.0), whoosh(2.0, False, 0.5))                                         # riavvolgimento
for k in range(14): put(sfx, T("riavvolgi", 0.1 + k * 0.12), click(0.15))
gl = [l for l in lines if l["scene"] == "giusta"]
put(sfx, gl[0]["start"] + 0.8, thud(0.3))                                                      # la cupola si posa
sys.path.insert(0, "tools")
for st in json.load(open("audio/stamps.json")): put(sfx, st, thud(0.55))                       # i tre timbri
fn = [l for l in lines if l["scene"] == "finale"]
put(sfx, fn[1]["start"] + 0.2, rustle(0.3, 0.2))                                               # saltello felice

mx = max(np.abs(music).max(), 1e-6); music = music / mx * 0.5
sf.write("audio/music.wav", music[: int(D * SR)], SR); sf.write("audio/sfx.wav", np.clip(sfx, -1, 1)[: int(D * SR)], SR)
print("musica e sfx:", round(D, 2), "s")

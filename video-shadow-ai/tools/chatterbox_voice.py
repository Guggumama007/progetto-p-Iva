"""Voce definitiva con Chatterbox multilingue (italiano), inserita negli STESSI spazi della timeline.
Le scene Blender sono sincronizzate alle battute: invece di ricalcolare la timeline (e rifare 2 ore di render)
ogni battuta nuova parte allo stesso istante e, se e' piu' lunga del suo spazio, viene accelerata con
atempo (max 1.12x); oltre quel limite lo script lo segnala.
Richiede huggingface.co abilitato (pesi ResembleAI/chatterbox). Gira su CPU.
Uso: /opt/venv/chatterbox/bin/python tools/chatterbox_voice.py
"""
import json, subprocess, os
import torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ROOT = "/home/user/APEX-AI-Terminal/video-shadow-ai"
FF = "/opt/ffmpeg-src/bin/ffmpeg"
tl = json.load(open(f"{ROOT}/timeline.json")); lines = tl["lines"]
out = f"{ROOT}/audio/chatterbox"; os.makedirs(out, exist_ok=True)
torch.manual_seed(7)
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")

# tono leggero e ironico: un po' di espressivita' in piu', ritmo naturale
STYLE = dict(exaggeration=0.62, cfg_weight=0.45, temperature=0.75)
report = []
for k, l in enumerate(lines):
    text = l["caption"]                       # Chatterbox legge "Shadow AI" e "chatbot" senza trucchi fonetici
    wav = model.generate(text, language_id="it", **STYLE)
    raw = f"{out}/{k:02d}_raw.wav"; torchaudio.save(raw, wav, model.sr)
    # spazio disponibile: fino all'inizio della battuta successiva (meno un respiro) o alla fine della scena
    nxt = lines[k + 1]["start"] if k + 1 < len(lines) and lines[k + 1]["scene"] == l["scene"] else \
          next(s["end"] for s in tl["scenes"] if s["id"] == l["scene"])
    slot = nxt - l["start"] - 0.2
    dur = wav.shape[-1] / model.sr
    tempo = 1.0 if dur <= slot else min(1.12, dur / slot)
    fit = f"{out}/{k:02d}.wav"
    subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-af", f"silenceremove=start_periods=1:start_threshold=-45dB,atempo={tempo:.3f}", "-ar", "48000", fit], check=True)
    report.append(dict(i=k, text=text, dur=round(dur, 2), slot=round(slot, 2), tempo=round(tempo, 3), ok=dur / tempo <= slot + 0.05))
    print(f"{k:02d} {dur:5.2f}s / spazio {slot:5.2f}s  atempo {tempo:.2f}  {'OK' if report[-1]['ok'] else 'TROPPO LUNGA'}  {text}")

# traccia voce sugli stessi istanti della timeline
inputs, filt = [], []
for k, l in enumerate(lines):
    inputs += ["-i", f"{out}/{k:02d}.wav"]
    filt.append(f"[{k}]adelay={int(l['start'] * 1000)}:all=1[v{k}]")
filt.append("".join(f"[v{k}]" for k in range(len(lines))) + f"amix=inputs={len(lines)}:normalize=0,apad=whole_dur={tl['duration']}[o]")
subprocess.run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[o]", "-ac", "1", f"{ROOT}/audio/voice_chatterbox.wav"], check=True)
json.dump(report, open(f"{out}/report.json", "w"), ensure_ascii=False, indent=1)
print("voce Chatterbox montata:", f"{ROOT}/audio/voice_chatterbox.wav")

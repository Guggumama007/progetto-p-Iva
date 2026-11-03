"""faster-whisper: tempi parola per parola della voce definitiva, per sottotitoli e timbri al frame giusto.
- trascrive la traccia voce montata (audio/voice_eleven.wav se c'e', altrimenti la voce guida) (modello small, italiano, CPU int8, VAD Silero incluso)
- abbina le parole alle battute per POSIZIONE (non per testo: le ripetizioni non si confondono)
- scrive line["words"] in timeline.json senza toccare inizi/fine delle battute (le scene restano valide)
- stampa quanto la trascrizione si discosta dal copione (controllo di pronuncia della voce)
Richiede huggingface.co abilitato (Systran/faster-whisper-small).
Uso: .venv/bin/python tools/fw_words.py
"""
import json, re, difflib, os
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE = next(f"{ROOT}/audio/{f}" for f in ("voice_eleven.wav", "voice_guide.wav") if os.path.exists(f"{ROOT}/audio/{f}"))
tl = json.load(open(f"{ROOT}/timeline.json"))
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = model.transcribe(VOICE, language="it", word_timestamps=True,
                              vad_filter=True, vad_parameters=dict(min_silence_duration_ms=200), beam_size=5)
words = [w for s in segs for w in s.words]
norm = lambda t: re.sub(r"[^\wàèéìòù]", "", t.lower())
heard = []
for l in tl["lines"]:
    ws = [w for w in words if l["start"] - 0.25 <= w.start <= l["start"] + 6 and w.start < (l["end"] + 1.2)]
    script_words = l["caption"].split()
    # allineamento per posizione tra parole del copione e parole sentite
    sm = difflib.SequenceMatcher(a=[norm(x) for x in script_words], b=[norm(w.word) for w in ws])
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        for k in range(i2 - i1):
            j = j1 + min(k, max(0, j2 - j1 - 1)) if j2 > j1 else None
            if j is not None and j < len(ws):
                out.append(dict(w=script_words[i1 + k], start=round(ws[j].start, 3), end=round(ws[j].end, 3)))
    l["words"] = out
    heard.append((l["caption"], " ".join(w.word.strip() for w in ws), sm.ratio()))
json.dump(tl, open(f"{ROOT}/timeline.json", "w"), ensure_ascii=False, indent=1)
bad = [h for h in heard if h[2] < 0.8]
print(f"parole: {len(words)}  battute con pronuncia da ricontrollare: {len(bad)}")
for c, h, r in bad: print(f"  {r:.2f}  copione: {c}\n        sentito: {h}")

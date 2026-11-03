# Prossima sessione: sincronizzare la voce di ElevenLabs con il cartone

Il cartone (`design/cartone-v2.mp4`) è sincronizzato su una **voce guida provvisoria**: serve solo a dare i tempi.
Tutto è generato a partire da `timeline.json`: animazione, lip-sync, sottotitoli, musica ed effetti.
Cambiando la voce, si rigenera e si riallinea tutto da solo.

## Cosa portare
- La ripresa unica di ElevenLabs con il testo di [`VOCE-ELEVENLABS.md`](VOCE-ELEVENLABS.md), in mp3 o wav,
  da caricare in chat.
- Facoltativo: musica ed effetti generati su ElevenLabs, se vuoi sostituire quelli sintetizzati da codice.

## Passi (li esegue Claude)
```bash
cd video-shadow-ai
# 0. ambiente: Blender non serve; servono le venv e i pacchetti npm (vedi REPOS.md), FFmpeg e hyperframes
# 1. taglia la ripresa nelle 13 battute
/opt/venv/tools/bin/python tools/voice_to_timeline.py audio/elevenlabs.mp3
# 2. nuova timeline sui tempi reali della voce (+ traccia voce montata)
/opt/venv/tools/bin/python tools/timeline.py audio/script_cartoon.json audio/eleven audio/pads_cartoon.json audio/voice_eleven.wav
# 3. (se huggingface.co è abilitato) tempi parola per parola con faster-whisper -> lip-sync e sottotitoli più precisi
/opt/venv/tools/bin/python tools/fw_words.py
# 4. musica ed effetti sui nuovi tempi, poi rigenera il progetto HyperFrames
python3 tools/make_audio_cartoon.py && python3 cartoon/build.py
# 5. controllo e render
cd cartoon/hf && npx hyperframes check && npx hyperframes render --quality delivery -o ../../design/cartone-v3.mp4
```

## Da verificare a occhio dopo il cambio voce
- I gesti cadono sulle parole giuste: le coreografie in `cartoon/shots/*.html` usano `W(i, "parola")`, quindi seguono la voce.
- Le pause per le gag visive in `audio/pads_cartoon.json` e i `pre` in `audio/script_cartoon.json`: allungale o accorciale
  se il ritmo della voce reale lo chiede.
- Il lip-sync: è a "passo due" (15 fps) e usa i visemi italiani. Con i tempi di faster-whisper diventa più preciso.

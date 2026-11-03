# Prossima sessione: sincronizzare la voce di ElevenLabs con il cartone

Il cartone (`design/cartone-v2.mp4`) è sincronizzato su una **voce guida provvisoria**: serve solo a dare i tempi.
Tutto è generato a partire da `timeline.json`: animazione, lip-sync, sottotitoli, musica ed effetti.
Cambiando la voce, si rigenera e si riallinea tutto da solo.

## Cosa portare
- La ripresa unica di ElevenLabs con il testo di [`VOCE-ELEVENLABS.md`](VOCE-ELEVENLABS.md), in mp3 o wav,
  da caricare in chat. Va salvata come `video-shadow-ai/audio/elevenlabs.mp3` (o `.wav`).
- Facoltativo: musica ed effetti generati su ElevenLabs, se vuoi sostituire quelli sintetizzati da codice.
- Nessuna chiave API: il file si carica in chat, non serve collegarsi a ElevenLabs.

## Passi (li esegue Claude, dalla cartella `video-shadow-ai`)
```bash
# 0. ambiente (container nuovo): faster-whisper in .venv, hyperframes 0.9.9 e font in .tools, FFmpeg di sistema
bash tools/setup_sessione.sh && source .tools/env.sh
# 1. taglia la ripresa nelle 13 battute -> audio/eleven/00.wav ... 12.wav (ascoltarle: se un taglio è sbagliato, correggerlo)
python tools/voice_to_timeline.py audio/elevenlabs.mp3
# 2. nuova timeline sui tempi reali della voce (+ traccia voce montata audio/voice_eleven.wav)
python tools/timeline.py audio/script_cartoon.json audio/eleven audio/pads_cartoon.json audio/voice_eleven.wav
# 3. (solo se huggingface.co è raggiungibile) tempi parola per parola -> lip-sync e sottotitoli più precisi
python tools/fw_words.py
# 4. musica ed effetti sui nuovi tempi, poi rigenera il progetto HyperFrames
python tools/make_audio_cartoon.py && python cartoon/build.py
# 5. controllo e render (il render dura parecchi minuti: lanciarlo in background)
cd cartoon/hf && hyperframes check && hyperframes render --quality delivery -o ../../design/cartone-v3-master.mp4
# 6. versione web leggera (come la v2)
ffmpeg -y -i ../../design/cartone-v3-master.mp4 -c:v libx264 -preset slow -tune animation -crf 18 -pix_fmt yuv420p \
       -c:a copy -movflags +faststart ../../design/cartone-v3.mp4
```
Da salvare su GitHub (ramo `video-sono-un-contratto`): `audio/elevenlabs.*`, `audio/voice_eleven.wav`, `timeline.json`,
`cartoon/hf/`, `design/cartone-v3.mp4` (il master no: è troppo pesante). Il file `.mp4` va spinto in un commit a parte.

## Da verificare a occhio dopo il cambio voce
- I gesti cadono sulle parole giuste: le coreografie in `cartoon/shots/*.html` usano `W(i, "parola")`, quindi seguono la voce.
  Senza il passo 3 il tempo di ogni parola è stimato dentro la battuta: controllare i fotogrammi chiave con `hyperframes snapshot`.
- Le pause per le gag visive in `audio/pads_cartoon.json` e i `pre` in `audio/script_cartoon.json`: allungale o accorciale
  se il ritmo della voce reale lo chiede.
- Il lip-sync: è a "passo due" (15 fps) e usa i visemi italiani. Con i tempi di faster-whisper diventa più preciso.
- Il volume: la v2 è a circa -15 LUFS; se la voce ElevenLabs è più alta o più bassa, riequilibrare in `tools/make_audio_cartoon.py`.

# "Sono un contratto": Usare l'IA in sicurezza · Lezione 3

**Cartone animato 2D** di circa 67 s in 16:9, a tema Shadow AI. Tutti i personaggi sono oggetti con caratteristiche
umane, il tono è leggero e ironico.
- Video: `design/cartone-v1.mp4` (voce guida provvisoria: la voce definitiva di ElevenLabs si monta nella
  prossima sessione, vedi [`PROSSIMA-SESSIONE.md`](PROSSIMA-SESSIONE.md))
- Design: `design/foglio-modello.png` e `design/immagine-chiave-*.png`
- Codice del cartone: `cartoon/`. Contiene personaggi SVG (`characters.js`), oggetti di scena (`props.js`),
  sfondi (`scenes.js`), il motore di animazione (`anim.js`), le coreografie (`shots/*.html`) e il generatore
  del progetto HyperFrames (`build.py` → `cartoon/hf/`)

### Versioni precedenti (archivio)
La prima versione, in 3D di carta con Blender (stop-motion), è nelle cartelle `blender/`, `remotion/` e
`hyperframes/` e in `design/bozza-1.mp4`. È stata sostituita dal cartone 2D.
- Copione: [`SCRIPT.md`](SCRIPT.md)
- Valutazione dei 14 repo usati: [`REPOS.md`](REPOS.md)
- Bozze: `design/`

## Pipeline della prima versione (3D di carta)
| Passo | Strumento | File |
|---|---|---|
| Voce (provvisoria Piper, definitiva Chatterbox) | Piper · Chatterbox | `tools/tts.py`, `tools/chatterbox_voice.py` |
| Timeline (battute, scene) | faster-whisper (VAD) | `tools/timeline.py` → `timeline.json` |
| Tempi parola per parola | faster-whisper | `tools/fw_words.py` |
| Scene in carta (personaggio, scrivania, sala server, cupola) | Blender 4.0 via **Blender MCP** | `blender/paperlib.py`, `blender/shot_*.py`, `tools/blender_mcp_client.py` |
| Render Blender (coda) | Blender CLI, EEVEE | `tools/render_daemon.sh` |
| Tunnel e copie | Three.js + GSAP in **Remotion** | `remotion/src/Tunnel.tsx`, `remotion/src/Copie.tsx` |
| Musica ed effetti | sintesi Python, suoni CC via **yt-dlp** | `tools/make_audio.py`, `tools/fetch_sfx.py` |
| Materiali di carta | **ComfyUI** (SD-Turbo) | `tools/comfy_assets.py` |
| Clip e riavvolgimento | **FFmpeg** compilato dal repo | `tools/make_clips.sh` |
| Montaggio, tipografia, sottotitoli | **HyperFrames** + GSAP | `tools/build_hyperframes.py` → `hyperframes/` |
| Controllo qualità | HyperFrames `check`/`snapshot`, **Impeccable**, **Chrome DevTools MCP** | `tools/devtools_check.mjs` |

## Rigenerare
```bash
python3 tools/build_hyperframes.py && tools/make_clips.sh
cd hyperframes && npx hyperframes check && npx hyperframes render --quality delivery -o ../design/finale.mp4
```

## Pipeline del cartone 2D
| Passo | Strumento | File |
|---|---|---|
| Copione e indicazioni di recitazione | ElevenLabs (prossima sessione) | `VOCE-ELEVENLABS.md`, `audio/script_cartoon.json` |
| Timeline (battute, pause per le gag) | faster-whisper (VAD) | `tools/timeline.py`, `audio/pads_cartoon.json` → `timeline.json` |
| Personaggi, oggetti, sfondi | SVG parametrico (disegnato in codice) | `cartoon/characters.js`, `cartoon/props.js`, `cartoon/scenes.js` |
| Animazione (chiavi, lip-sync, camera) | GSAP | `cartoon/anim.js`, `cartoon/shots/*.html` |
| Montaggio, sottotitoli, render | HyperFrames | `cartoon/build.py` → `cartoon/hf/` |
| Musica ed effetti | sintesi Python (FFmpeg) | `tools/make_audio_cartoon.py` |
| Foglio modello e immagini chiave | Chrome DevTools MCP (screenshot) | `cartoon/model-sheet.html`, `cartoon/frame.html` |
| Controllo qualità | HyperFrames `check`/`snapshot`, Impeccable `detect` | |

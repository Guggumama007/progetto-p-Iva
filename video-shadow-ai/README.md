# "Sono un contratto": Usare l'IA in sicurezza · Lezione 3

Video di circa 63 s in 16:9, a tema Shadow AI. Mondo di carta in stop-motion a 12 fps, personaggio con occhi minimali,
tono leggero e ironico.
- Copione: [`SCRIPT.md`](SCRIPT.md)
- Valutazione dei 14 repo usati: [`REPOS.md`](REPOS.md)
- Bozze: `design/`

## Pipeline
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

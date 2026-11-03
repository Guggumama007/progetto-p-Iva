# "Sono un contratto": Usare l'IA in sicurezza · Lezione 3

**Cartone animato 2D** di circa 67 s in 16:9 sul tema della Shadow AI. Il protagonista è un contratto che viene
copiato in un chatbot gratuito, finisce chissà dove e poi, "riavvolgendo", mostra il modo giusto: strumento approvato,
regole chiare, persone formate. Tutti i personaggi sono oggetti con caratteristiche umane, e il tono è leggero e ironico.

- **Video attuale:** [`design/cartone-v2.mp4`](design/cartone-v2.mp4), con voce guida provvisoria. La voce definitiva
  di ElevenLabs si monta con [`PROSSIMA-SESSIONE.md`](PROSSIMA-SESSIONE.md).
- **Design:** `design/foglio-modello.png` (personaggi), `design/immagine-chiave-*.png` (ambienti),
  `design/chatbot-proposte.png` e `design/protezione-proposte.png` (proposte approvate per la v2).

## Documentazione
| File | Contenuto |
|---|---|
| [`STILE.md`](STILE.md) | guida di stile della serie: mondo, disegno, tavolozza, personaggi, animazione, tipografia, suono, struttura di un episodio |
| [`NUOVO-VIDEO.md`](NUOVO-VIDEO.md) | come fare un nuovo episodio nello stesso stile, con un prompt pronto per Claude Code |
| [`REPOS.md`](REPOS.md) | i 14 repo GitHub usati (e perché) e il metodo di lavoro |
| [`VOCE-ELEVENLABS.md`](VOCE-ELEVENLABS.md) | casting della voce, impostazioni e testo delle 13 battute |
| [`PROSSIMA-SESSIONE.md`](PROSSIMA-SESSIONE.md) | comandi per montare la voce ElevenLabs e renderizzare la v3 |

## Pipeline
| Passo | Strumento | File |
|---|---|---|
| Copione e recitazione | ElevenLabs | `VOCE-ELEVENLABS.md`, `audio/script_cartoon.json` |
| Timeline (battute, pause per le gag) | faster-whisper (VAD) | `tools/timeline.py`, `audio/pads_cartoon.json` → `timeline.json` |
| Tempi parola per parola | faster-whisper | `tools/fw_words.py` |
| Personaggi, oggetti, sfondi | SVG parametrico disegnato in codice | `cartoon/characters.js`, `chatbots.js`, `props.js`, `scenes.js` |
| Animazione (chiavi, lip-sync, camera) | GSAP | `cartoon/anim.js`, `cartoon/shots/*.html` |
| Montaggio, sottotitoli, render | HyperFrames | `cartoon/build.py` → `cartoon/hf/` |
| Musica ed effetti | sintesi Python + FFmpeg | `tools/make_audio_cartoon.py` |
| Tavole di design | Chrome DevTools MCP | `cartoon/model-sheet.html`, `frame.html`, `*-proposte.html` |
| Controllo qualità | HyperFrames `check` e `snapshot`, Impeccable `detect` | |
| Ambiente per una sessione nuova | | `tools/setup_sessione.sh` |

## Rigenerare
```bash
bash tools/setup_sessione.sh && source .tools/env.sh      # solo la prima volta in un ambiente nuovo
python tools/make_audio_cartoon.py && python cartoon/build.py
cd cartoon/hf && hyperframes check && hyperframes render --quality delivery -o ../../design/cartone-master.mp4
```

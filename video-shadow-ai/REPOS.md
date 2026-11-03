# I 14 repo: installati, provati e valutati

Ho clonato da GitHub tutti e 14 i repo dello screenshot (in `/opt/repos`), li ho installati e li ho provati
in questo ambiente cloud. Poi ho deciso caso per caso se usarli nel video.

Prima, i limiti di questo ambiente, perché spiegano quasi tutti i "no":
- **niente GPU**: solo 4 core CPU e 15 GB di RAM;
- **rete filtrata**: GitHub, npm, PyPI e i pacchetti Ubuntu sono raggiungibili. HuggingFace, Civitai,
  YouTube, Vimeo, PolyHaven, Sketchfab e projects.blender.org invece sono **bloccati**;
- **disco limitato**: circa 40 GB in tutto per la sessione.

| # | Repo | Installato | Provato | Nel video? |
|---|------|-----------|---------|------------|
| 1 | remotion-dev/skills | ✅ clonato | ✅ letto e applicato | ✅ **Sì**, come guida |
| 2 | blender/blender | ✅ clonato, ⚠️ non compilato | ✅ Blender 4.0.2 ufficiale | ✅ **Sì** |
| 3 | SYSTRAN/faster-whisper | ✅ 1.2.1 dal repo | ⚠️ modello non scaricabile | 🟡 **In parte**, solo VAD |
| 4 | resemble-ai/chatterbox | ✅ dal repo | ❌ pesi non scaricabili | ❌ **No**, sostituito da Piper |
| 5 | greensock/GSAP | ✅ 3.15.0 (= repo) | ✅ | ✅ **Sì** |
| 6 | ahujasid/mcp-for-blender | ✅ dal repo + add-on | ✅ 9 strumenti MCP | ✅ **Sì** |
| 7 | ChromeDevTools/chrome-devtools-mcp | ✅ 1.12.0 (= repo) | ✅ 32 strumenti MCP | ✅ **Sì**, per i controlli |
| 8 | FFmpeg/FFmpeg | ✅ **compilato dal sorgente** | ✅ | ✅ **Sì** |
| 9 | remotion-dev/remotion | ✅ 4.0.540 (= repo) | ✅ | ✅ **Sì** |
| 10 | pbakaus/impeccable | ✅ dal repo | ✅ `detect` | ✅ **Sì**, per la revisione |
| 11 | mrdoob/three.js | ✅ 0.187.0 (= repo) | ✅ WebGL su CPU | ✅ **Sì** |
| 12 | Comfy-Org/ComfyUI | ✅ dal repo | ✅ gira, 1036 nodi, 0 modelli | ❌ **No** |
| 13 | yt-dlp/yt-dlp | ✅ dal repo | ❌ YouTube e Vimeo bloccati | ❌ **No** |
| 14 | heygen-com/hyperframes | ✅ 0.9.9 (= repo) | ✅ render ok | ✅ **Sì**, come compositor finale |

---

## Dettaglio, uno per uno

### 1. Remotion Skills: ✅ usato
**Cosa è:** le istruzioni ufficiali di Remotion pensate per gli agenti AI.
**Test:** le ho lette (`remotion-best-practices`, `remotion-create`, `remotion-render`, `remotion-captions`).
**Perché lo uso:** mi hanno detto come impostare il progetto, la configurazione del browser per il
rendering e come gestire Three.js dentro Remotion. È documentazione, non codice: la uso come guida.

### 2. Blender: ✅ usato (build ufficiale, non compilata da me)
**Test:** il repo `blender/blender` è clonato. Compilarlo qui però non è fattibile: le librerie
precompilate stanno su `projects.blender.org`, che è bloccato, e la compilazione richiederebbe ore su 4 core.
Ho installato **Blender 4.0.2**, la build ufficiale dello stesso progetto (pacchetto Ubuntu).
EEVEE funziona senza schermo grazie a Xvfb e a Mesa (render su CPU).
**Perché lo uso:** fa le scene 3D "fisiche", cioè la scrivania delle 9:15 e la pioggia di fogli, con
luci, materiali e profondità di campo che in HTML non si ottengono.

### 3. faster-whisper: 🟡 usato in parte
**Test:** la libreria 1.2.1 è installata dal repo. `WhisperModel("small")` fallisce con
`ProxyError 403`, perché i modelli stanno solo su HuggingFace. Ho trovato un mirror su GitHub
(`ct2-models-de/whisper-small-ct2`), ma è un account sconosciuto e i pesi non si possono verificare:
non l'ho scaricato.
**Cosa uso:** il **Silero VAD** che faster-whisper include già e che funziona senza rete. Rileva dove
c'è voce, e mi serve per sincronizzare i sottotitoli con la voce.
**Al posto della trascrizione:** lo stesso modello Whisper small, in formato ONNX dalle release GitHub di
k2-fsa/sherpa-onnx (progetto affidabile). Con quello ho trascritto il video originale e verifico la voce generata.

### 4. Chatterbox: ❌ non usato
**Test:** installato dal repo. L'import funziona e l'italiano è supportato (`"it" in SUPPORTED_LANGUAGES`).
`from_pretrained()` però fallisce con `ProxyError 403`, perché i pesi stanno su HuggingFace.
**Perché no:** senza pesi non genera voce. **Sostituto:** Piper (open-source, voce italiana
"paola", modello scaricato dalle release GitHub di sherpa-onnx).
*Se Chatterbox ti interessa, sul tuo computer funziona: lì HuggingFace non è bloccato.*

### 5. GSAP: ✅ usato
**Test:** una timeline GSAP in pausa guidata dal fotogramma corrente, sia in Remotion sia in HyperFrames.
**Perché lo uso:** anima tutti i titoli, i punti elenco, il timer, l'interfaccia del chatbot e la barra dei capitoli.

### 6. MCP for Blender: ✅ usato
**Test:** add-on installato in Blender, avviato con interfaccia grafica su display virtuale. Server socket
sulla porta 9876, server MCP collegato con un mio client MCP (`tools/blender_mcp_client.py`).
Funzionano `get_scene_info`, `execute_blender_code` e `look` (cattura della vista).
Telemetria disattivata. Non funzionano gli strumenti online (`search_assets`, `import_asset`,
`generate_3d`), perché PolyHaven, Sketchfab e i generatori 3D sono bloccati.
**Perché lo uso:** costruisco le scene Blender **attraverso MCP**, cioè codice inviato alla scena viva,
controllo con `look` e correggo. Il rendering vero lo faccio poi con Blender da riga di comando,
perché un render lungo bloccherebbe il canale MCP.

### 7. Chrome DevTools MCP: ✅ usato per i controlli
**Test:** mio client MCP (`tools/devtools_check.mjs`) con Chromium headless. Ho provato
`new_page`, `evaluate_script`, `list_console_messages` e `take_screenshot`. Usage statistics e CrUX disattivati.
**Perché lo uso:** prima di esportare apro le composizioni HTML, leggo gli errori in console e
guardo gli screenshot. È quello che promette il repo: "l'agente vede il proprio rendering e lo corregge".

### 8. FFmpeg: ✅ usato (compilato dal repo)
**Test:** **compilato dal sorgente clonato**, versione `git-2026-11-03` con libx264, in `/opt/ffmpeg-src`.
**Perché lo uso:** mix audio (voce e musica sintetizzata), loudness, inversione per l'effetto "riavvolgiamo",
encoding finale e ispezione. Anche HyperFrames usa questo FFmpeg.

### 9. Remotion: ✅ usato
**Test:** render di prova con `@remotion/three` e GSAP, Chromium headless con WebGL software (SwiftShader).
**Perché lo uso:** renderizza le scene Three.js (il documento che esce, i server, lo scudo), poi passate a HyperFrames.

### 10. Impeccable: ✅ usato per la revisione
**Test:** `impeccable detect` (62 regole, nessun LLM) gira sui file HTML.
**Perché lo uso:** controlla le composizioni HTML (tipografia, contrasto, impaginazione). Seguo anche le sue
linee guida `animate.md` e `critique.md` nella revisione dei fotogrammi.

### 11. Three.js: ✅ usato
**Test:** scena con luci e materiali PBR renderizzata in Remotion.
**Perché lo uso:** le scene "astratte" (fibre luminose, server, scudo olografico) sono più controllabili
in Three.js che in Blender, e si animano fotogramma per fotogramma insieme a GSAP.

### 12. ComfyUI: ❌ non usato
**Test:** installato dal repo, avviato con `--cpu`, versione 0.43.0, 1036 nodi.
Ho eseguito un flusso di lavoro via API senza modelli (LoadImage → ImageSharpen → ImageBlur → SaveImage):
funziona.
**Perché no:** ComfyUI serve a **generare** immagini e video con modelli (Stable Diffusion, Flux, Wan…).
Qui i modelli sono irraggiungibili (HuggingFace e Civitai bloccati), e senza GPU una sola immagine
richiederebbe minuti. I nodi che restano sono filtri che FFmpeg applica meglio e più velocemente
sui circa 1500 fotogrammi. I nodi "API" (Flux Pro, Gemini, Kling…) sono servizi cloud a pagamento
con chiave: non li ho usati. Nel video originale ComfyUI serviva per le persone in sala: io le
sostituisco con una scena grafica (vedi sotto).

### 13. yt-dlp: ❌ non usato
**Test:** installato dal repo. `yt-dlp` su YouTube e Vimeo fallisce con `403 Forbidden`, perché il proxy blocca i siti.
**Perché no:** serve a scaricare clip di riferimento dal web, ma il riferimento è il tuo video, che mi hai già
mandato. E comunque qui non può raggiungere i siti.

### 14. HyperFrames: ✅ usato, è il compositor finale
**Test:** `hyperframes init` e `render` funzionano con il Chromium locale e l'FFmpeg compilato dal repo.
Telemetria disattivata.
**Perché lo uso:** unisce tutto: clip di Blender e Remotion, titoli GSAP, sottotitoli, barra dei capitoli,
voce e musica. Il suo skill `reverse-any-video` (per rifare un video) richiede un piano a pagamento:
non l'ho usato, ma ho seguito lo stesso metodo a mano (misura, ricostruisci ogni livello, confronta).

---

## Cosa cambia rispetto all'originale
- **Persone e riprese dal vero** (mani sulla tastiera, sala riunioni): senza ComfyUI con modelli, né
  stock video, le ho sostituite con scene 3D e grafiche coerenti con la storia.
- **Voce:** Piper invece della voce originale; è più sintetica di Chatterbox o di una voce professionale.

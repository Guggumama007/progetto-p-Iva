# "Sono un contratto" · Usare l'IA in sicurezza · Lezione 3

Bozza 2 del copione. Tono leggero e ironico, mondo di carta, protagonista con occhi minimali.
Durata prevista: circa 50 s, formato 16:9.

| # | Scena | Cosa si vede | Voce del contratto (Chatterbox, italiano) |
|---|-------|--------------|------------------------------------------|
| 1 | **Buongiorno** | 09:15. Scrivania di carta, il contratto in piedi si stiracchia (un leggero arricciamento) | «Buongiorno. Sono un contratto. Tre pagine, due firme e parecchi dati riservati.» |
| 2 | **La fretta** | Ombra di un cursore di carta che mi seleziona; le mie righe si staccano come striscioline | «Alle nove e quindici qualcuno ha fretta. Mi copia… e mi incolla in un chatbot trovato online. Gratis. Che fortuna.» |
| 3 | **Nessuno** | Due cartellini di carta: "VIETATO?" e "AUTORIZZATO?", entrambi con un punto interrogativo che cade | «Nessuno l'ha vietato. Nessuno l'ha autorizzato. Diciamo che… nessuno ha chiesto.» |
| 4 | **Il viaggio** | Vengo arrotolato e risucchiato nel cavo di carta; tunnel di striscioline; sbuco in una sala server di cartone, etichetta "Paese: ?" | «Trenta secondi ed è fatto. Peccato che adesso io sia qui. Non so nemmeno in che paese.» |
| 5 | **Il nome** | Titolo grande ritagliato: **SHADOW AI** | «Questa si chiama Shadow AI.» |
| 6 | **Il rischio doppio** | Mi fotocopiano cento volte; le copie volano. Due colonne di cartellini | «E il rischio è doppio. Per l'azienda: dati dei clienti esposti, informazioni riservate fuori controllo. Per te: errori che firmi tu, e regole aziendali violate. Firmate da te, eh.» |
| 7 | **Riavvolgiamo** | Tutto torna indietro di corsa, l'orologio torna alle 09:15, io faccio un sospiro | «Riavvolgiamo.» |
| 8 | **La versione giusta** | Stessa scrivania; una cupola di carta trasparente (la "casa" dell'azienda); tre timbri si posano: ✓ ✓ ✓ | «Stessa azienda, tre cose in più. Uno strumento approvato. Regole chiare. Persone formate.» |
| 9 | **Finale** | Io soddisfatto, occhi chiusi a mezzaluna | «Il lavoro si fa lo stesso, in trenta secondi. E io resto a casa.» |
| 10 | **Cartello** | "Usare l'IA in sicurezza · Lezione 3" (solo il corso, nessun nome) | (musica) |

## Strumenti per scena
- **Blender + Blender MCP**: scene 1, 2, 4 (sala server), 6, 7, 8, 9: il mondo di carta e il personaggio.
- **Three.js + Remotion**: scena 4, il tunnel di striscioline, e le righe che si staccano nella scena 2.
- **ComfyUI** (quando HuggingFace è abilitato): fondali dipinti in stile carta (città, sala server lontana) e texture di carta.
- **GSAP + HyperFrames**: tipografia ritagliata (scene 3, 5, 6, 8, 10), sottotitoli, montaggio.
- **Chatterbox**: la voce. **faster-whisper**: i tempi parola per parola, per sincronizzare testi e sottotitoli.
- **yt-dlp**: suoni con licenza libera (fruscio di carta, ronzio di server) da archive.org e Wikimedia Commons.
- **FFmpeg**: mix ed export. **Chrome DevTools MCP + Impeccable**: controllo qualità delle composizioni.

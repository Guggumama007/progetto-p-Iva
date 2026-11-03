// Motore di animazione 2D del cartone: chiavi interpolate con le eases di GSAP, pupazzi SVG ridisegnati a ogni
// fotogramma, lip-sync dal testo + tempi della timeline, battiti di ciglia, "idle" di recitazione, camera.
// Tutto e' funzione del tempo t (deterministico): HyperFrames puo' cercare qualsiasi fotogramma.
(function (root) {
  const { Chars } = root;
  const E = {};
  const ease = (n) => (n ? (E[n] ??= root.gsap ? root.gsap.parseEase(n) : (x) => x) : (x) => x * x * (3 - 2 * x));

  // ---------------------------------------------------------------- chiavi
  // keys: [[t, {param: valore, ...}, "ease"], ...]  — i numeri si interpolano con l'ease della chiave d'arrivo,
  // stringhe/booleani cambiano a scatto. Un parametro non presente in una chiave mantiene il valore precedente.
  function at(keys, t, base = {}) {
    const ks = keys.slice().sort((a, b) => a[0] - b[0]);
    let prev = { ...base }, prevT = -1e9;
    for (const [kt, kv, ke] of ks) {
      const next = { ...prev, ...kv };
      if (t < kt) {
        if (prevT === -1e9) return next;          // prima della prima chiave: la prima posa
        const u = Math.min(1, Math.max(0, (t - prevT) / Math.max(1e-6, kt - prevT)));
        const f = ease(ke)(u), out = { ...prev };
        for (const k in kv) if (typeof kv[k] === "number" && typeof prev[k] === "number") out[k] = prev[k] + (kv[k] - prev[k]) * f;
        return out;
      }
      prev = next; prevT = kt;
    }
    return prev;
  }
  const lerp = (a, b, u) => a + (b - a) * u;
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const osc = (t, f, ph = 0) => Math.sin((t * f + ph) * Math.PI * 2);

  // ---------------------------------------------------------------- lip-sync (italiano: lingua fonetica)
  const V = { a: "A", à: "A", e: "E", è: "E", é: "E", i: "I", ì: "I", o: "O", ò: "O", u: "U", ù: "U" };
  function visemeTrack(line) {
    // tempi delle parole: faster-whisper (line.words) se ci sono, altrimenti per proporzione dentro i segmenti VAD
    const words = line.caption.split(/\s+/).filter(Boolean);
    let wt;
    if (line.words && line.words.length === words.length) wt = line.words.map((w) => [w.start, w.end]);
    else {
      const segs = line.pauses && line.pauses.length ? line.pauses : [[0, line.speech]];
      const total = segs.reduce((s, [a, b]) => s + b - a, 0), chars = words.map((w) => w.replace(/[^\wàèéìòù]/g, "").length + 1);
      const sum = chars.reduce((a, b) => a + b, 0);
      const map = (x) => { let acc = 0; for (const [a, b] of segs) { if (acc + (b - a) >= x) return line.start + a + (x - acc); acc += b - a; } return line.end; };
      let c = 0; wt = chars.map((n) => { const a = map((c / sum) * total); c += n; return [a, map((c / sum) * total) - 0.03]; });
    }
    const track = [];
    words.forEach((w, i) => {
      const [a, b] = wt[i]; const L = w.toLowerCase().replace(/[^a-zàèéìòù]/g, "");
      const shapes = [];
      for (let k = 0; k < L.length; k++) {
        const ch = L[k];
        if (V[ch]) { if (shapes[shapes.length - 1] !== V[ch]) shapes.push(V[ch]); }
        else if ("mbp".includes(ch)) shapes.push("MBP");
        else if ("fv".includes(ch)) shapes.push("FV");
      }
      if (!shapes.length) shapes.push("E");
      const d = (b - a) / shapes.length;
      shapes.forEach((s, k) => track.push([a + k * d, s]));
      track.push([b, "rest"]);
    });
    return track;
  }
  // bocca al tempo t: a "passo due" (15 fps) come nell'animazione tradizionale; fuori dalle battute -> idle
  function mouthAt(lines, t, idle = "rest") {
    const tq = Math.floor(t * 15) / 15;
    for (const l of lines) {
      if (tq < l.start - 0.02 || tq > l.end + 0.05) continue;
      l._vt ??= visemeTrack(l);
      let m = "rest";
      for (const [vt, v] of l._vt) { if (vt <= tq) m = v; else break; }
      return m === "rest" ? (idle === "rest" ? "MBP" : idle) : m;
    }
    return idle;
  }
  // battiti di ciglia: lista di istanti -> fattore d'apertura (chiusura in 2 fotogrammi, riapertura in 3)
  function blinkAt(times, t) {
    for (const b of times) { const d = t - b; if (d >= 0 && d < 0.2) return d < 0.067 ? 0.15 : d < 0.13 ? 0.05 : 0.6; }
    return 1;
  }
  const autoBlinks = (t0, t1, seed = 1, every = 3.1) => { const out = []; let t = t0 + 0.6 + (seed % 5) * 0.37; while (t < t1) { out.push(t); t += every + ((seed * 7 + out.length * 13) % 10) / 10; } return out; };

  // ---------------------------------------------------------------- adattatori pupazzo -> opzioni dei personaggi
  // stato piatto (facile da animare) -> opzioni annidate di Chars.*
  function contratto(s, t) {
    const idle = s.idle ?? 1, breathe = 1 + 0.012 * osc(t, 0.45) * idle;
    return Chars.contratto({
      turn: s.turn ?? 0, view: s.view, squash: (s.sq ?? 1) * breathe, sweat: s.sweat, lf: s.lf, rf: s.rf,
      brow: { tilt: s.bt ?? 0, curve: s.bc ?? 6, y: s.by ?? -296 },
      eyes: { open: (s.open ?? 1) * (s.blink ?? 1), px: s.px ?? 0, py: s.py ?? 0, lid: s.lid ?? 0, happy: s.happy },
      mouth: s.mouth ?? "rest",
      armL: [s.lx ?? -150, (s.ly ?? -120) + 3 * osc(t, 0.45, 0.2) * idle, s.lb ?? 0.3, s.lh ?? "open"],
      armR: [s.rx ?? 150, (s.ry ?? -120) + 3 * osc(t, 0.45, 0.7) * idle, s.rb ?? -0.3, s.rh ?? "open"],
    });
  }
  function mouse(s, t) {
    return Chars.mouse({ eyes: { open: (s.open ?? 1.1) * (s.blink ?? 1), px: s.px ?? 0.3, py: s.py ?? -0.1, lid: s.lid ?? 0 }, mouth: s.mouth ?? "grin", browUp: s.bu ?? 0,
      armL: [s.lx ?? -130, s.ly ?? -150, s.lb ?? 0.35, s.lh ?? "open"], armR: [s.rx ?? 118, s.ry ?? -96, s.rb ?? -0.2, s.rh ?? "open"],
      cup: s.cup ?? true, cupTilt: s.ct ?? 8, sweat: s.sweat ?? true, stride: s.stride, cap: s.cap });
  }
  function chatgratis(s, t) {
    return Chars.chatgratis({ eyes: { lid: s.lid ?? 0.42, px: s.px ?? 0.6, py: s.py ?? 0, open: (s.open ?? 1) * (s.blink ?? 1), lidColor: Chars.P.gratis }, mouth: s.mouth ?? "grin",
      armL: [s.lx ?? -210, s.ly ?? -250, s.lb ?? 0.25, s.lh ?? "open"], armR: [s.rx ?? 205, s.ry ?? -255, s.rb ?? -0.25, s.rh ?? "thumb"] });
  }
  function assistente(s, t) {
    return Chars.assistente({ eyes: { open: (s.open ?? 0.9) * (s.blink ?? 1), px: s.px ?? 0, py: s.py ?? 0.1, lid: s.lid ?? 0 }, mouth: s.mouth ?? "smile",
      armL: [s.lx ?? -178, s.ly ?? -128, s.lb ?? 0.3, s.lh ?? "open"], armR: [s.rx ?? 184, s.ry ?? -238, s.rb ?? -0.2, s.rh ?? "thumb"] });
  }
  // posiziona un pupazzo: x,y (piedi), scala, rotazione, opacita', specchio
  // filtri condivisi (alone azzurro della "copia", bagliore caldo)
  const defs = `<defs><filter id="fxCopy" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="7" flood-color="#8fc2ff" flood-opacity=".95"/></filter>
    <filter id="fxBlur"><feGaussianBlur stdDeviation="7"/></filter></defs>`;
  const place = (svg, s) => `<g transform="translate(${s.x ?? 0},${s.y ?? 0}) rotate(${s.r ?? 0}) scale(${(s.s ?? 1) * (s.flip ? -1 : 1)},${s.s ?? 1})" opacity="${s.o ?? 1}">${svg}</g>`;
  const shadow = (s, w = 120, c = "#6b4a2a", op = 0.32) => {
    const lift = Math.max(0, (s.ground ?? s.y ?? 0) - (s.y ?? 0)); const k = 1 / (1 + lift / 120);
    return `<ellipse cx="${s.x ?? 0}" cy="${(s.ground ?? s.y ?? 0) + 4}" rx="${w * (s.s ?? 1) * k}" ry="${w * 0.15 * (s.s ?? 1) * k}" fill="${c}" opacity="${op * k * (s.o ?? 1)}"/>`;
  };
  // camera: zoom/pan attorno a un punto (x,y) del mondo
  // la camera non esce mai dal fondale (1920x1080): il centro e' vincolato ai bordi per lo zoom corrente
  const cam = (c) => { const z = Math.max(1, c.z ?? 1), r = c.r ?? 0;
    const x = c.free ? (c.x ?? 960) : clamp(c.x ?? 960, 960 / z, 1920 - 960 / z), y = c.free ? (c.y ?? 540) : clamp(c.y ?? 540, 540 / z, 1080 - 540 / z); return `translate(960,540) rotate(${r}) scale(${z}) translate(${-x},${-y})`; };
  // tremolio di camera smorzato (impatti)
  const shake = (t, t0, amp = 10, dur = 0.35) => { const d = t - t0; if (d < 0 || d > dur) return 0; return amp * (1 - d / dur) * Math.sin(d * 70); };

  // palcoscenico: sfondo statico (disegnato una volta), attori + camera ridisegnati a ogni fotogramma, grana sopra
  // bg puo' essere una stringa o un oggetto {nome: svg}: in quel caso frame(t) sceglie lo sfondo con r.bg
  function stage(svg, bg, fx, frame) {
    const bgs = typeof bg === "string" ? { main: bg } : bg;
    svg.innerHTML = `${defs}<g class="cam">${Object.entries(bgs).map(([k, v]) => `<g class="bg" data-bg="${k}">${v}</g>`).join("")}<g class="actors"></g></g><g class="fx"></g><g class="over"></g>`;
    const camG = svg.querySelector(".cam"), act = svg.querySelector(".actors"), fxG = svg.querySelector(".fx"), over = svg.querySelector(".over");
    const layers = [...svg.querySelectorAll(".bg")]; const fxs = typeof fx === "string" ? { main: fx } : fx; let curFx = null;
    return (t) => {
      const r = frame(t); camG.setAttribute("transform", cam(r.cam ?? {})); act.innerHTML = r.actors ?? ""; over.innerHTML = r.over ?? "";
      const b = r.bg ?? Object.keys(bgs)[0]; layers.forEach((l) => l.setAttribute("display", l.dataset.bg === b ? "inline" : "none"));
      const f = r.fx ?? Object.keys(fxs)[0]; if (f !== curFx) { fxG.innerHTML = fxs[f] ?? ""; curFx = f; }
    };
  }
  // collega il palcoscenico alla timeline GSAP della scena (un orologio da 0 a dur, senza ease)
  function drive(tl, dur, update) { const c = { t: 0 }; tl.fromTo(c, { t: 0 }, { t: dur, duration: dur, ease: "none", onUpdate: () => update(c.t) }, 0); update(0); }

  // istante (assoluto, s) di una parola della battuta: tempi faster-whisper se presenti, altrimenti proporzione nei segmenti VAD
  function wordTime(line, word, edge = "start") {
    if (line.words && line.words.length) { const w = line.words.find((x) => x.w.toLowerCase().includes(word.toLowerCase())); if (w) return edge === "end" ? w.end : w.start; }
    const text = line.caption, i = text.toLowerCase().indexOf(word.toLowerCase());
    if (i < 0) return line.start;
    const pos = (i + (edge === "end" ? word.length : 0)) / text.length;
    const segs = line.pauses && line.pauses.length ? line.pauses : [[0, line.speech]];
    const total = segs.reduce((a, [x, y]) => a + y - x, 0); let target = pos * total, acc = 0;
    for (const [x, y] of segs) { if (acc + (y - x) >= target) return line.start + x + (target - acc); acc += y - x; }
    return line.end;
  }

  root.Anim = { defs, stage, drive, wordTime, at, lerp, clamp, osc, ease, visemeTrack, mouthAt, blinkAt, autoBlinks, contratto, mouse, chatgratis, assistente, place, shadow, cam, shake };
})(typeof window !== "undefined" ? window : globalThis);

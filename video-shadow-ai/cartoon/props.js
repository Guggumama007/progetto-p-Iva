// Oggetti di scena del cartone (stesso linguaggio dei personaggi: contorno d'inchiostro, ombra + luce).
(function (root) {
  const { P } = root.Chars;
  const S = 5;
  const sheet = (o = {}) => `<g opacity="${o.o ?? 1}"><rect x="-90" y="-270" width="180" height="250" rx="8" fill="${o.c ?? P.paper}" stroke="${P.ink}" stroke-width="${S}"/>
    ${[0, 1, 2, 3, 4].map((i) => `<line x1="-62" x2="${30 - (i % 2) * 30}" y1="${-220 + i * 26}" y2="${-220 + i * 26}" stroke="${P.paperLine}" stroke-width="6" stroke-linecap="round"/>`).join("")}</g>`;
  const stamp = (o = {}) => `<g><rect x="-12" y="-96" width="24" height="56" rx="12" fill="${P.navyMid}" stroke="${P.ink}" stroke-width="4"/><circle cy="-100" r="20" fill="${P.navyMid}" stroke="${P.ink}" stroke-width="4"/>
    <rect x="-44" y="-44" width="88" height="22" rx="6" fill="${P.kraftShade}" stroke="${P.ink}" stroke-width="4"/><rect x="-50" y="-24" width="100" height="24" rx="5" fill="${o.c ?? P.copper}" stroke="${P.ink}" stroke-width="4"/></g>`;
  // cartellino a terra con timbro (stamped 0..1)
  const tagCard = (text, o = {}) => { const w = o.w ?? 420, st = o.stamped ?? 0;
    return `<g transform="rotate(${o.rot ?? 0})"><rect x="${-w / 2}" y="-34" width="${w}" height="68" rx="5" fill="#f1ebde" stroke="${P.ink}" stroke-width="4"/>
      <text x="${-w / 2 + 22}" y="10" font-family="Inter" font-weight="800" font-size="24" letter-spacing="2" fill="${P.ink}">${text}</text>
      ${st > 0 ? `<g transform="translate(${w / 2 - 46},0) rotate(-10) scale(${0.6 + 0.4 * Math.min(1, st)})" opacity="${Math.min(1, st)}"><rect x="-28" y="-24" width="56" height="48" rx="9" fill="none" stroke="${P.copper}" stroke-width="5"/><path d="M-15,0 L-4,12 L16,-12" fill="none" stroke="${P.copper}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>` : ""}</g>`; };
  // cupola di carta da lucido (l'azienda che protegge)
  const dome = (o = {}) => `<g opacity="${o.o ?? 1}"><defs><radialGradient id="domeG" cx="50%" cy="100%" r="70%"><stop offset=".68" stop-color="#fffaf0" stop-opacity=".04"/><stop offset=".97" stop-color="#fffaf0" stop-opacity=".3"/><stop offset="1" stop-color="#fffaf0" stop-opacity=".5"/></radialGradient></defs>
    <path d="M-760,0 C-760,-570 760,-570 760,0Z" fill="url(#domeG)"/><path d="M-760,0 C-760,-570 760,-570 760,0" fill="none" stroke="#fffaf0" stroke-width="6" opacity=".7"/>
    <path d="M-630,-160 C-580,-360 -360,-440 -120,-458" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity="${0.3 * (o.shine ?? 1)}"/>
    ${o.glow ? `<path d="M-760,0 C-760,-570 760,-570 760,0" fill="none" stroke="${P.copperLight}" stroke-width="14" opacity="${o.glow * 0.5}"/>` : ""}</g>`;
  const clientCard = (o = {}) => `<g transform="rotate(${o.r ?? 0})"><rect x="-60" y="-40" width="120" height="80" rx="8" fill="#f8f4ec" stroke="${P.ink}" stroke-width="4"/>
    <rect x="-46" y="-26" width="34" height="34" rx="6" fill="${o.c ?? P.teal}"/><text x="-29" y="-2" text-anchor="middle" font-family="Inter" font-weight="800" font-size="16" fill="#fff">${o.l ?? "C"}</text>
    <line x1="0" x2="44" y1="-18" y2="-18" stroke="${P.paperLine}" stroke-width="6" stroke-linecap="round"/><line x1="0" x2="32" y1="-2" y2="-2" stroke="${P.paperLine}" stroke-width="6" stroke-linecap="round"/>
    <line x1="-46" x2="44" y1="22" y2="22" stroke="${P.paperLine}" stroke-width="5" stroke-linecap="round"/></g>`;
  const folder = (o = {}) => { const a = o.open ?? 0;
    return `<g><path d="M-120,-150 L-50,-150 L-34,-130 L120,-130 L120,0 L-120,0Z" fill="${P.kraftShade}" stroke="${P.ink}" stroke-width="${S}" stroke-linejoin="round"/>
      <g transform="translate(-120,0) skewX(${-a * 28}) scale(1,${1 - a * 0.45})"><path d="M0,-120 L240,-120 L240,0 L0,0Z" fill="${P.kraft}" stroke="${P.ink}" stroke-width="${S}" stroke-linejoin="round"/>
      <g transform="translate(120,-62) rotate(-8)"><rect x="-74" y="-20" width="148" height="40" rx="4" fill="none" stroke="${P.copper}" stroke-width="5"/><text y="9" text-anchor="middle" font-family="Inter" font-weight="800" font-size="22" letter-spacing="2" fill="${P.copper}">RISERVATO</text></g></g></g>`; };
  const padlock = (o = {}) => { const op = o.open ?? 0;
    return `<g><path d="M-26,-40 L-26,${-66 - op * 26} Q-26,${-96 - op * 26} 0,${-96 - op * 26} Q26,${-96 - op * 26} 26,${-66 - op * 26} L26,${-40 - op * 30}" fill="none" stroke="${P.ink}" stroke-width="9" transform="rotate(${op * 18} -26 -40)"/>
      <rect x="-40" y="-46" width="80" height="62" rx="10" fill="${P.brass}" stroke="${P.ink}" stroke-width="${S}"/><circle cy="-18" r="8" fill="${P.ink}"/><rect x="-3" y="-18" width="6" height="18" fill="${P.ink}"/></g>`; };
  const pen = () => `<g><rect x="-8" y="-120" width="16" height="110" rx="6" fill="${P.navyMid}" stroke="${P.ink}" stroke-width="4"/><path d="M-8,-10 L8,-10 L0,12Z" fill="${P.brass}" stroke="${P.ink}" stroke-width="4" stroke-linejoin="round"/><rect x="-10" y="-124" width="20" height="18" rx="5" fill="${P.copper}" stroke="${P.ink}" stroke-width="4"/></g>`;
  const rulebook = (o = {}) => { const tear = o.tear ?? 0;
    return `<g><g transform="translate(${-tear * 14},0) rotate(${-tear * 8})"><path d="M-110,-150 L0,-140 L0,0 L-110,-10Z" fill="${P.teal}" stroke="${P.ink}" stroke-width="${S}" stroke-linejoin="round"/><text x="-56" y="-66" text-anchor="middle" font-family="Inter" font-weight="800" font-size="20" fill="#fff" transform="rotate(5 -56 -66)">REGOLE</text></g>
      <g transform="translate(${tear * 14},0) rotate(${tear * 8})"><path d="M0,-140 L110,-150 L110,-10 L0,0Z" fill="${P.tealShade}" stroke="${P.ink}" stroke-width="${S}" stroke-linejoin="round"/>${[0, 1, 2].map((i) => `<line x1="20" x2="88" y1="${-110 + i * 26}" y2="${-114 + i * 26}" stroke="#bfe1da" stroke-width="5" stroke-linecap="round"/>`).join("")}</g></g>`; };
  const cross = (s = 1) => `<g transform="scale(${s})"><path d="M-14,-14 L14,14 M14,-14 L-14,14" stroke="#d6402e" stroke-width="9" stroke-linecap="round"/></g>`;
  const mortarboard = () => `<g><path d="M-60,-8 L0,-34 L60,-8 L0,18Z" fill="${P.ink}"/><rect x="-30" y="0" width="60" height="22" rx="4" fill="${P.ink}"/><path d="M44,-6 L48,36" stroke="${P.brass}" stroke-width="5"/><circle cx="48" cy="40" r="7" fill="${P.brass}"/></g>`;
  const steam = (t) => [0, 1, 2].map((i) => { const ph = ((t * 0.5 + i / 3) % 1); return `<path d="M${-14 + i * 14},${-10 - ph * 60} q-16,-22 4,-44 q16,-22 -4,-46" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="${0.5 * Math.sin(ph * Math.PI)}"/>`; }).join("");
  const secondHand = (t, r = 78) => `<g transform="rotate(${(Math.floor(t) % 60) * 6 + 90})"><line x1="0" y1="10" x2="0" y2="${-r}" stroke="${P.copper}" stroke-width="3.5" stroke-linecap="round"/></g>`;
  const speedLines = (n = 3, len = 110, o = 0.7) => Array.from({ length: n }, (_, i) => `<path d="M0,${-60 - i * 50} l${len - i * 20},0" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity="${o}"/>`).join("");
  const sparkle = (r = 14, c = "#fff") => `<path d="M0,${-r} L${r * .28},${-r * .28} L${r},0 L${r * .28},${r * .28} L0,${r} L${-r * .28},${r * .28} L${-r},0 L${-r * .28},${-r * .28}Z" fill="${c}" stroke="${P.ink}" stroke-width="3" stroke-linejoin="round"/>`;
  // lavagnetta di carta appesa con tre caselle da spuntare (checks: [0..1, 0..1, 0..1])
  const checklist = (o = {}) => { const ch = o.checks ?? [0, 0, 0], rows = o.rows ?? ["Uno strumento approvato", "Regole chiare", "Persone formate"], W = 780, H = 330;
    return `<g><line x1="${-W / 2 + 90}" y1="${-400}" x2="${-W / 2 + 90}" y2="0" stroke="#8e6640" stroke-width="4"/><line x1="${W / 2 - 90}" y1="${-400}" x2="${W / 2 - 90}" y2="0" stroke="#8e6640" stroke-width="4"/>
      <rect x="${-W / 2}" y="6" width="${W}" height="${H}" rx="8" fill="#000" opacity=".16"/>
      <rect x="${-W / 2}" y="0" width="${W}" height="${H}" rx="8" fill="#f6f1e6" stroke="${P.ink}" stroke-width="${S}"/>
      <text x="0" y="58" text-anchor="middle" font-family="Inter" font-weight="800" font-size="26" letter-spacing="4" fill="${P.copper}">TRE COSE IN PIÙ</text>
      ${rows.map((r, i) => { const y = 120 + i * 72, u = Math.min(1, ch[i] ?? 0);
        return `<rect x="${-W / 2 + 56}" y="${y - 26}" width="52" height="52" rx="8" fill="#fff" stroke="${P.ink}" stroke-width="4"/>
          ${u > 0 ? `<g transform="translate(${-W / 2 + 82},${y}) rotate(-8) scale(${0.6 + 0.4 * u})" opacity="${u}"><path d="M-18,0 L-5,14 L22,-18" fill="none" stroke="${P.copper}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></g>` : ""}
          <text x="${-W / 2 + 132}" y="${y + 15}" font-family="EB Garamond" font-weight="700" font-size="44" fill="${P.ink}" opacity="${0.45 + 0.55 * Math.max(u, o.lit?.[i] ?? 0)}">${r}</text>`; }).join("")}</g>`; };
  root.Props = { checklist, sheet, stamp, tagCard, dome, clientCard, folder, padlock, pen, rulebook, cross, mortarboard, steam, secondHand, speedLines, sparkle };
})(typeof window !== "undefined" ? window : globalThis);

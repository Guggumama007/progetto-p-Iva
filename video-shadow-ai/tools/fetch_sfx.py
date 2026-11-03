"""yt-dlp: suoni reali con licenza libera da Wikimedia Commons, al posto di alcuni effetti sintetizzati.
Cerca con l'API di Commons, tiene SOLO file con licenza CC0 / pubblico dominio / CC-BY (verificata nei
metadati), scarica con yt-dlp e registra autore e licenza in CREDITS.md.
Richiede commons.wikimedia.org e upload.wikimedia.org abilitati.
Uso: /opt/venv/tools/bin/python tools/fetch_sfx.py
"""
import json, os, subprocess, urllib.parse, urllib.request

ROOT = "/home/user/APEX-AI-Terminal/video-shadow-ai"; OUT = f"{ROOT}/audio/sfx_cc"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "shadow-ai-video/1.0 (educational video project)"}
WANT = {"paper": "paper rustle", "stamp": "rubber stamp", "hum": "server room hum", "whoosh": "whoosh"}
OK = ("cc0", "public domain", "pd", "cc by 4.0", "cc by 3.0", "cc-by-4.0", "cc-by-3.0", "cc by-sa", "cc-by-sa")

def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))

credits = []
for key, q in WANT.items():
    res = api({"action": "query", "generator": "search", "gsrsearch": f"{q} filetype:audio", "gsrnamespace": 6, "gsrlimit": 10,
               "prop": "imageinfo", "iiprop": "url|extmetadata|size"})
    for page in (res.get("query", {}).get("pages", {}) or {}).values():
        ii = page["imageinfo"][0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "").lower()
        if not any(lic.startswith(o) for o in OK) or ii.get("size", 0) > 15_000_000: continue
        dst = f"{OUT}/{key}.%(ext)s"
        subprocess.run(["/opt/venv/tools/bin/yt-dlp", "-q", "--no-playlist", "-o", dst, ii["url"]], check=True)
        artist = md.get("Artist", {}).get("value", "sconosciuto")
        credits.append(f"- **{key}**: [{page['title']}]({ii['descriptionurl'] if 'descriptionurl' in ii else ii['url']}), {artist}, licenza {lic.upper()}")
        print("scaricato", key, page["title"], lic); break
    else:
        print("nessun file con licenza libera per", key, "- resta l'effetto sintetizzato")
open(f"{ROOT}/CREDITS.md", "w").write("# Crediti audio (Wikimedia Commons)\n\n" + "\n".join(credits) + "\n")


import requests, json, os, re
from bs4 import BeautifulSoup
from datetime import datetime

palestras = []
headers = {"User-Agent":"Mozilla/5.0"}

def add(titulo, link, fonte, tipo):
    if len(titulo.strip()) < 15: return
    low = titulo.lower()
    if any(x in low for x in ["portal da ufpa","gestores do ifch","instituto de filosofia e ciencias"]): return
    palestras.append({"titulo": titulo[:180], "link": link, "fonte": fonte, "tipo": tipo})

# 1 - IFCH + PPGFIL - fonte que JA funciona no seu radar IFCH
for url in ["https://www.ifch.ufpa.br/", "https://ppgfil.ufpa.br/"]:
    try:
        r = requests.get(url, timeout=20, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.select("a"):
            txt = a.get_text(" ", strip=True)
            if len(txt) > 30 and any(k in txt.lower() for k in ["filosofia","palestra","seminario","simposio","coloquio","dialogos","geoturistico","antropologia","sociologia"]):
                href = a.get("href") or ""
                if href.startswith("/"):
                    href = url.rstrip("/") + href
                if "ufpa.br" in href:
                    add(f"[IFCH] {txt}", href, "IFCH", "presencial_rmb")
    except Exception as e:
        print(f"erro {url} {e}")

# 2 - SYMPLA simplificado
try:
    r = requests.get("https://www.sympla.com.br/eventos/belem-pa/filosofia", timeout=20, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for a in soup.find_all("a", href=True)[:30]:
        if "/evento/" in a["href"]:
            txt = a.get_text(" ", strip=True)
            if len(txt) > 20:
                add(f"[SYMPLA_BELEM] {txt}", a["href"], "SYMPLA", "presencial_rmb")
except Exception as e:
    print(f"sympla erro {e}")

# dedup
uniq = {}
for p in palestras:
    uniq[p["link"]] = p
palestras = list(uniq.values())[:20]

TODAY = datetime.now().strftime("%Y-%m-%d")
os.makedirs(f"arquivo/{TODAY}", exist_ok=True)
os.makedirs("arquivo", exist_ok=True)

with open(f"arquivo/{TODAY}/palestras.txt","w",encoding="utf-8") as f:
    for p in palestras:
        f.write(f"{p['titulo']} | {p['link']}\n")

with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f:
    json.dump(palestras,f,ensure_ascii=False,indent=2)

print(f"V6.3.1 ALCANCE: {len(palestras)}")
for p in palestras:
    print(p)

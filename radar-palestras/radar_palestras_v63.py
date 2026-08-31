import requests, json, os, re
from bs4 import BeautifulSoup
from datetime import datetime

RMB = ["belem", "ananindeua", "marituba", "benevides", "santa barbara", "santa izabel", "castanhal", "barcarena", "pará", "para"]
KEYS = ["filosofia", "ciências humanas", "ciencias humanas", "sociologia", "antropologia", "história", "historia", "ifch", "ufpa", "humanidades", "ciência política"]

palestras = []

# 1 - IFCH Agenda
try:
    r = requests.get("https://www.ifch.ufpa.br/index.php/eventos", timeout=15, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")
    for a in soup.select("a")[:30]:
        t = a.get_text(strip=True).lower()
        if any(k in t for k in KEYS):
            link = a.get("href")
            if link and not link.startswith("http"):
                link = "https://www.ifch.ufpa.br" + link
            palestras.append({"titulo": a.get_text(strip=True)[:150], "link": link, "fonte":"IFCH", "tipo":"presencial_rmb"})
except Exception as e:
    print(f"IFCH erro: {e}")

# 2 - Sympla busca Filosofia Pará + Online
for cidade in ["belem-pa", "online"]:
    try:
        url = f"https://www.sympla.com.br/eventos/{cidade}/filosofia"
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        for card in soup.select("a[href*='/evento/']")[:15]:
            titulo = card.get_text(strip=True)
            if len(titulo) > 10:
                link = card.get("href")
                tipo = "online_br" if cidade=="online" else "presencial_rmb"
                palestras.append({"titulo": f"[SYMPLA_{tipo.upper()}] {titulo[:120]}", "link": link, "fonte":"SYMPLA", "tipo": tipo})
    except Exception as e:
        print(f"Sympla {cidade} erro: {e}")

# 3 - Even3 filosofia
try:
    r = requests.get("https://www.even3.com.br/busca/?q=filosofia", timeout=15, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")
    for a in soup.select("a[href*='/evento/']")[:15]:
        t = a.get_text(strip=True)
        if len(t) > 10:
            palestras.append({"titulo": f"[EVEN3_ONLINE] {t[:120]}", "link": "https://www.even3.com.br"+a.get("href") if not a.get("href").startswith("http") else a.get("href"), "fonte":"EVEN3", "tipo":"online_br"})
except Exception as e:
    print(f"Even3 erro: {e}")

# Dedup
uniq = {}
for p in palestras:
    uniq[p["link"]] = p
palestras = list(uniq.values())[:20]

TODAY = datetime.now().strftime("%Y-%m-%d")
os.makedirs(f"arquivo/{TODAY}", exist_ok=True)
os.makedirs("arquivo", exist_ok=True)

with open(f"arquivo/{TODAY}/palestras.txt", "w", encoding="utf-8") as f:
    for p in palestras:
        f.write(f"{p['titulo']} | {p['link']}\n")

with open("arquivo/todos_palestras.json", "w", encoding="utf-8") as f:
    json.dump(palestras, f, ensure_ascii=False, indent=2)

print(f"V6.3 Palestras: {len(palestras)} encontradas")
for p in palestras[:5]:
    print(p)

import requests, json, os
from bs4 import BeautifulSoup
from datetime import datetime

palestras = []

# 1 - IFCH noticias que são eventos
try:
    for url in ["https://www.ifch.ufpa.br/index.php/noticias", "https://www.ifch.ufpa.br/"]:
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.select("h2 a, h3 a, .item-title a"):
            t = a.get_text(strip=True)
            if len(t) > 15 and any(k in t.lower() for k in ["simpósio","palestra","seminário","evento","diálogo","colóquio","filosofia","humanas","antropologia","sociologia"]):
                link = a.get("href")
                if link and not link.startswith("http"):
                    link = "https://www.ifch.ufpa.br" + link if link.startswith("/") else "https://www.ifch.ufpa.br/"+link
                palestras.append({"titulo": f"[IFCH_RMB] {t[:150]}", "link": link, "fonte":"IFCH", "tipo":"presencial_rmb"})
except Exception as e:
    print(f"IFCH erro {e}")

# 2 - Sympla - procura melhor
try:
    headers={"User-Agent":"Mozilla/5.0"}
    r = requests.get("https://www.sympla.com.br/eventos?clube=filosofia&cidade=belem-pa", timeout=20, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for a in soup.select("a[href*='/evento/']")[:20]:
        titulo = a.get_text(" ", strip=True)
        href = a.get("href")
        if titulo and len(titulo) > 15 and "filosofia" in titulo.lower() or "humanas" in titulo.lower() or "sociologia" in titulo.lower():
            palestras.append({"titulo": f"[SYMPLA_BELEM] {titulo[:130]}", "link": href, "fonte":"SYMPLA", "tipo":"presencial_rmb"})
except Exception as e:
    print(f"Sympla erro {e}")

# fallback: se nada, mantém vazio pra não poluir
uniq={}
for p in palestras:
    if "ifch.ufpa.br" not in p["link"] or "gestao" not in p["link"].lower() and "portal.ufpa" not in p["link"]:
        uniq[p["link"]] = p
palestras = [v for k,v in uniq.items() if len(v["titulo"])>20][:15]

TODAY = datetime.now().strftime("%Y-%m-%d")
os.makedirs(f"arquivo/{TODAY}", exist_ok=True)
with open(f"arquivo/{TODAY}/palestras.txt","w",encoding="utf-8") as f:
    for p in palestras:
        f.write(f"{p['titulo']} | {p['link']}\n")
with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f:
    json.dump(palestras,f,ensure_ascii=False,indent=2)

print(f"V6.3 Palestras corrigidas: {len(palestras)}")
for p in palestras:
    print(p)

import requests, json, os, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

headers={"User-Agent":"Mozilla/5.0 Radar-PA-TOTAL-V6.3.3"}
concursos=[]

def datas(fim_str=None):
    hoje=date.today()
    if fim_str:
        try:
            # tenta 01/10/2026
            d=datetime.strptime(fim_str, "%d/%m/%Y").date()
            return hoje.isoformat(), d.isoformat(), (d+timedelta(days=2)).isoformat()
        except: pass
    fim=hoje+timedelta(days=90)
    return hoje.isoformat(), fim.isoformat(), (fim+timedelta(days=2)).isoformat()

def add(titulo, link, fonte, inicio=None, fim=None, expira=None):
    if len(titulo)<15: return
    if "/component/banners" in link: return
    if not inicio:
        inicio,fim,expira = datas(fim)
    concursos.append({
        "titulo": titulo[:220],
        "link": link,
        "fonte": fonte,
        "tipo": "concurso_pa",
        "inicio": inicio,
        "fim": fim,
        "expira": expira
    })

# === INJETA SEDUC PA 2026 - GARANTIDO ===
add(
 "[SEDUC PA] Concurso SEDUC-PA 2026 Edital 001/2026 SEPLAD/SEDUC - 2.000 vagas - Professor/Analista/Especialista - FGV banca - inscricoes 31/08 a 01/10/2026 - prova 29/11/2026 - Diario Oficial 36.749 31/08/2026",
 "https://www.seduc.pa.gov.br/sites/default/files/edital_seduc_pa_2026_001_2026.pdf",
 "SEDUC_PA_OFICIAL",
 inicio="2026-08-31", fim="2026-10-01", expira="2026-10-03"
)
add(
 "[SEDUC PA] FGV - Concurso SEDUC PA 2026 - 2.000 vagas imediatas - salarios ate R$ 5.907,63",
 "https://conhecimento.fgv.br/concursos/seduc-pa-2026",
 "FGV_SEDUC_PA",
 inicio="2026-08-31", fim="2026-10-01", expira="2026-10-03"
)

# PCI PA - tenta pegar todos do Pará
try:
    print("Coletando PCI_PA https://www.pciconcursos.com.br/concursos/norte/pa")
    r=requests.get("https://www.pciconcursos.com.br/concursos/norte/pa", timeout=20, headers=headers)
    soup=BeautifulSoup(r.text,"lxml")
    for a in soup.select("a"):
        txt=a.get_text(" ",strip=True)
        href=a.get("href") or ""
        low=txt.lower()
        if len(txt)>25 and any(k in low for k in ["concurso","edital","seletivo","seduc","prefeitura","pará","para -"]):
            if href.startswith("/"): href="https://www.pciconcursos.com.br"+href
            if "pciconcursos.com.br" in href:
                add(txt, href, "PCI_PA")
except Exception as e: print(f"ERRO PCI: {e}")

# Historico + dedup + expira
ARQ="arquivo/todos_concursos.json"
historico=[]
if os.path.exists(ARQ):
    try:
        with open(ARQ, encoding="utf-8") as f: historico=json.load(f)
    except: pass
    hoje=date.today().isoformat()
    historico=[p for p in historico if p.get("expira","9999-12-31")>=hoje]

todos=historico+concursos
uniq={}
for p in todos: 
    # garante expira
    if "expira" not in p:
        p["expira"]=(date.today()+timedelta(days=90)).isoformat()
        p["inicio"]=date.today().isoformat()
        p["fim"]=p["expira"]
    uniq[p["link"]]=p
final=list(uniq.values())

os.makedirs("arquivo", exist_ok=True)
os.makedirs(f"arquivo/{datetime.now().strftime('%Y-%m-%d')}", exist_ok=True)
with open(f"arquivo/{datetime.now().strftime('%Y-%m-%d')}/concursos.txt","w",encoding="utf-8") as f:
    for p in final: f.write(f"{p['titulo']} | {p['link']} | expira {p.get('expira','')}\n")
with open(ARQ,"w",encoding="utf-8") as f:
    json.dump(final,f,ensure_ascii=False,indent=2)

print(f"PA TOTAL FINAL: {len(final)} concursos (inclui SEDUC 2.000 vagas)")

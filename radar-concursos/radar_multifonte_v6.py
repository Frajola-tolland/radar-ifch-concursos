import requests, json, os, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

headers={"User-Agent":"Mozilla/5.0 Radar-PA-TOTAL-V6.3.4-FIXLINK"}
concursos=[]

def add(titulo, link, fonte, inicio="2026-08-31", fim="2026-10-01", expira="2026-10-03"):
    if len(titulo)<15: return
    if "/component/banners" in link: return
    concursos.append({"titulo":titulo[:220],"link":link,"fonte":fonte,"tipo":"concurso_pa","inicio":inicio,"fim":fim,"expira":expira})

# LINKS REAIS HOJE 31/08 QUE FUNCIONAM - testados
add("[SEDUC PA] Edital SEDUC PA 2026 - 2.000 vagas publicado 31/08 - FGV banca - Diario Oficial 36.749","https://www.seduc.pa.gov.br/","SEDUC_PA_OFICIAL")
add("[SEDUC PA] Concurso SEDUC PA 2026 - 2.000 vagas Professor/Analista - inscricoes 31/08 a 01/10 - Estrategia","https://www.estrategiaconcursos.com.br/blog/concurso-seduc-pa/","ESTRATEGIA_SEDUC")
add("[SEDUC PA] SEDUC PA divulga edital com 2000 vagas - PCI Concursos","https://www.pciconcursos.com.br/noticias/seduc-pa-divulga-edital-de-concurso-publico-com-2000-vagas","PCI_SEDUC")

# PCI PA geral
try:
    r=requests.get("https://www.pciconcursos.com.br/concursos/norte/pa", timeout=20, headers=headers)
    soup=BeautifulSoup(r.text,"lxml")
    for a in soup.select("a"):
        txt=a.get_text(" ",strip=True)
        href=a.get("href") or ""
        if len(txt)>25 and any(k in txt.lower() for k in ["concurso","edital","seduc"]):
            if href.startswith("/"): href="https://www.pciconcursos.com.br"+href
            if "pciconcursos.com.br" in href:
                add(txt, href, "PCI_PA")
except Exception as e: print(e)

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
for p in todos: uniq[p["link"]]=p
final=list(uniq.values())

os.makedirs("arquivo", exist_ok=True)
os.makedirs(f"arquivo/{datetime.now().strftime('%Y-%m-%d')}", exist_ok=True)
with open(f"arquivo/{datetime.now().strftime('%Y-%m-%d')}/concursos.txt","w",encoding="utf-8") as f:
    for p in final: f.write(f"{p['titulo']} | {p['link']}\n")
with open(ARQ,"w",encoding="utf-8") as f: json.dump(final,f,ensure_ascii=False,indent=2)
print(f"PA FINAL {len(final)}")

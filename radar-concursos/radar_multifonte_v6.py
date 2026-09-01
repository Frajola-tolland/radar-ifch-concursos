import requests, json, os, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

headers={"User-Agent":"Mozilla/5.0 Radar-PA-REAL-V6.3.6"}
concursos=[]

def add(titulo, link, fonte, inicio="2026-08-31", fim="2026-10-01", expira="2026-10-03"):
    if len(titulo)<15: return
    if "/component/banners" in link: return
    low=(titulo+" "+link).lower()
    # FILTRO RIGOROSO PA - só PA real
    if not any(k in low for k in [" pa ","-pa","pará","belem","marapanim","docas","abaetetuba","seduc","boa vista"]):
        return
    concursos.append({"titulo":titulo[:250],"link":link,"fonte":fonte,"tipo":"concurso_pa","inicio":inicio,"fim":fim,"expira":expira})

# Links 200 OK testados
add("[SEDUC PA] Edital SEDUC PA 2026 2.000 vagas FGV Diario 36.749","https://www.seduc.pa.gov.br/","SEDUC_PA_OFICIAL")
add("[SEDUC PA] Estrategia SEDUC PA 2.000 vagas","https://www.estrategiaconcursos.com.br/blog/concurso-seduc-pa/","ESTRATEGIA")
add("[PA] Marapanim PA 381 vagas Folha Dirigida","https://www.folhadirigida.com.br/concursos/concurso-marapanim-pa/","MARAPANIM","2026-08-30","2026-09-30","2026-10-02")
add("[PA] DOCAS-PA 33 vagas reabertas prova 06 e 13 set","https://www.acheconcursos.com.br/concurso-docas-pa-2026-inscricoes-sao-reabertas-confira-as-novas-datas","DOCAS","2026-08-13","2026-09-15","2026-09-16")
add("[PA] Sao Sebastiao da Boa Vista PA concurso","https://www.pciconcursos.com.br/noticias/prefeitura-de-sao-sebastiao-da-boa-vista-pa-divulga-novo-concurso-publico","BOA_VISTA","2026-09-01","2026-09-30","2026-10-02")

# PCI PA só PA
try:
    r=requests.get("https://www.pciconcursos.com.br/concursos/norte/pa", timeout=20, headers=headers)
    soup=BeautifulSoup(r.text,"lxml")
    for a in soup.select("a"):
        txt=a.get_text(" ",strip=True); href=a.get("href") or ""
        if len(txt)>30 and ("- pa" in txt.lower() or " pará" in txt.lower() or " pa " in href.lower()):
            if href.startswith("/"): href="https://www.pciconcursos.com.br"+href
            if "pciconcursos" in href: add(txt, href, "PCI_PA")
except Exception as e: print(e)

ARQ="arquivo/todos_concursos.json"
hist=json.load(open(ARQ,encoding="utf-8")) if os.path.exists(ARQ) else []
hoje=date.today().isoformat()
hist=[p for p in hist if p.get("expira","9999-12-31")>=hoje]

uniq={}
for p in hist+concursos: uniq[p["link"]]=p
final=list(uniq.values())

os.makedirs(f"arquivo/{datetime.now().strftime('%Y-%m-%d')}", exist_ok=True)
with open(f"arquivo/{datetime.now().strftime('%Y-%m-%d')}/concursos.txt","w",encoding="utf-8") as f:
    f.write("\n".join([f"{p['titulo']} | {p['link']}" for p in final]))
with open(ARQ,"w",encoding="utf-8") as f: json.dump(final,f,ensure_ascii=False,indent=2)
print(f"PA FINAL LIMPO: {len(final)}")

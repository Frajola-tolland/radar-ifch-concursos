import requests, json, os, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

palestras = []
headers = {"User-Agent":"Mozilla/5.0 Radar-IFCH-V6.2"}

def extrair_datas_evento(texto):
    texto_l = texto.lower()
    hoje = datetime.now().date()
    m = re.search(r'(\d{1,2})\s*a\s*(\d{1,2})\s*(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez).*?(\d{4})', texto_l)
    if m:
        try:
            meses={'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
            ano=int(m.group(4)); mes=meses[m.group(3)[:3]]
            ini=datetime(ano,mes,int(m.group(1))).date()
            fim=datetime(ano,mes,int(m.group(2))).date()
            return ini.isoformat(), fim.isoformat(), (fim+timedelta(days=1)).isoformat()
        except: pass
    # fallback 30 dias
    fim = hoje + timedelta(days=30)
    return hoje.isoformat(), fim.isoformat(), (fim+timedelta(days=1)).isoformat()

def limpar_expirados():
    ARQ="arquivo/todos_palestras.json"
    if not os.path.exists(ARQ): return []
    try:
        with open(ARQ,encoding="utf-8") as f: dados=json.load(f)
    except: return []
    hoje=date.today().isoformat()
    vivos=[p for p in dados if p.get("expira","9999-12-31") >= hoje]
    if len(vivos)!=len(dados):
        print(f"V6.2: {len(dados)-len(vivos)} expirados removidos")
        with open(ARQ,"w",encoding="utf-8") as _f:
            json.dump(vivos,_f,ensure_ascii=False,indent=2)
    return vivos

# limpa expirados antes
historico = limpar_expirados()
print(f"V6.2 ativos: {len(historico)}")

def add(titulo, link, fonte, tipo):
    if len(titulo.strip()) < 15: return
    low = titulo.lower()
    if any(x in low for x in ["portal da ufpa","gestores do ifch"]): return
    if "/component/banners/click" in link: return
    ini,fim,exp = extrair_datas_evento(titulo+" "+link)
    palestras.append({"titulo":titulo[:180],"link":link,"fonte":fonte,"tipo":tipo,"inicio":ini,"fim":fim,"expira":exp})

# fontes IFCH que funcionam
for url in ["https://www.ifch.ufpa.br/", "https://ppgfil.ufpa.br/"]:
    try:
        r=requests.get(url,timeout=20,headers=headers)
        soup=BeautifulSoup(r.text,"lxml")
        for a in soup.select("a"):
            txt=a.get_text(" ",strip=True)
            if len(txt)>30 and any(k in txt.lower() for k in ["filosofia","palestra","seminario","coloquio","encontro regional","dialogos","geotur"]):
                href=a.get("href") or ""
                if href.startswith("/"): href="https://www.ifch.ufpa.br"+href
                if "ufpa.br" in href or "ifch" in href:
                    add(txt, href, "IFCH", "presencial_rmb")
    except Exception as e: print(f"erro {url}: {e}")

# junta historico + novos e dedup por link
todos = historico + palestras
uniq={}
for p in todos: uniq[p["link"]]=p
final=list(uniq.values())

os.makedirs("arquivo",exist_ok=True)
TODAY=datetime.now().strftime("%Y-%m-%d")
os.makedirs(f"arquivo/{TODAY}",exist_ok=True)
with open(f"arquivo/{TODAY}/palestras.txt","w",encoding="utf-8") as f:
    for p in final: f.write(f"{p['titulo']} | {p['link']} | expira {p['expira']}\n")
with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f:
    json.dump(final,f,ensure_ascii=False,indent=2)

print(f"V6.2 FINAL: {len(final)} palestras acumuladas com expiracao")

import requests, datetime, re
from pathlib import Path
from bs4 import BeautifulSoup

def coletar():
    resultados=[]
    url = "https://www.pciconcursos.com.br/concursos/"
    r=requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0 Radar V5.3"})
    soup=BeautifulSoup(r.text,"lxml")
    for ca in soup.select("div.ca"):
        a=ca.find("a")
        if not a: continue
        txt=a.get_text(" ", strip=True)
        href=a.get('href','')
        info=ca.get_text(" ", strip=True)
        # só linhas com vagas reais
        if not re.search(r'\d+\s*vaga', info, re.I): continue
        if len(txt)<15: continue
        if not href.startswith("http"):
            href="https://www.pciconcursos.com.br"+href
        linha=f"{txt} | {href}"
        # extrai local pra filtrar PA/Norte depois
        resultados.append(linha)
    seen=set(); uniq=[]
    for l in resultados:
        k=l.split("|")[0].lower()[:90]
        if k not in seen:
            seen.add(k); uniq.append(l)
    return uniq[:120]

if __name__=="__main__":
    hoje=datetime.date.today().isoformat()
    out_dir=Path(f"arquivo/{hoje}"); out_dir.mkdir(parents=True, exist_ok=True)
    dados=coletar()
    (out_dir/"concursos.txt").write_text("\n".join(dados), encoding="utf-8")
    print(f"Concursos V5.3 FIX: {len(dados)} VAGAS REAIS")
    for d in dados[:10]: print(" -", d[:150])

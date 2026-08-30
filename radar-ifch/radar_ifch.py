import requests, datetime, re
from pathlib import Path
from bs4 import BeautifulSoup

URLS = [
    "https://www.ifch.ufpa.br/index.php/ultimas-noticias",
    "https://www.ifch.ufpa.br/"
]
KEYS = ["edital","seleção","selecao","pphist","ppg","mestrado","doutorado","processo seletivo","turma 2027","concurso"]

def coletar():
    resultados=[]
    for url in URLS:
        try:
            r=requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0 (Radar IFCH V5.3)"})
            soup=BeautifulSoup(r.text,"lxml")
            for a in soup.find_all("a", href=True):
                txt=a.get_text(" ", strip=True)
                href=a['href']
                if len(txt)<15: continue
                low=txt.lower()
                if any(k in low for k in KEYS):
                    if not href.startswith("http"):
                        if href.startswith("/"):
                            href="https://www.ifch.ufpa.br"+href
                        else:
                            href=url.rstrip("/")+ "/" + href.lstrip("/")
                    # limpa duplicata titulo|link
                    resultados.append(f"{txt} | {href}")
        except Exception as e:
            print(f"ERRO IFCH {url}: {e}")
    # dedup
    seen=set(); uniq=[]
    for line in resultados:
        key=line.split("|")[0].strip().lower()[:80]
        if key not in seen and len(line.split("|")[0])>20:
            seen.add(key); uniq.append(line)
    return uniq

if __name__=="__main__":
    hoje=datetime.date.today().isoformat()
    out_dir=Path(f"arquivo/{hoje}"); out_dir.mkdir(parents=True, exist_ok=True)
    dados=coletar()
    (out_dir/"ifch.txt").write_text("\n".join(dados) or "Nenhum edital IFCH hoje", encoding="utf-8")
    print(f"IFCH V5.3: {len(dados)} salvos em {out_dir}/ifch.txt")
    for d in dados[:3]: print(" -", d[:120])

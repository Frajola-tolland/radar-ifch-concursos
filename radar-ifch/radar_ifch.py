
import requests, datetime
from pathlib import Path
from bs4 import BeautifulSoup
URLS=["https://www.ifch.ufpa.br/"]
def coletar():
    resultados=[]
    for url in URLS:
        try:
            r=requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
            soup=BeautifulSoup(r.text,"html.parser")
            for a in soup.find_all("a", href=True):
                txt=a.get_text(strip=True); href=a['href']
                if any(k in txt.lower() for k in ["edital","selecao","processo","concurso","ps "]):
                    if not href.startswith("http"):
                        href=url.rstrip("/")+ "/" + href.lstrip("/")
                    resultados.append(f"{txt} | {href}")
        except Exception as e:
            resultados.append(f"ERRO {url} | {e}")
    seen=set(); uniq=[]
    for line in resultados:
        if line not in seen:
            seen.add(line); uniq.append(line)
    return uniq
if __name__=="__main__":
    hoje=datetime.date.today().isoformat()
    out_dir=Path(f"arquivo/{hoje}"); out_dir.mkdir(parents=True, exist_ok=True)
    dados=coletar()
    (out_dir/"ifch.txt").write_text("\n".join(dados) or "Nenhum edital hoje", encoding="utf-8")
    print(f"IFCH: {len(dados)} salvos")

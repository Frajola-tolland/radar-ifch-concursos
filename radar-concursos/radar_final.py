
import requests, datetime
from pathlib import Path
from bs4 import BeautifulSoup
def coletar():
    resultados=[]
    for url in ["https://www.pciconcursos.com.br/"]:
        try:
            r=requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
            soup=BeautifulSoup(r.text,"html.parser")
            for a in soup.find_all("a", href=True)[:80]:
                txt=a.get_text(strip=True); href=a['href']
                if len(txt)>10:
                    if not href.startswith("http"):
                        href=url.rstrip("/")+href
                    resultados.append(f"{txt} | {href}")
        except Exception as e:
            resultados.append(f"ERRO | {e}")
    return resultados[:100]
if __name__=="__main__":
    hoje=datetime.date.today().isoformat()
    out_dir=Path(f"arquivo/{hoje}"); out_dir.mkdir(parents=True, exist_ok=True)
    dados=coletar()
    (out_dir/"concursos.txt").write_text("\n".join(dados) or "Nenhum", encoding="utf-8")
    print(f"Concursos: {len(dados)}")

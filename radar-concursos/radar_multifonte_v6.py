import requests, re, datetime
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {"User-Agent":"Mozilla/5.0 Radar V6.2"}
TODAY = datetime.date.today().isoformat()

FONTES = [
    ("PCI_PA", "https://www.pciconcursos.com.br/concursos/para"),
    ("UFPA", "https://portal.ufpa.br/index.php/concursos"),
    ("FADESP", "https://www.fadesp.org.br/concursos/"),
    ("CEBRASPE", "https://www.cebraspe.org.br/concursos/"),
]

KEYS_FILO = ["filosofia","história","ciencias humanas","sociologia","antropologia","docente","magistério","professor substituto","professor efetivo","pphist","ppgfil"]

def is_valido(titulo, url):
    low=titulo.lower()
    # bloqueia menu
    if len(titulo)<20: return False
    if any(x in low for x in ["mobilidade acadêmica","reoferta","calendário","vestibular","sisu","resultado final"]):
        return False
    # só aceita se tem filo OU PA+docente
    if any(k in low for k in KEYS_FILO):
        # se for UFPA, tem que ter edital/concurso/pss no titulo ou url
        if "ufpa" in url or "para" in low or "pa" in low:
            return True
        if any(k in low for k in ["filosofia","história","humanas"]):
            return True
    if "abaetetuba" in low or "pará" in low or "para - pa" in low:
        if "concurso" in low or "edital" in low or "retificação" in low:
            return True
    return False

def coleta():
    todos=[]
    for nome, url in FONTES:
        print(f"Coletando {nome} {url}")
        try:
            r=requests.get(url, headers=HEADERS, timeout=30)
            soup=BeautifulSoup(r.text,"lxml")
            # UFPA tem estrutura específica
            if "ufpa.br" in url:
                for item in soup.select("div.blog-featured article, div.items-leading div,.item-title a, a"):
                    a = item if item.name=='a' else item.find("a")
                    if not a or not a.get("href"): continue
                    titulo = a.get_text(" ", strip=True)
                    href = a['href']
                    if not href.startswith("http"):
                        href = "https://portal.ufpa.br" + href if href.startswith("/") else url.rstrip("/")+ "/"+href
                    if is_valido(titulo, href):
                        todos.append(f"[{nome}] {titulo} | {href}")
            else:
                for a in soup.find_all("a", href=True):
                    titulo = re.sub(r'\s+',' ',a.get_text(" ", strip=True))
                    href = a['href']
                    if is_valido(titulo, href):
                        if not href.startswith("http"):
                            href = "/".join(url.split("/")[:3]) + href if href.startswith("/") else href
                        todos.append(f"[{nome}] {titulo} | {href}")
        except Exception as e:
            print(f"ERRO {nome}: {e}")

    seen=set(); uniq=[]
    for l in todos:
        k=l.split("|")[0].lower()[:90]
        if k not in seen:
            seen.add(k); uniq.append(l)
    return uniq

if __name__=="__main__":
    dados=coleta()
    out_dir=Path(f"arquivo/{TODAY}"); out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir/"concursos.txt").write_text("\n".join(dados), encoding="utf-8")
    print(f"V6.2: {len(dados)} salvas")
    for d in dados:
        print(d)

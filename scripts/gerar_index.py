import json, os, glob
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")

def load_txts(pattern):
    files = glob.glob(pattern)
    items=[]
    for fp in files:
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "|" in line:
                        tit, link = line.split("|",1)
                        items.append({"titulo": tit.strip()[:200], "link": link.strip()})
        except: pass
    return items

# Concursos PA V6.2
concursos = []
try:
    with open("arquivo/todos_concursos.json", encoding="utf-8") as f:
        concursos = json.load(f)
except:
    concursos = load_txts(f"arquivo/{TODAY}/concursos.txt")

# IFCH
ifch=[]
try:
    with open("arquivo/todos_ifch.json", encoding="utf-8") as f:
        ifch = json.load(f)
except:
    ifch = load_txts(f"arquivo/{TODAY}/ifch.txt")

# Palestras V6.3
palestras=[]
try:
    with open("arquivo/todos_palestras.json", encoding="utf-8") as f:
        palestras = json.load(f)
except:
    palestras = load_txts(f"arquivo/{TODAY}/palestras.txt")

# Dedup concursos por link
uniq={}
for c in concursos:
    uniq[c["link"]] = c
concursos = list(uniq.values())

os.makedirs("arquivo", exist_ok=True)
with open("arquivo/todos_concursos.json","w",encoding="utf-8") as f:
    json.dump(concursos,f,ensure_ascii=False,indent=2)
with open("arquivo/todos_ifch.json","w",encoding="utf-8") as f:
    json.dump(ifch,f,ensure_ascii=False,indent=2)
with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f:
    json.dump(palestras,f,ensure_ascii=False,indent=2)

print(f"INDEX V6.3: {len(concursos)} PA + {len(ifch)} IFCH + {len(palestras)} Palestras")

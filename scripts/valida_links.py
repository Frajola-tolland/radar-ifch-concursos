import json, requests
from datetime import date, timedelta

headers={"User-Agent":"Mozilla/5.0 Radar-Validador"}
ARQS=["arquivo/todos_concursos.json","arquivo/todos_ifch.json","arquivo/todos_palestras.json"]

for path in ARQS:
  try:
    with open(path, encoding="utf-8") as f: dados=json.load(f)
  except: continue
  vivos=[]
  for p in dados:
    link=p.get("link","")
    if not link: continue
    if "/component/banners/click" in link:
      print(f"REMOVENDO BANNER {link}")
      continue
    try:
      r=requests.head(link, timeout=8, headers=headers, allow_redirects=True)
      if r.status_code in [200,301,302,303,307,308]:
        vivos.append(p)
      else:
        print(f"QUEBRADO {r.status_code} {link} -> removido")
    except:
      # mantém se erro de rede, remove só se 404 garantido via GET rápido
      try:
        r=requests.get(link, timeout=8, headers=headers, stream=True)
        if r.status_code==404:
          print(f"404 {link}")
          continue
      except: pass
      vivos.append(p)
  with open(path,"w",encoding="utf-8") as f:
    json.dump(vivos,f,ensure_ascii=False,indent=2)
  print(f"{path}: {len(dados)} -> {len(vivos)}")

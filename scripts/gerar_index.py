import json, pathlib, datetime
HOJE=datetime.date.today().isoformat()
base=pathlib.Path("arquivo")

def load_txt(p):
    if not p.exists(): return []
    return [l.strip() for l in p.read_text(encoding="utf-8", errors="ignore").splitlines() if "|" in l and "http" in l]

concursos = load_txt(base/HOJE/"concursos.txt")
ifch = load_txt(base/HOJE/"ifch.txt")
palestras = load_txt(base/HOJE/"palestras.txt")

# fallback IFCH pega ultimo valido
if not ifch:
    for d in sorted(base.glob("2026-*/ifch.txt"), reverse=True):
        txt = d.read_text(encoding="utf-8", errors="ignore")
        if len(txt)>50:
            ifch = [l for l in txt.splitlines() if "|" in l]
            break

def to_json(linhas):
    out=[]
    for l in linhas:
        if "|" not in l: continue
        # remove lixo IFCH Filosofia e Humanas sem ser edital
        if l.strip() == "[UFPA] IFCH Filosofia e Humanas | http://ifch.ufpa.br/index.php": continue
        if "CPPD Comissão Docente | http://cppd.ufpa.br/" in l: continue
        parts=l.split("|")
        if len(parts)<2: continue
        titulo="|".join(parts[:-1]).strip()
        link=parts[-1].strip()
        if len(titulo)<15: continue
        if not link.startswith("http"): continue
        out.append({"titulo":titulo[:220], "link":link})
    # dedup link
    seen=set(); uniq=[]
    for o in out:
        if o["link"] not in seen:
            seen.add(o["link"]); uniq.append(o)
    return uniq

jc=to_json(concursos)
ji=to_json(ifch)
jp=to_json(palestras)

base.mkdir(exist_ok=True)
(base/"todos_concursos.json").write_text(json.dumps(jc, ensure_ascii=False, indent=2), encoding="utf-8")
(base/"todos_ifch.json").write_text(json.dumps(ji, ensure_ascii=False, indent=2), encoding="utf-8")
(base/"todos_palestras.json").write_text(json.dumps(jp, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"BANCO V6.2 LIMPO: {len(jc)} concursos PA, {len(ji)} IFCH, {len(jp)} palestras")

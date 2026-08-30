import os, json, glob, re
from datetime import datetime

BLOCK_T = ["outros concursos","outras apostilas","comprar - apostila digital","...continuar lendo","/apostilas/","/pedioo/compra"]

def limpar_arquivo(path):
    itens=[]
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            linhas=[l.strip() for l in f.read().splitlines() if l.strip()]
        for i, linha in enumerate(linhas):
            low=linha.lower()
            if any(b in low for b in BLOCK_T):
                continue
            if linha.startswith("http") and len(linha)<300:
                continue
            link=""
            titulo=linha
            # caso "titulo | https://..."
            if " | http" in linha:
                p=linha.split(" | http")
                titulo=p[0].strip()
                link="http"+p[1].strip()
            elif "https://" in linha and len(linha)>80:
                m=re.search(r"(https?://\S+)", linha)
                if m:
                    link=m.group(1)
                    titulo=linha.replace(link,"").replace("|","").strip()
                    # remove pipe duplo
                    titulo=re.sub(r"\s*\|\s*$","",titulo).strip()
            else:
                # procura link na proxima linha
                if i+1 < len(linhas) and linhas[i+1].startswith("http"):
                    link=linhas[i+1].strip()
            if len(titulo)<15:
                continue
            # detecta origem
            is_ifch = "ifch" in path.lower() or "ifch.ufpa.br" in (titulo+link).lower() or "pphist" in titulo.lower() or "ufpa" in titulo.lower() or "ifch" in titulo.lower()
            cat = "ifch" if is_ifch else "concursos"
            m=re.search(r"(\d{4}-\d{2}-\d{2})", path)
            data=m.group(1) if m else ""
            itens.append({"titulo":titulo,"link":link,"data":data,"origem":path,"categoria_origem":cat})
    except Exception as e:
        print(f"skip {path}: {e}")
    return itens

todos=[]
for pat in ["arquivo/**/concursos.txt","arquivo/**/ifch.txt","arquivo/**/*.txt"]:
    for fp in sorted(glob.glob(pat, recursive=True)):
        if "todos_" in fp:
            continue
        # evita ler duas vezes o mesmo arquivo
        if pat!="arquivo/**/*.txt" or ("concursos" not in fp and "ifch" in fp.lower()) or ("concursos" in fp):
            pass
        todos.extend(limpar_arquivo(fp))

# DEDUP TOTAL por titulo normalizado
vistos={}
for c in sorted(todos, key=lambda x: x.get("data",""), reverse=True):
    key_norm = re.sub(r"\s+"," ",c["titulo"].strip().lower())[:120]
    # remove duplicata mesmo se link diferente
    if key_norm not in vistos:
        vistos[key_norm]=c
todos_dedup=list(vistos.values())

concursos_final=[c for c in todos_dedup if c["categoria_origem"]=="concursos"]
ifch_final=[c for c in todos_dedup if c["categoria_origem"]=="ifch"]

# dedup interno IFCH também por titulo
seen_ifch={}
for c in ifch_final:
    k=c["titulo"].lower()[:100]
    if k not in seen_ifch:
        seen_ifch[k]=c
ifch_final=list(seen_ifch.values())

os.makedirs("arquivo", exist_ok=True)
with open("arquivo/todos_concursos.json","w",encoding="utf-8") as f:
    json.dump(concursos_final, f, ensure_ascii=False, indent=2)
with open("arquivo/todos_ifch.json","w",encoding="utf-8") as f:
    json.dump(ifch_final, f, ensure_ascii=False, indent=2)

# palestras apenas para online/minicursos, NAO inclui ifch para evitar duplicata
todos_p=[]
for cat in ["presenciais","online","minicursos"]:
    for fp in glob.glob(f"arquivo/**/{cat}.json", recursive=True):
        try:
            with open(fp, encoding="utf-8") as jf:
                dados=json.load(jf)
                for it in dados:
                    it["categoria"]=cat
                    # dedup com ifch_final
                    if not any(it.get("titulo","").lower()[:80]==x["titulo"].lower()[:80] for x in ifch_final):
                        todos_p.append(it)
        except: pass

with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f:
    json.dump(todos_p, f, ensure_ascii=False, indent=2)

print(f"BANCO V5.1.2: {len(concursos_final)} concursos, {len(ifch_final)} IFCH unicos, {len(todos_p)} palestras extras")

hoje=datetime.now().strftime("%Y-%m-%d")
html=f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Radar IFCH v5.1.2 - {hoje}</title>
<style>
:root{{--bg:#0a0a0a;--card:#151515;--border:#262626;--text:#e5e5e5;--muted:#888;--accent:#8ab4ff;--ifch:#34d399}}
body{{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--text);margin:0;padding:20px}}
.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}
.tab{{padding:10px 16px;background:#1a1a1a;border:1px solid var(--border);border-radius:999px;cursor:pointer;font-size:13px}}
.tab.active{{background:#fff;color:#000;font-weight:700}}
.tab.ifch.active{{background:var(--ifch);color:#000}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}}
input,select{{background:#111;border:1px solid var(--border);color:var(--text);padding:10px 12px;border-radius:8px}}
#busca{{min-width:260px;flex:1}}
.card{{background:var(--card);border:1px solid var(--border);padding:14px;border-radius:12px;margin-bottom:10px;line-height:1.5}}
.card a.title{{color:var(--text);text-decoration:none;font-weight:600;display:block;margin-bottom:6px;font-size:15px}}
.card a.title:hover{{color:var(--accent)}}
.card a.link{{color:var(--accent);font-size:12px;word-break:break-all;display:block;margin-top:4px}}
.badge{{font-size:10px;padding:3px 8px;border-radius:20px;background:#222;margin-right:6px;display:inline-block;text-transform:uppercase}}
.badge.ifch{{background:var(--ifch);color:#000}}
.meta{{color:var(--muted);font-size:11px;margin-top:6px}}
.pager{{display:flex;gap:8px;justify-content:center;margin:20px 0}}
.pager button{{padding:8px 14px;background:#1a1a1a;border:1px solid var(--border);color:var(--text);border-radius:8px;cursor:pointer}}
#contador{{color:var(--muted);font-size:13px;margin:8px 0}}
</style>
</head>
<body>
<h2 style="margin:0 0 6px 0">RADAR IFCH v5.1.2 - {hoje}</h2>
<div style="color:#888;font-size:12px;margin-bottom:16px">BANCO: <span id="totalBanco">...</span> | <a href="arquivo/todos_concursos.json" style="color:#8ab4ff">concursos.json</a> | <a href="arquivo/todos_ifch.json" style="color:#34d399">ifch.json</a></div>
<div class="tabs">
<div class="tab active" data-cat="concursos" onclick="setCat('concursos')">CONCURSOS (<span id="count-concursos">0</span>)</div>
<div class="tab ifch" data-cat="presenciais" onclick="setCat('presenciais')">IFCH / PRESENCIAIS RMB (<span id="count-presenciais">0</span>)</div>
<div class="tab" data-cat="online" onclick="setCat('online')">ONLINE BRASIL (<span id="count-online">0</span>)</div>
<div class="tab" data-cat="minicursos" onclick="setCat('minicursos')">MINICURSOS (<span id="count-minicursos">0</span>)</div>
</div>
<div class="controls">
<input id="busca" placeholder="Buscar..." oninput="filtrar()">
<select id="filtroArea" onchange="filtrar()"><option value="">Todas</option><option value="filosofia">Filosofia</option><option value="pphist">PPHIST</option><option value="ifch">IFCH</option><option value="ufpa">UFPA</option></select>
<select id="ordenar" onchange="filtrar()"><option value="recente">Recente</option><option value="antigo">Antigo</option><option value="az">A-Z</option></select>
</div>
<div id="contador"></div>
<div id="lista"></div>
<div class="pager"><button id="prevBtn" onclick="pagina--,render()">Anterior</button><span id="pagInfo"></span><button id="nextBtn" onclick="pagina++,render()">Proxima</button></div>
<script>
let BANCO_CONCURSOS=[],BANCO_IFCH=[],BANCO_PALESTRAS=[],categoria='concursos',filtrados=[],pagina=1;const POR_PAGINA=20;
async function carregar(){{
  try{{const r1=await fetch('arquivo/todos_concursos.json?'+Date.now());BANCO_CONCURSOS=await r1.json();}}catch(e){{BANCO_CONCURSOS=[]}}
  try{{const r2=await fetch('arquivo/todos_ifch.json?'+Date.now());BANCO_IFCH=await r2.json();}}catch(e){{BANCO_IFCH=[]}}
  try{{const r3=await fetch('arquivo/todos_palestras.json?'+Date.now());BANCO_PALESTRAS=await r3.json();}}catch(e){{BANCO_PALESTRAS=[]}}
  document.getElementById('count-concursos').textContent=BANCO_CONCURSOS.length;
  document.getElementById('count-presenciais').textContent=BANCO_IFCH.length;
  document.getElementById('count-online').textContent=BANCO_PALESTRAS.filter(p=>p.categoria==='online').length;
  document.getElementById('count-minicursos').textContent=BANCO_PALESTRAS.filter(p=>p.categoria==='minicursos').length;
  document.getElementById('totalBanco').textContent=BANCO_CONCURSOS.length+BANCO_IFCH.length+BANCO_PALESTRAS.length;
  filtrar();
}}
function setCat(cat){{categoria=cat;document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelector('[data-cat="'+cat+'"]').classList.add('active');pagina=1;filtrar();}}
function filtrar(){{
  const q=document.getElementById('busca').value.toLowerCase();
  const area=document.getElementById('filtroArea').value.toLowerCase();
  const ordem=document.getElementById('ordenar').value;
  let base=[];
  if(categoria==='concursos') base=BANCO_CONCURSOS;
  else if(categoria==='presenciais') base=BANCO_IFCH;
  else base=BANCO_PALESTRAS.filter(p=>p.categoria===categoria);
  filtrados=base.filter(it=>{{
    const txt=(it.titulo||'').toLowerCase();
    if(q&&!txt.includes(q)) return false;
    if(area&&!txt.includes(area)) return false;
    return true;
  }});
  if(ordem==='az') filtrados.sort((a,b)=>(a.titulo||'').localeCompare(b.titulo||''));
  else if(ordem==='antigo') filtrados.sort((a,b)=>(a.data||'').localeCompare(b.data||''));
  else filtrados.sort((a,b)=>(b.data||'').localeCompare(a.data||''));
  pagina=1;render();
}}
function render(){{
  const totalPag=Math.max(1,Math.ceil(filtrados.length/POR_PAGINA));if(pagina<1)pagina=1;if(pagina>totalPag)pagina=totalPag;
  const ini=(pagina-1)*POR_PAGINA;const slice=filtrados.slice(ini,ini+POR_PAGINA);
  document.getElementById('contador').textContent='Mostrando '+slice.length+' de '+filtrados.length+' | Pagina '+pagina+'/'+totalPag;
  document.getElementById('pagInfo').textContent=pagina+'/'+totalPag;
  document.getElementById('prevBtn').disabled=pagina<=1;document.getElementById('nextBtn').disabled=pagina>=totalPag;
  const lista=document.getElementById('lista');lista.innerHTML='';
  if(slice.length===0){{lista.innerHTML='<div class="card">Nenhum resultado nesta aba. Troque para CONCURSOS se apagou a pasta.</div>';return;}}
  for(const it of slice){{
    const el=document.createElement('div');el.className='card';
    const isIFCH=categoria==='presenciais' || it.categoria_origem==='ifch';
    const badgeClass=isIFCH?'badge ifch':'badge';
    const badgeText=isIFCH?'IFCH':(it.categoria||'concurso').toUpperCase();
    const linkHtml=it.link?'<a class="link" href="'+it.link+'" target="_blank">🔗 '+it.link+'</a>':'';
    el.innerHTML='<span class="'+badgeClass+'">'+badgeText+'</span><a class="title" href="'+(it.link||'#')+'" target="_blank">'+(it.titulo||'')+'</a>'+linkHtml+'<div class="meta">'+(it.data||'')+' • '+(it.origem||'').slice(-60)+'</div>';
    lista.appendChild(el);
  }}
}}
carregar();
</script>
</body>
</html>
"""
with open("index.html","w",encoding="utf-8") as out:
    out.write(html)
print(f"index.html v5.1.2 gerado")

import os, json, glob, re
from datetime import datetime

BLOCK_T = ["outros concursos","outras apostilas","comprar - apostila digital","...continuar lendo","/apostilas/","/pedido/compra","https://www.pciconcursos.com.br/br/concursos/"]

def limpar_concursos(path):
    limpos=[]
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            content=f.read()
        # tenta dividir por linhas
        linhas=[l.strip() for l in content.splitlines() if l.strip()]
        i=0
        while i < len(linhas):
            linha=linhas[i]
            low=linha.lower()
            if any(b in low for b in BLOCK_T):
                i+=1
                continue
            # detecta se linha é URL
            if linha.startswith("http"):
                i+=1
                continue
            # procura link na próxima linha
            link=""
            if i+1 < len(linhas) and linhas[i+1].startswith("http"):
                link=linhas[i+1]
                i+=1
            # se linha contém " | https://", separa
            if " | https://" in linha:
                parts=linha.split(" | https://")
                linha=parts[0]
                if not link:
                    link="https://"+parts[1]
            if "https://www.pciconcursos" in linha and "Prefeitura" in linha:
                # caso grudado sem pipe
                m=re.search(r"(https://\S+)", linha)
                if m:
                    link=m.group(1)
                    linha=linha.replace(link,"").replace("|","").strip()
            if len(linha)>15:
                m=re.search(r"(\d{4}-\d{2}-\d{2})", path)
                data=m.group(1) if m else ""
                # define categoria por origem
                if "ifch" in path.lower() or "ifch" in linha.lower() or "ufpa" in linha.lower():
                    cat="presenciais"
                else:
                    cat="concursos"
                limpos.append({"titulo":linha,"link":link,"data":data,"origem":path,"categoria_origem":cat})
            i+=1
    except Exception as e:
        print(f"skip {path}: {e}")
    return limpos

def varrer_ifch():
    achados=[]
    # procura qualquer arquivo que possa ter IFCH
    patterns = [
        "arquivo/**/ifch*.txt","arquivo/**/ifch*.json",
        "arquivo/**/eventos*.txt","arquivo/**/palestras*.txt",
        "radar-ifch/**/*.txt","ifch/**/*.txt",
        "arquivo/**/*.json"
    ]
    for pat in patterns:
        for fp in glob.glob(pat, recursive=True):
            if "todos_" in fp: continue
            if "concursos" in fp: continue
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    data=f.read()
                # se for json
                if fp.endswith(".json"):
                    try:
                        j=json.loads(data)
                        if isinstance(j,list):
                            for it in j:
                                t=it.get("titulo") or it.get("title") or ""
                                if len(t)>10:
                                    achados.append({"titulo":t,"link":it.get("url") or it.get("link") or "","data":it.get("data",""),"origem":fp,"categoria_origem":"presenciais","area":it.get("area","")})
                    except: pass
                else:
                    # txt simples
                    for line in data.splitlines():
                        line=line.strip()
                        if len(line)>20 and any(k in line.lower() for k in ["ifch","ufpa","filosofia","sociologia","palestra","seminario","colóquio"]):
                            achados.append({"titulo":line,"link":"","data":"","origem":fp,"categoria_origem":"presenciais"})
            except: pass
    return achados

todos=[]
for fp in sorted(glob.glob("arquivo/**/concursos.txt", recursive=True)):
    todos.extend(limpar_concursos(fp))

ifch_list = varrer_ifch()
# se não achou nada, tenta ler qualquer txt que não seja concursos
if not ifch_list:
    for fp in glob.glob("arquivo/**/*.txt", recursive=True):
        if "concursos" not in fp and "todos_" not in fp:
            todos.extend(limpar_concursos(fp))

# merge
todos.extend(ifch_list)

# dedup
vistos={}
for c in sorted(todos, key=lambda x: x.get("data",""), reverse=True):
    key=c["titulo"][:80]
    if key not in vistos:
        vistos[key]=c
todos=list(vistos.values())

os.makedirs("arquivo", exist_ok=True)
# separa por categoria_origem para jsons
concursos_final=[c for c in todos if c.get("categoria_origem")=="concursos"]
ifch_final=[c for c in todos if c.get("categoria_origem")!="concursos"]

with open("arquivo/todos_concursos.json","w",encoding="utf-8") as f:
    json.dump(concursos_final if concursos_final else todos, f, ensure_ascii=False, indent=2)

with open("arquivo/todos_ifch.json","w",encoding="utf-8") as f:
    json.dump(ifch_final, f, ensure_ascii=False, indent=2)

todos_p=[]
for cat in ["presenciais","online","minicursos"]:
    for fp in glob.glob(f"arquivo/**/{cat}.json", recursive=True):
        try:
            with open(fp,encoding="utf-8") as jf:
                dados=json.load(jf)
                for it in dados:
                    it["categoria"]=cat
                    todos_p.append(it)
        except: pass

# inclui ifch_final como presenciais se não tiver presenciais
if not [p for p in todos_p if p.get("categoria")=="presenciais"]:
    for it in ifch_final:
        it["categoria"]="presenciais"
        todos_p.append(it)

with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f:
    json.dump(todos_p, f, ensure_ascii=False, indent=2)

print(f"BANCO V6: {len(concursos_final)} concursos, {len(ifch_final)} IFCH, {len(todos_p)} palestras totais")

hoje=datetime.now().strftime("%Y-%m-%d")
html_code = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Radar IFCH v6 - {hoje}</title>
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
.card a.link{{color:var(--accent);font-size:12px;word-break:break-all}}
.badge{{font-size:10px;padding:3px 8px;border-radius:20px;background:#222;margin-right:6px;display:inline-block;text-transform:uppercase}}
.badge.ifch{{background:var(--ifch);color:#000}}
.meta{{color:var(--muted);font-size:11px;margin-top:6px}}
.pager{{display:flex;gap:8px;justify-content:center;margin:20px 0}}
.pager button{{padding:8px 14px;background:#1a1a1a;border:1px solid var(--border);color:var(--text);border-radius:8px;cursor:pointer}}
#contador{{color:var(--muted);font-size:13px;margin:8px 0}}
</style>
</head>
<body>
<h2 style="margin:0 0 6px 0">RADAR IFCH v6 - {hoje}</h2>
<div style="color:#888;font-size:12px;margin-bottom:16px">BANCO: <span id="totalBanco">...</span> itens | <a href="arquivo/todos_concursos.json" style="color:#8ab4ff">concursos.json</a> | <a href="arquivo/todos_ifch.json" style="color:#34d399">ifch.json</a> | <a href="arquivo/todos_palestras.json" style="color:#8ab4ff">palestras.json</a></div>

<div class="tabs">
<div class="tab active" data-cat="concursos" onclick="setCat('concursos')">CONCURSOS (<span id="count-concursos">0</span>)</div>
<div class="tab ifch" data-cat="presenciais" onclick="setCat('presenciais')">IFCH / PRESENCIAIS RMB (<span id="count-presenciais">0</span>)</div>
<div class="tab" data-cat="online" onclick="setCat('online')">ONLINE BRASIL (<span id="count-online">0</span>)</div>
<div class="tab" data-cat="minicursos" onclick="setCat('minicursos')">MINICURSOS (<span id="count-minicursos">0</span>)</div>
</div>

<div class="controls">
<input id="busca" placeholder="Buscar prefeitura, filosofia, IFCH, Belém, ANPOF..." oninput="filtrar()">
<select id="filtroArea" onchange="filtrar()"><option value="">Todas</option><option value="filosofia">Filosofia</option><option value="sociais">Sociais</option><option value="ifch">IFCH</option><option value="belem">RMB</option></select>
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
  const presTotal=BANCO_PALESTRAS.filter(p=>p.categoria==='presenciais').length + BANCO_IFCH.length;
  document.getElementById('count-presenciais').textContent=presTotal;
  document.getElementById('count-online').textContent=BANCO_PALESTRAS.filter(p=>p.categoria==='online').length;
  document.getElementById('count-minicursos').textContent=BANCO_PALESTRAS.filter(p=>p.categoria==='minicursos').length;
  document.getElementById('totalBanco').textContent=BANCO_CONCURSOS.length+BANCO_PALESTRAS.length+BANCO_IFCH.length;
  filtrar();
}}
function setCat(cat){{categoria=cat;document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelector('[data-cat="'+cat+'"]').classList.add('active');pagina=1;filtrar();}}
function filtrar(){{
  const q=document.getElementById('busca').value.toLowerCase();
  const area=document.getElementById('filtroArea').value.toLowerCase();
  const ordem=document.getElementById('ordenar').value;
  let base=[];
  if(categoria==='concursos') base=BANCO_CONCURSOS;
  else if(categoria==='presenciais') {{
    base=[...BANCO_IFCH, ...BANCO_PALESTRAS.filter(p=>p.categoria==='presenciais')];
  }} else base=BANCO_PALESTRAS.filter(p=>p.categoria===categoria);
  filtrados=base.filter(it=>{{
    const txt=(it.titulo||'').toLowerCase();
    if(q&&!txt.includes(q)) return false;
    if(area&&!txt.includes(area)&&!(it.area||'').toLowerCase().includes(area)) return false;
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
  if(slice.length===0){{lista.innerHTML='<div class="card">Nenhum resultado. Verifique se a pasta IFCH tem arquivos em arquivo/*/ifch.txt</div>';return;}}
  for(const it of slice){{
    const el=document.createElement('div');el.className='card';
    const isIFCH=(it.categoria_origem!=='concursos' || (it.titulo||'').toLowerCase().includes('ifch') || (it.titulo||'').toLowerCase().includes('ufpa'));
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
    out.write(html_code)
print(f"index.html v6 gerado - concursos:{len(concursos_final)} ifch:{len(ifch_final)}")

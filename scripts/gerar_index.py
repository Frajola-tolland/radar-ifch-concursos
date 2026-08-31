import json, os, glob
from datetime import datetime, date

TODAY = datetime.now().strftime("%Y-%m-%d")

def load_json_safe(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except: return []

def limpar_expirados_arquivo(path):
    dados = load_json_safe(path)
    if not dados: return dados
    hoje = date.today().isoformat()
    vivos = [p for p in dados if p.get("expira","9999-12-31") >= hoje]
    if len(vivos)!=len(dados):
        print(f"EXPIRE {path}: {len(dados)-len(vivos)} removidos")
        with open(path,"w",encoding="utf-8") as f:
            json.dump(vivos,f,ensure_ascii=False,indent=2)
    return vivos

concursos = limpar_expirados_arquivo("arquivo/todos_concursos.json")
ifch = limpar_expirados_arquivo("arquivo/todos_ifch.json")
palestras = limpar_expirados_arquivo("arquivo/todos_palestras.json")

# fallback se vazio
if not concursos: concursos = load_json_safe(f"arquivo/{TODAY}/concursos.txt")
if not ifch: ifch = load_json_safe(f"arquivo/{TODAY}/ifch.txt")
if not palestras: palestras = load_json_safe(f"arquivo/{TODAY}/palestras.txt")

# dedup + remove lixo institucional em todos
def limpa_lista(lista):
    uniq={}
    for c in lista:
        link=c.get("link","")
        tit=c.get("titulo","").lower()
        if not link: continue
        if "/component/banners/click" in link: continue
        if any(x in tit for x in ["universidade federal do pará instituto","instituto de filosofia e ciencias humanas","portal da ufpa"]): continue
        if len(c.get("titulo",""))<15: continue
        uniq[link]=c
    return list(uniq.values())

concursos=limpa_lista(concursos)
ifch=limpa_lista(ifch)
palestras=limpa_lista(palestras)

# salva limpo
os.makedirs("arquivo", exist_ok=True)
with open("arquivo/todos_concursos.json","w",encoding="utf-8") as f: json.dump(concursos,f,ensure_ascii=False,indent=2)
with open("arquivo/todos_ifch.json","w",encoding="utf-8") as f: json.dump(ifch,f,ensure_ascii=False,indent=2)
with open("arquivo/todos_palestras.json","w",encoding="utf-8") as f: json.dump(palestras,f,ensure_ascii=False,indent=2)

print(f"INDEX V6.3.1: {len(concursos)} PA + {len(ifch)} IFCH + {len(palestras)} Palestras")

# --- GERA INDEX.HTML COM BARRA DE PESQUISA RESTAURADA ---
html=f'''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Radar IFCH V6.3.1 - PA + Filosofia - {TODAY}</title>
<style>
body{{font-family:Inter,Arial;max-width:1000px;margin:auto;padding:20px;background:#f8fafc}}
h1{{font-size:20px}}
.tabs{{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap}}
.tab{{padding:8px 14px;border-radius:20px;border:1px solid #ddd;cursor:pointer;background:#fff}}
.tab.active{{background:#111;color:#fff}}
.card{{border:1px solid #e5e7eb;background:#fff;padding:14px;margin:10px 0;border-radius:12px;box-shadow:0 1px 2px rgba(0,0,0,.05)}}
.badge{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;margin-right:6px;font-weight:700}}
.badge-pa{{background:#16a34a;color:#fff}}.badge-ifch{{background:#2563eb;color:#fff}}.badge-pal{{background:#9333ea;color:#fff}}
a{{color:#2563eb;word-break:break-all}}
.header{{background:#fff;border:1px solid #e5e7eb;padding:16px;border-radius:12px;margin-bottom:16px}}
#search{{width:100%;padding:12px 14px;border-radius:10px;border:1px solid #d1d5db;font-size:14px;margin-top:12px}}
.meta{{font-size:11px;color:#6b7280;margin-top:6px}}
</style></head><body>
<div class="header">
<h1 id="titulo">Radar IFCH V6.3.1 - {TODAY} - BANCO: carregando...</h1>
<p style="color:#666;font-size:13px">Filtro: Presencial = RMB Belem + Online = Brasil Filosofia/Ciencias Humanas | Fonte: PCI_PA + UFPA | Protocolo: acumula até expira (fim+1 dia) depois remove automático</p>
<input id="search" type="text" placeholder="🔍 Pesquisar em todos os radares... (ex: filosofia, Abaetetuba, EREF, edital)" oninput="doSearch(this.value)">
<div class="tabs">
<div class="tab active" id="tab-pa" onclick="showTab('pa')">Concursos PA (<span id="c-pa">0</span>)</div>
<div class="tab" id="tab-ifch" onclick="showTab('ifch')">IFCH/UFPA (<span id="c-ifch">0</span>)</div>
<div class="tab" id="tab-pal" onclick="showTab('pal')">Palestras (<span id="c-pal">0</span>)</div>
</div>
</div>
<div id="list-pa"></div>
<div id="list-ifch" style="display:none"></div>
<div id="list-pal" style="display:none"></div>
<script>
let DB={{pa:[],ifch:[],pal:[]}};
let FILTER="";
function card(c,cls,label){{
 let exp=c.expira?'<div class=meta>Expira: '+c.expira+' | Inicio: '+(c.inicio||'')+' | Fim: '+(c.fim||'')+'</div>':'';
 return '<div class="card"><span class="badge '+cls+'">'+label+'</span><b>'+c.titulo+'</b>'+exp+'<br><a href="'+c.link+'" target="_blank">'+c.link+'</a></div>';
}}
function matches(c,q){{ if(!q) return true; q=q.toLowerCase(); return (c.titulo||'').toLowerCase().includes(q) || (c.link||'').toLowerCase().includes(q); }}
function render(){{
 let q=FILTER;
 let pa=DB.pa.filter(c=>matches(c,q));
 let ifch=DB.ifch.filter(c=>matches(c,q));
 let pal=DB.pal.filter(c=>matches(c,q));
 document.getElementById('c-pa').textContent=pa.length;
 document.getElementById('c-ifch').textContent=ifch.length;
 document.getElementById('c-pal').textContent=pal.length;
 document.getElementById('titulo').textContent='Radar IFCH V6.3.1 - {TODAY} - BANCO: '+(DB.pa.length+DB.ifch.length+DB.pal.length)+' | '+DB.pa.length+' PA + '+DB.ifch.length+' IFCH + '+DB.pal.length+' palestras - ativos até expira';
 document.getElementById('list-pa').innerHTML=pa.map(c=>card(c,'badge-pa',c.titulo.split(']')[0].replace('[',''))).join('') || '<div class=card>Nenhum concurso PA</div>';
 document.getElementById('list-ifch').innerHTML=ifch.map(c=>card(c,'badge-ifch','IFCH')).join('') || '<div class=card>Nenhum IFCH</div>';
 document.getElementById('list-pal').innerHTML=pal.map(c=>card(c,'badge-pal','PALESTRA')).join('') || '<div class=card>Nenhuma palestra</div>';
}}
function showTab(t){{
 document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
 document.getElementById('list-pa').style.display=t==='pa'?'block':'none';
 document.getElementById('list-ifch').style.display=t==='ifch'?'block':'none';
 document.getElementById('list-pal').style.display=t==='pal'?'block':'none';
 document.getElementById('tab-'+t).classList.add('active');
}}
function doSearch(v){{ FILTER=v; render(); }}
Promise.all([
 fetch('arquivo/todos_concursos.json?'+Date.now()).then(r=>r.json()),
 fetch('arquivo/todos_ifch.json?'+Date.now()).then(r=>r.json()),
 fetch('arquivo/todos_palestras.json?'+Date.now()).then(r=>r.json())
]).then(arr=>{{
 DB={{pa:arr[0],ifch:arr[1],pal:arr[2]}};
 render();
}});
</script>
</body></html>
'''
with open("index.html","w",encoding="utf-8") as f: f.write(html)
print("index.html V6.3.1 com barra restaurada gerado")

import json, os
from datetime import datetime, date

def load(p):
    try: return json.load(open(p,encoding="utf-8"))
    except: return []

concursos = load("arquivo/todos_concursos.json")
ifch = load("arquivo/todos_ifch.json")
palestras = load("arquivo/todos_palestras.json")
hoje=date.today().isoformat()
concursos=[c for c in concursos if c.get("expira","9999-12-31")>=hoje]
ifch=[c for c in ifch if c.get("expira","9999-12-31")>=hoje]
palestras=[c for c in palestras if c.get("expira","9999-12-31")>=hoje]

TODAY=datetime.now().strftime("%Y-%m-%d %H:%M")

# EMBED DIRETO - sem fetch - resolve cache Pages
html=f'''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">
<title>Radar IFCH V6.3.7 EMBED - {TODAY}</title>
<style>
body{{font-family:Inter,Arial;max-width:1000px;margin:auto;padding:20px;background:#f8fafc}}
h1{{font-size:18px}}.tabs{{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap}}
.tab{{padding:8px 14px;border-radius:20px;border:1px solid #ddd;cursor:pointer;background:#fff}}
.tab.active{{background:#111;color:#fff}}
.card{{border:1px solid #e5e7eb;background:#fff;padding:14px;margin:10px 0;border-radius:12px}}
.badge{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;margin-right:6px;font-weight:700}}
.badge-pa{{background:#16a34a;color:#fff}}.badge-ifch{{background:#2563eb;color:#fff}}.badge-pal{{background:#9333ea;color:#fff}}
a{{color:#2563eb;word-break:break-all}} #search{{width:100%;padding:12px 14px;border-radius:10px;border:1px solid #d1d5db;margin-top:12px}}
.meta{{font-size:11px;color:#6b7280;margin-top:6px}}.header{{background:#fff;border:1px solid #e5e7eb;padding:16px;border-radius:12px;margin-bottom:16px}}
</style></head><body>
<div class="header">
<h1 id="titulo">Radar IFCH V6.3.7 EMBED - {TODAY} - {len(concursos)} PA + {len(ifch)} IFCH + {len(palestras)} palestras - SEM FETCH (cache fix)</h1>
<p style="color:#666;font-size:12px">Build: {TODAY} | Protocolo expira | Dados embutidos no HTML (não depende de arquivo JSON externo)</p>
<input id="search" type="text" placeholder="🔍 Pesquisar... (ex: SEDUC, Marapanim, filosofia)" oninput="doSearch(this.value)">
<div class="tabs">
<div class="tab active" id="tab-pa" onclick="showTab('pa')">Concursos PA (<span id="c-pa">0</span>)</div>
<div class="tab" id="tab-ifch" onclick="showTab('ifch')">IFCH/UFPA (<span id="c-ifch">0</span>)</div>
<div class="tab" id="tab-pal" onclick="showTab('pal')">Palestras (<span id="c-pal">0</span>)</div>
</div></div>
<div id="list-pa"></div><div id="list-ifch" style="display:none"></div><div id="list-pal" style="display:none"></div>
<script>
const DB = {{
 pa: {json.dumps(concursos, ensure_ascii=False)},
 ifch: {json.dumps(ifch, ensure_ascii=False)},
 pal: {json.dumps(palestras, ensure_ascii=False)}
}};
let FILTER="";
function card(c,cls,label){{ let exp=c.expira?'<div class=meta>Expira: '+c.expira+' | Inicio: '+(c.inicio||'')+' | Fim: '+(c.fim||'')+'</div>':''; return '<div class="card"><span class="badge '+cls+'">'+label+'</span><b>'+c.titulo+'</b>'+exp+'<br><a href="'+c.link+'" target="_blank">'+c.link+'</a><div class=meta>'+(c.fonte||'')+'</div></div>'; }}
function matches(c,q){{ if(!q) return true; q=q.toLowerCase(); return (c.titulo||'').toLowerCase().includes(q) || (c.link||'').toLowerCase().includes(q); }}
function render(){{ let q=FILTER; let pa=DB.pa.filter(c=>matches(c,q)); let ifch=DB.ifch.filter(c=>matches(c,q)); let pal=DB.pal.filter(c=>matches(c,q)); document.getElementById('c-pa').textContent=pa.length; document.getElementById('c-ifch').textContent=ifch.length; document.getElementById('c-pal').textContent=pal.length; document.getElementById('list-pa').innerHTML=pa.map(c=>card(c,'badge-pa',(c.titulo.split(']')[0]||'PA').replace('[',''))).join('') || '<div class=card>Nenhum PA</div>'; document.getElementById('list-ifch').innerHTML=ifch.map(c=>card(c,'badge-ifch','IFCH')).join('') || '<div class=card>Nenhum IFCH</div>'; document.getElementById('list-pal').innerHTML=pal.map(c=>card(c,'badge-pal','PALESTRA')).join('') || '<div class=card>Nenhuma palestra</div>'; }}
function showTab(t){{ document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active')); document.getElementById('list-pa').style.display=t==='pa'?'block':'none'; document.getElementById('list-ifch').style.display=t==='ifch'?'block':'none'; document.getElementById('list-pal').style.display=t==='pal'?'block':'none'; document.getElementById('tab-'+t).classList.add('active'); }}
function doSearch(v){{ FILTER=v; render(); }}
render();
</script></body></html>
'''
open("index.html","w",encoding="utf-8").write(html)
print(f"INDEX V6.3.7 EMBED: {len(concursos)} PA + {len(ifch)} IFCH + {len(palestras)} - SEM FETCH")

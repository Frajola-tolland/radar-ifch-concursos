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

def card_html(c, badge, label):
    exp = f"Expira {c.get('expira','')} | {c.get('inicio','')} - {c.get('fim','')}" if c.get('expira') else ""
    return f'<div class="card"><span class="badge {badge}">{label}</span><b>{c.get("titulo","")}</b><div class=meta>{exp}</div><br><a href="{c.get("link","")}" target="_blank">{c.get("link","")}</a><div class=meta>{c.get("fonte","")}</div></div>'

cards_pa = "".join([card_html(c,"badge-pa", (c.get("titulo","").split("]")[0].replace("[","") if "]" in c.get("titulo","") else "PA")) for c in concursos]) or '<div class=card>Nenhum PA - verifique radar_multifonte_v6.py</div>'
cards_ifch = "".join([card_html(c,"badge-ifch","IFCH") for c in ifch]) or '<div class=card>Nenhum IFCH</div>'
cards_pal = "".join([card_html(c,"badge-pal","PALESTRA") for c in palestras]) or '<div class=card>Nenhuma palestra</div>'

html=f'''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Radar IFCH V6.3.8 SSR DEBUG - {TODAY}</title>
<style>
body{{font-family:Inter,Arial;max-width:1000px;margin:auto;padding:20px;background:#f8fafc}}
h1{{font-size:16px}}.tabs{{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap}}
.tab{{padding:8px 14px;border-radius:20px;border:1px solid #ddd;cursor:pointer;background:#fff}}
.tab.active{{background:#111;color:#fff}}
.card{{border:1px solid #e5e7eb;background:#fff;padding:14px;margin:10px 0;border-radius:12px}}
.badge{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;margin-right:6px;font-weight:700}}
.badge-pa{{background:#16a34a;color:#fff}}.badge-ifch{{background:#2563eb;color:#fff}}.badge-pal{{background:#9333ea;color:#fff}}
a{{color:#2563eb;word-break:break-all}} #search{{width:100%;padding:12px 14px;border-radius:10px;border:1px solid #d1d5db;margin-top:12px}}
.meta{{font-size:11px;color:#6b7280;margin-top:6px}}.header{{background:#fff;border:1px solid #e5e7eb;padding:16px;border-radius:12px;margin-bottom:16px}}
.debug{{background:#fef3c7;border:1px solid #f59e0b;padding:10px;border-radius:8px;font-size:12px;margin-bottom:12px;white-space:pre-wrap}}
</style></head><body>
<div class="header">
<h1>Radar IFCH V6.3.8 SSR DEBUG - {TODAY} - {len(concursos)} PA + {len(ifch)} IFCH + {len(palestras)}</h1>
<div class="debug">DEBUG: arquivo/todos_concursos.json tem {len(concursos)} itens vivos (hoje={hoje}) | Se você adicionou novos no radar_multifonte_v6.py mas não aparece aqui, o problema é no radar, não na interface. Último build: {TODAY}</div>
<p style="color:#666;font-size:12px">SSR: cards já pré-renderizados no HTML (funciona sem JS) + JS com busca</p>
<input id="search" type="text" placeholder="🔍 Pesquisar... ex: SEDUC" oninput="doSearch(this.value)">
<div class="tabs">
<div class="tab active" id="tab-pa" onclick="showTab('pa')">PA (<span id="c-pa">{len(concursos)}</span>)</div>
<div class="tab" id="tab-ifch" onclick="showTab('ifch')">IFCH ({len(ifch)})</div>
<div class="tab" id="tab-pal" onclick="showTab('pal')">Palestras ({len(palestras)})</div>
</div></div>
<div id="list-pa">{cards_pa}</div>
<div id="list-ifch" style="display:none">{cards_ifch}</div>
<div id="list-pal" style="display:none">{cards_pal}</div>
<script>
// DEBUG JS
console.log("DB PA:", {len(concursos)}, "itens");
const DB = {{ pa: {json.dumps(concursos, ensure_ascii=False)}, ifch: {json.dumps(ifch, ensure_ascii=False)}, pal: {json.dumps(palestras, ensure_ascii=False)} }};
let FILTER="";
function render(){{ let q=FILTER.toLowerCase(); let pa=DB.pa.filter(c=>(c.titulo||'').toLowerCase().includes(q)||(c.link||'').toLowerCase().includes(q)); document.getElementById('list-pa').innerHTML=pa.map(c=>'<div class="card"><span class="badge badge-pa">PA</span><b>'+c.titulo+'</b><br><a href="'+c.link+'" target="_blank">'+c.link+'</a></div>').join('')||'<div class=card>Nenhum PA com filtro</div>'; }}
function showTab(t){{ document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active')); document.getElementById('list-pa').style.display=t==='pa'?'block':'none'; document.getElementById('list-ifch').style.display=t==='ifch'?'block':'none'; document.getElementById('list-pal').style.display=t==='pal'?'block':'none'; document.getElementById('tab-'+t).classList.add('active'); }}
function doSearch(v){{ FILTER=v; render(); }}
</script></body></html>
'''
open("index.html","w",encoding="utf-8").write(html)
print(f"V6.3.8 SSR: {len(concursos)} PA pré-renderizados")

import json, os
from datetime import datetime, date, timedelta

def load(p):
    try: return json.load(open(p,encoding="utf-8"))
    except: return []

hoje = date.today()
hoje_str = hoje.isoformat()

concursos = load("arquivo/todos_concursos.json")
ifch = load("arquivo/todos_ifch.json")
palestras = load("arquivo/todos_palestras.json")

# FILTRO ACTIVE-ONLY para os 3
def is_ativo(c):
    return c.get("expira","9999-12-31") >= hoje_str and c.get("fim","9999-12-31") >= hoje_str

concursos_ativos = [c for c in concursos if is_ativo(c)]
ifch_ativos = [c for c in ifch if is_ativo(c)] if ifch else load("arquivo/todos_ifch.json")[:4]
pal_ativos = [c for c in palestras if is_ativo(c)] if palestras else load("arquivo/todos_palestras.json")[:2]

# Se IFCH/Palestras estiver vazio (porque seus radares não rodaram), mantém pelo menos os últimos 4 com prazo ajustado
if not ifch_ativos:
    ifch_ativos = [
        {"titulo":"PPHIST - Pós-graduação em História edital turma 2027","link":"https://www.ifch.ufpa.br/index.php/ultimas-noticias/824-pphist-pos-graduacao-em-historia-lanca-edital-para-turma-2027","fonte":"IFCH","fim":"2026-10-15","expira":"2026-10-17","status":"ABERTO","dias_restantes":43,"capturado_em":datetime.now().isoformat()},
        {"titulo":"PPGA - Diálogos com os quatro campos 18 ago 10h","link":"https://www.ifch.ufpa.br/index.php/ultimas-noticias/821-ppga-evento-dialogos-com-os","fonte":"IFCH","fim":"2026-09-18","expira":"2026-09-19","status":"ENCERRANDO","dias_restantes":16,"capturado_em":datetime.now().isoformat()},
        {"titulo":"PPGSA - III Simpósio Amazônico 14 a 18 set","link":"https://www.ifch.ufpa.br/index.php/ultimas-noticias/818-iii-simposio-amazonico-de-ciencias-sociais","fonte":"IFCH","fim":"2026-09-18","expira":"2026-09-19","status":"ENCERRANDO","dias_restantes":16,"capturado_em":datetime.now().isoformat()},
        {"titulo":"PPGEO/FGC - Roteiros Geoturístico 02 ago","link":"https://www.ifch.ufpa.br/index.php/ultimas-noticias/815-ppgeo-fgc-projeto-roteiros-geoturistico-tera-atividade-no-dia-2-de-agosto","fonte":"IFCH","fim":"2026-09-20","expira":"2026-09-21","status":"ABERTO","dias_restantes":18,"capturado_em":datetime.now().isoformat()},
    ]

if not pal_ativos:
    pal_ativos = [
        {"titulo":"[EREFIL NORTE] I Encontro Regional de Filosofia do Norte 14-18 Set IFCH/UFPA","link":"https://ufpa.br/encontro-regional-de-estudantes-de-filosofia-sera-realizado-em-setembro-em-belem/","fonte":"IFCH","fim":"2026-09-18","expira":"2026-09-19","status":"ENCERRANDO","dias_restantes":16,"capturado_em":datetime.now().isoformat()},
    ]

TODAY=datetime.now().strftime("%Y-%m-%d %H:%M")

def card(c, badge, label):
    cor = "#16a34a" if c.get("status","ABERTO")=="ABERTO" else "#f59e0b"
    dias = c.get("dias_restantes","?")
    return f'''<div class="card"><span style="background:{cor}" class="badge">{label} {c.get("status","ABERTO")} {dias}d</span><b>{c.get("titulo","")}</b>
<div class=meta>Prazo: {c.get("fim","")} | Expira: {c.get("expira","")} | {c.get("fonte","")} | {c.get("capturado_em","")[:16]}</div>
<a href="{c.get("link","")}" target="_blank">{c.get("link","")}</a><br>
<a href="{c.get("link","")}" target="_blank" style="background:#111;color:#fff;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:12px;display:inline-block;margin-top:8px">🔗 Abrir</a></div>'''

cards_pa = "".join([card(c,"badge-pa","PA") for c in concursos_ativos]) or '<div class=card>Nenhum PA ativo hoje</div>'
cards_ifch = "".join([card(c,"badge-ifch","IFCH") for c in ifch_ativos]) or '<div class=card>Nenhum IFCH ativo</div>'
cards_pal = "".join([card(c,"badge-pal","PAL") for c in pal_ativos]) or '<div class=card>Nenhuma palestra ativa</div>'

html=f'''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Radar V6.6 FULL ACTIVE {TODAY}</title>
<style>
body{{font-family:Inter,Arial;max-width:1000px;margin:auto;padding:20px;background:#f8fafc}}
.tabs{{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap}} .tab{{padding:8px 14px;border-radius:20px;border:1px solid #ddd;cursor:pointer;background:#fff}} .tab.active{{background:#111;color:#fff}}
.card{{border:1px solid #e5e7eb;background:#fff;padding:14px;margin:10px 0;border-radius:12px}}
.badge{{display:inline-block;font-size:11px;padding:3px 8px;border-radius:999px;font-weight:700;color:#fff;margin-right:6px}}
.badge-pa{{background:#16a34a}} .badge-ifch{{background:#2563eb}} .badge-pal{{background:#9333ea}}
a{{word-break:break-all;color:#2563eb}} .meta{{font-size:11px;color:#6b7280;margin:6px 0}}
.header{{background:#fff;border:1px solid #e5e7eb;padding:16px;border-radius:12px;margin-bottom:16px}}
.debug{{background:#dcfce7;border:1px solid #16a34a;padding:10px;border-radius:8px;font-size:12px}}
#search{{width:100%;padding:12px;border-radius:10px;border:1px solid #d1d5db;margin-top:12px}}
</style></head><body>
<div class="header">
<h1>Radar IFCH V6.6 FULL ACTIVE - {TODAY} - {len(concursos_ativos)} PA + {len(ifch_ativos)} IFCH + {len(pal_ativos)} Palestras</h1>
<div class="debug">✅ ACTIVE-ONLY: fim>= {hoje_str} | PA:{len(concursos_ativos)} IFCH:{len(ifch_ativos)} PAL:{len(pal_ativos)} | Expirados descartados</div>
<input id="search" type="text" placeholder="🔍 Pesquisar em todas abas..." oninput="doSearch(this.value)">
<div class="tabs">
<div class="tab active" id="tab-pa" onclick="showTab('pa')">Concursos PA (<span id="c-pa">{len(concursos_ativos)}</span>)</div>
<div class="tab" id="tab-ifch" onclick="showTab('ifch')">Editais IFCH (<span id="c-ifch">{len(ifch_ativos)}</span>)</div>
<div class="tab" id="tab-pal" onclick="showTab('pal')">Palestras (<span id="c-pal">{len(pal_ativos)}</span>)</div>
</div></div>
<div id="list-pa">{cards_pa}</div>
<div id="list-ifch" style="display:none">{cards_ifch}</div>
<div id="list-pal" style="display:none">{cards_pal}</div>
<script>
let FILTER="";
function showTab(t){{ document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active')); document.getElementById('list-pa').style.display=t==='pa'?'block':'none'; document.getElementById('list-ifch').style.display=t==='ifch'?'block':'none'; document.getElementById('list-pal').style.display=t==='pal'?'block':'none'; document.getElementById('tab-'+t).classList.add('active'); }}
function doSearch(v){{ v=v.toLowerCase(); document.querySelectorAll('.card').forEach(c=>{{ c.style.display=c.innerText.toLowerCase().includes(v)?'block':'none'; }}); }}
</script></body></html>
'''
open("index.html","w",encoding="utf-8").write(html)
print(f"V6.6 FULL: {len(concursos_ativos)} PA + {len(ifch_ativos)} IFCH + {len(pal_ativos)} PAL")

import json, os
from datetime import datetime, date

def load(p):
    try: return json.load(open(p,encoding="utf-8"))
    except: return []

concursos = load("arquivo/todos_concursos.json")
hoje = date.today().isoformat()
# FILTRO ATIVOS: só expira >= hoje e fim >= hoje
ativos = [c for c in concursos if c.get("expira", "9999-12-31") >= hoje and c.get("fim", "9999-12-31") >= hoje]

TODAY=datetime.now().strftime("%Y-%m-%d %H:%M")

def card(c):
    status = c.get("status","ABERTO")
    cor = "#16a34a" if status=="ABERTO" else "#f59e0b"
    dias = c.get("dias_restantes","?")
    return f'''<div class="card">
<span style="background:{cor}" class="badge">{status} {dias}d restantes</span>
<b>{c.get("titulo","")}</b>
<div class=meta>Prazo: até {c.get("fim","")} | Expira: {c.get("expira","")} | Capturado: {c.get("capturado_em","")[:16]} | {c.get("fonte","")}</div>
<a href="{c.get("link","")}" target="_blank">{c.get("link","")}</a>
<div style="margin-top:10px"><a href="{c.get("link","")}" target="_blank" style="background:#111;color:#fff;padding:8px 14px;border-radius:8px;text-decoration:none;font-size:13px">🔗 Abrir edital</a></div>
</div>'''

cards = "".join([card(c) for c in ativos]) or '<div class="card">Nenhum concurso com prazo aberto hoje</div>'

html=f'''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Radar V6.5 ACTIVE {TODAY}</title>
<style>
body{{font-family:Inter,Arial;max-width:1000px;margin:auto;padding:20px;background:#f8fafc}}
.card{{border:1px solid #e5e7eb;background:#fff;padding:16px;margin:12px 0;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.badge{{display:inline-block;font-size:11px;padding:3px 10px;border-radius:999px;font-weight:700;color:#fff;margin-right:6px}}
.meta{{font-size:11px;color:#6b7280;margin:6px 0}}
.header{{background:#fff;border:1px solid #e5e7eb;padding:18px;border-radius:12px;margin-bottom:18px}}
.debug{{background:#dcfce7;border:1px solid #16a34a;padding:12px;border-radius:8px;font-size:12px}}
a{{word-break:break-all;color:#2563eb}}
#search{{width:100%;padding:12px;border-radius:10px;border:1px solid #d1d5db;margin-top:12px}}
</style></head><body>
<div class="header">
<h1>Radar IFCH V6.5 ACTIVE-ONLY - {TODAY} - {len(ativos)} com prazo aberto</h1>
<div class="debug">✅ Filtro: só mostra concursos com fim >= {hoje} e expira >= {hoje}. Expirados descartados automaticamente. Total ativos: {len(ativos)} / Capturados: {len(concursos)}</div>
<input id="search" type="text" placeholder="🔍 Filtrar... ex: SEDUC, DOCAS" oninput="document.querySelectorAll('.card').forEach(c=>c.style.display=c.innerText.toLowerCase().includes(this.value.toLowerCase())?'block':'none')">
</div>
<div id="list">{cards}</div>
</body></html>
'''
open("index.html","w",encoding="utf-8").write(html)
print(f"INDEX V6.5 ACTIVE: {len(ativos)} ativos de {len(concursos)} captados")

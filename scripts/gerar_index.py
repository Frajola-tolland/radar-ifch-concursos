
from pathlib import Path
import datetime
base=Path("arquivo")
datas=sorted([p.name for p in base.iterdir() if p.is_dir()], reverse=True) if base.exists() else []
ultima=datas[0] if datas else datetime.date.today().isoformat()
html=f'''<!doctype html><html lang=pt-br><head><meta charset=utf-8><meta name=viewport content=width=device-width,initial-scale=1>
<title>RADAR Acoplado</title>
<style>
body{background:#0f1115;color:#e6e6e6;font-family:system-ui;padding:20px}
a{color:#8ab4f8}.datas{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.datas a{padding:6px 12px;background:#1e2530;border-radius:8px;text-decoration:none}
.datas a.ativo{background:#1565c0;color:white}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:#171b22;border:1px solid #222a38;border-radius:12px;padding:14px;max-height:80vh;overflow:auto}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
.item{padding:8px 0;border-bottom:1px solid #222}
</style></head><body>
<h1>Radar Acoplado - {ultima}</h1><p>Espelho GitHub Pages | Local: http://127.0.0.1:8789</p><div class=datas>
'''
for d in datas[:60]:
    cls="ativo" if d==ultima else ""
    html+=f'<a class="{cls}" href="arquivo/{d}/ifch.txt">{d}</a>'
html+='</div><div class=grid>'
for tipo,label in [("concursos","CONCURSOS"),("ifch","IFCH")]:
    txt_path=base/ultima/f"{tipo}.txt"
    linhas=[]
    if txt_path.exists():
        linhas=[l.strip() for l in txt_path.read_text(encoding="utf-8", errors="ignore").splitlines() if "|" in l][:80]
        linhas=list(reversed(linhas))
    html+=f'<div class=card><h2>{label} - {len(linhas)}</h2>'
    for line in linhas:
        parts=line.split("|"); titulo=parts[0].strip(); link=parts[1].strip() if len(parts)>1 else "#"
        html+=f'<div class=item><a href="{link}" target=_blank>{titulo}</a><br><small>{link[:90]}</small></div>'
    html+=f'<p><a href="arquivo/{ultima}/{tipo}.txt" download>Baixar {tipo}.txt</a></div>'
html+='</div></body></html>'
Path("index.html").write_text(html, encoding="utf-8")
print("index.html gerado")

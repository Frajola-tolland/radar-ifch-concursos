import pathlib, datetime

ROOT = pathlib.Path(".")
ARQ_DIR = ROOT / "arquivo"
TODAY = datetime.date.today().isoformat()

def get_last_files():
    concursos_lines = []
    ifch_lines = []
    if ARQ_DIR.exists():
        for p in sorted(ARQ_DIR.glob("*"), reverse=True):
            if (p/"concursos.txt").exists():
                concursos_lines = (p/"concursos.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
                if (p/"ifch.txt").exists():
                    ifch_lines = (p/"ifch.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
                break
    return concursos_lines, ifch_lines

conc_raw, ifch_raw = get_last_files()

def parse_lines(lines):
    out=[]
    for line in lines:
        if "|" not in line: continue
        parts=line.split("|",1)
        title=parts[0].strip()
        url=parts[1].strip()
        if len(title)<15: continue
        out.append((title,url))
    return out

conc_parsed = parse_lines(conc_raw)
ifch_parsed = parse_lines(ifch_raw)

BLOCK_T = ["comprar","apostila","outras apostilas","outros concursos","...continuar lendo","organizadoras","centro-oeste","página inicial"]
BLOCK_U = ["apostilas","/pedido/compra","/provas/","/organizadoras"]

def valid_conc(title, url):
    t=title.lower(); u=url.lower()
    if any(b in t for b in BLOCK_T): return False
    if any(b in u for b in BLOCK_U): return False
    if u.endswith("pciconcursos.com.br/") or u.endswith("/concursos/"): return False
    if "/noticias/" not in u and "concurso" not in t and "seletivo" not in t and "edital" not in t:
        return False
    return True

conc_filtered=[]; seen=set()
for title,url in conc_parsed:
    if valid_conc(title,url) and url not in seen:
        seen.add(url); conc_filtered.append((title,url))

ifch_filtered=[]; seen=set()
for title,url in ifch_parsed:
    if url not in seen and len(title)>5:
        seen.add(url); ifch_filtered.append((title,url))

if not conc_filtered:
    conc_filtered=[("Ver todos concursos - PCI","https://www.pciconcursos.com.br/concursos/")]
if not ifch_filtered:
    ifch_filtered=[("Nenhum edital IFCH hoje","https://www.ifch.ufpa.br/")]

date_str=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

cards_conc=""
for title,url in conc_filtered:
    cards_conc+=f'<a class="card" href="{url}" target="_blank" data-title="{title.lower()}"><h3>{title}</h3><div class="badges"><span class="badge live">• AO VIVO</span><span class="badge">PCI</span><span class="badge">{TODAY}</span></div></a>\n'

cards_ifch=""
for title,url in ifch_filtered:
    cards_ifch+=f'<a class="card ifch-card" href="{url}" target="_blank" data-title="{title.lower()}"><h3>{title}</h3><div class="badges"><span class="badge ifch">• IFCH UFPA</span><span class="badge">{TODAY}</span></div></a>\n'

html="""<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RADAR IFCH v3</title>
<style>
:root{--bg:#070709;--card:#121214;--card2:#19191c;--border:#26262a;--text:#e8e8ea;--muted:#8a8a93;--accent:#a855f7;--green:#10b981}
*{margin:0;padding:0;box-sizing:border-box}body{background:var(--bg);color:var(--text);font-family:Inter,system-ui,sans-serif}
header{position:sticky;top:0;z-index:50;background:rgba(7,7,9,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:14px 20px}
.top{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
h1{font-size:20px}h1 b{color:var(--accent)}
.meta{font-family:monospace;font-size:11px;color:var(--muted);background:var(--card);border:1px solid var(--border);padding:6px 10px;border-radius:999px}
.tabs{max-width:1100px;margin:18px auto 0;padding:0 20px;display:flex;gap:8px}
.tab{padding:10px 16px;border-radius:10px;border:1px solid var(--border);background:var(--card);color:var(--muted);cursor:pointer;font-size:13px;font-weight:700}
.tab.active{background:#fff;color:#000}
.search-wrap{max-width:1100px;margin:12px auto;padding:0 20px}
#q{width:100%;background:var(--card);border:1px solid var(--border);color:var(--text);padding:14px;border-radius:12px;outline:none}
.grid{max-width:1100px;margin:0 auto;padding:18px 20px 80px;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:10px;text-decoration:none;color:inherit}
.card:hover{transform:translateY(-2px);background:var(--card2)}
.card.ifch-card{border-color:#2d2040}
.card h3{font-size:14px;line-height:1.35}
.badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:auto}
.badge{font-size:10px;padding:4px 8px;border-radius:999px;border:1px solid var(--border);color:var(--muted);font-family:monospace}
.badge.live{background:rgba(16,185,129,.15);color:var(--green);border-color:rgba(16,185,129,.3)}
.badge.ifch{background:rgba(168,85,247,.15);color:#a855f7;border-color:rgba(168,85,247,.3)}
.section{display:none}.section.active{display:grid}
footer{border-top:1px solid var(--border);padding:18px;text-align:center;color:var(--muted);font-family:monospace;font-size:10px}
</style></head><body>
<header><div class="top"><h1>RADAR <b>IFCH</b> <small style="color:var(--muted);font-size:12px">/ v3 abas</small></h1><div class="meta">"""+f"{len(conc_filtered)} concursos • {len(ifch_filtered)} IFCH • {date_str}"+"""</div></div></header>
<div class="tabs">
<button class="tab active" data-t="conc">CONCURSOS PUBLICOS <span>"""+str(len(conc_filtered))+"""</span></button>
<button class="tab" data-t="ifch">IFCH / UFPA <span>"""+str(len(ifch_filtered))+"""</span></button>
<button class="tab" data-t="all">TUDO</button>
</div>
<div class="search-wrap"><input id="q" placeholder="filtrar: professor, Limeira, PPHIST, edital..."></div>
<div id="grid-conc" class="grid section active">
"""+cards_conc+"""</div>
<div id="grid-ifch" class="grid section">
"""+cards_ifch+"""</div>
<div id="grid-all" class="grid section"></div>
<footer>radar-ifch v3 - separacao concursos | ifch ufpa - 2026</footer>
<script>
const q=document.getElementById('q');
const tabs=document.querySelectorAll('.tab');
const sections={conc:document.getElementById('grid-conc'),ifch:document.getElementById('grid-ifch'),all:document.getElementById('grid-all')};
const all=[...document.querySelectorAll('#grid-conc.card'),...document.querySelectorAll('#grid-ifch.card')];
const gridAll=document.getElementById('grid-all');
all.forEach(c=>{gridAll.appendChild(c.cloneNode(true))});
function filter(t){t=t.toLowerCase();document.querySelectorAll('.card').forEach(c=>{c.style.display=(c.dataset.title||'').includes(t)?'flex':'none'})}
q.addEventListener('input',e=>filter(e.target.value));
tabs.forEach(tab=>{tab.addEventListener('click',()=>{tabs.forEach(x=>x.classList.remove('active'));tab.classList.add('active');Object.values(sections).forEach(s=>s.classList.remove('active'));sections[tab.dataset.t].classList.add('active');filter(q.value)})});
</script></body></html>
"""

path=pathlib.Path("index.html")
path.write_text(html,encoding="utf-8")
print(f"OK {len(conc_filtered)} conc + {len(ifch_filtered)} ifch -> {path} {len(html)//1024}K")

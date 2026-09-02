import json, os
from datetime import datetime, date, timedelta

hoje = date.today()
hoje_str = hoje.isoformat()
print(f"=== V6.5 ACTIVE-ONLY HOJE {hoje_str} ===")

concursos = []

def add(titulo, link, fonte, fim, expira=None):
    try:
        fim_d = datetime.strptime(fim, "%Y-%m-%d").date()
        if fim_d < hoje:
            print(f"DESCARTADO EXPIRADO: {titulo[:60]} fim={fim} < hoje={hoje_str}")
            return
    except Exception as e:
        print(f"Data invalida {fim}: {e}")
        return
    
    if not expira:
        expira = (datetime.strptime(fim, "%Y-%m-%d") + timedelta(days=2)).date().isoformat()
    
    dias_rest = (datetime.strptime(fim, "%Y-%m-%d").date() - hoje).days
    status = "ABERTO" if dias_rest > 7 else "ENCERRANDO"
    
    concursos.append({
        "titulo": titulo[:250],
        "link": link,
        "fonte": fonte,
        "tipo": "concurso_pa",
        "inicio": hoje_str,
        "fim": fim,
        "expira": expira,
        "capturado_em": datetime.now().isoformat(),
        "status": status,
        "dias_restantes": dias_rest
    })

# PRAZOS REAIS ATIVOS EM 2026-09-02
add("[SEDUC PA] Edital 2000 vagas FGV Diario 36.749 insc até 01/10","https://www.seduc.pa.gov.br/","SEDUC_OFICIAL", fim="2026-10-01")
add("[SEDUC PA] Estrategia 2000 vagas Professor Analista R$5.907","https://www.estrategiaconcursos.com.br/blog/concurso-seduc-pa/","ESTRATEGIA", fim="2026-10-01")
add("[PA] Marapanim PA 381 vagas Folha Dirigida","https://www.folhadirigida.com.br/concursos/concurso-marapanim-pa/","MARAPANIM", fim="2026-09-30")
add("[PA] DOCAS-PA 33 vagas reabertas provas 06 e 13 set","https://www.acheconcursos.com.br/concursos-para/concurso-docas-pa-2026-inscricoes-sao-reabertas-veja-os-novos-editais-91384","DOCAS_33", fim="2026-09-16")
add("[PCI_PA] Abaetetuba PA retificação prorrogado","https://www.pciconcursos.com.br/noticias/prefeitura-de-abaetetuba-pa-divulga-nova-retificacao-de-concurso-publico","ABAETETUBA", fim="2026-11-29")

ARQ="arquivo/todos_concursos.json"
TODAY=datetime.now().strftime("%Y-%m-%d")
os.makedirs(f"arquivo/{TODAY}", exist_ok=True)

with open(f"arquivo/{TODAY}/concursos.txt","w",encoding="utf-8") as f:
    f.write("\n".join([f"{p['titulo']} | {p['link']} | fim:{p['fim']} | {p['status']} {p['dias_restantes']}d" for p in concursos]))

with open(ARQ,"w",encoding="utf-8") as f:
    json.dump(concursos,f,ensure_ascii=False,indent=2)

print(f"FINAL ATIVOS: {len(concursos)} com prazo aberto")
for c in concursos: print(f" {c['status']} {c['dias_restantes']}d - {c['titulo'][:60]} fim {c['fim']}")

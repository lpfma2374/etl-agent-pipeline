"""Cria linked records entre as tabelas da base Airtable 'Frameworks'.

Relações (chave natural -> record ID do Airtable):
- Indicadores Eficacia / Fases / Historico Versoes / Quadro Registos:
    'Processo' -> Processos Resumo, por 'ID Processo' (hex)
- Subseccoes Fases:
    'Processo' -> Processos Resumo, por 'ID Processo'
    'Fase'     -> Fases, por ('ID Processo', 'Nº Fase')  [chave composta]

O script é IDEMPOTENTE: PATCH do campo link substitui o valor (re-execuções
não duplicam). Campos link criados via API uma vez; a re-execução só refaz
as ligações.

Uso:
    python3 extract/link_frameworks.py --dry-run   # só valida mapeamentos
    python3 extract/link_frameworks.py             # cria campos + ligações
"""

import argparse
import os
import sys
import time
from collections import defaultdict

import requests

API = "https://api.airtable.com/v0"
BASE_ID = "apppOTLgiRO5kH4oA"
PARENT = "Processos Resumo"

# tabela filha -> (nome do campo link na filha, tabela alvo, chaves de junção)
LINKS = {
    "Indicadores Eficacia": [("Processo", PARENT, ("ID Processo",))],
    "Fases": [("Processo", PARENT, ("ID Processo",))],
    "Historico Versoes": [("Processo", PARENT, ("ID Processo",))],
    "Quadro Registos": [("Processo", PARENT, ("ID Processo",))],
    "Subseccoes Fases": [
        ("Processo", PARENT, ("ID Processo",)),
        ("Fase", "Fases", ("ID Processo", "Nº Fase")),
    ],
}


def _h():
    key = os.environ.get("AIRTABLE_API_KEY")
    if not key:
        sys.exit("AIRTABLE_API_KEY em falta (env)")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _get_tables(h):
    d = requests.get(f"{API}/meta/bases/{BASE_ID}/tables", headers=h).json()
    return {t["name"]: t for t in d["tables"]}


def _list_records(h, table, fields):
    """Devolve todos os registos com os campos pedidos (pagina via offset)."""
    recs, offset = [], None
    base = f"{API}/{BASE_ID}/{requests.utils.quote(table, safe='')}"
    while True:
        params = [("fields[]", f) for f in fields]
        if offset:
            params.append(("offset", offset))
        d = requests.get(base, headers=h, params=params).json()
        if "error" in d:
            sys.exit(f"erro a listar {table}: {d['error']}")
        recs += d.get("records", [])
        offset = d.get("offset")
        if not offset:
            return recs


def ensure_link_fields(h, tables):
    """Cria os campos link (e os inversos automáticos) se ainda não existirem."""
    created = []
    for child, links in LINKS.items():
        existing = {f["name"] for f in tables[child]["fields"]}
        for field, target, _ in links:
            if field in existing:
                continue
            # NOTA (quirk Airtable): criar link field exige APENAS
            # 'linkedTableId' — isReversed/prefersSingleRecordLink no POST
            # devolvem 422 confuso; o campo inverso é criado automaticamente.
            payload = {
                "name": field,
                "type": "multipleRecordLinks",
                "options": {"linkedTableId": tables[target]["id"]},
            }
            r = requests.post(
                f"{API}/meta/bases/{BASE_ID}/tables/{tables[child]['id']}/fields",
                headers=h, json=payload)
            r.raise_for_status()
            created.append(f"{child}.{field} -> {target}")
            print(f"[campo] criado: {child}.{field} -> {target}")
            time.sleep(0.4)
    return created


def build_maps(h, links_needed):
    """Mapas de chave natural -> record ID para cada tabela alvo."""
    maps = {}
    needed = {target for links in links_needed.values() for _, target, _ in links}
    for target in needed:
        keys = {k for links in LINKS.values() for _, t, ks in links
                if t == target for k in ks}
        recs = _list_records(h, target, sorted(keys))
        m = {}
        for r in recs:
            m[tuple(r["fields"].get(k) for k in sorted(keys))] = r["id"]
        maps[target] = m
        print(f"[mapa] {target}: {len(m)} registos (chaves {sorted(keys)})")
    return maps


def link_child(h, child, links, maps, dry_run):
    """PATCH dos campos link de cada registo filho (lotes de 10)."""
    keys = {k for _, _, ks in links for k in ks}
    recs = _list_records(h, child, sorted(keys))
    updates = []
    unmatched = defaultdict(list)
    for r in recs:
        f, patch = r["fields"], {}
        for field, target, join_keys in links:
            jk = sorted(join_keys)
            key = tuple(f.get(k) for k in jk)
            rid = maps[target].get(key)
            if rid is None:
                unmatched[field].append(str(key))
                continue
            patch[field] = [rid]
        if patch:
            updates.append({"id": r["id"], "fields": patch})
    print(f"[{child}] {len(recs)} registos | ligações: {len(updates)} "
          f"| sem match: {dict(unmatched) if unmatched else 'nenhuma'}")
    if dry_run or not updates:
        return len(updates), unmatched
    url = f"{API}/{BASE_ID}/{requests.utils.quote(child, safe='')}"
    for i in range(0, len(updates), 10):
        batch = {"records": updates[i:i + 10]}
        requests.patch(url, headers=h, json=batch).raise_for_status()
        time.sleep(0.4)
    return len(updates), unmatched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    h = _h()
    tables = _get_tables(h)
    missing = (set(LINKS) | {PARENT, "Fases"}) - set(tables)
    if missing:
        sys.exit(f"tabelas em falta: {missing}")
    if not args.dry_run:
        ensure_link_fields(h, tables)
    maps = build_maps(h, LINKS)
    total, all_unmatched = 0, defaultdict(int)
    for child, links in LINKS.items():
        n, unmatched = link_child(h, child, links, maps, args.dry_run)
        total += n
        for k, v in unmatched.items():
            all_unmatched[k] += len(v)
    mode = "DRY-RUN (nada escrito)" if args.dry_run else "APLICADO"
    print(f"[fim] {mode}: {total} ligações "
          f"({'sem unmatched' if not all_unmatched else 'ATENÇÃO unmatched: ' + dict(all_unmatched)})")


if __name__ == "__main__":
    main()

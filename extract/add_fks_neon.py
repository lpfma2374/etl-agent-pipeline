"""Adiciona foreign keys na base Neon PostgreSQL pós-migração (Frameworks).

Porquê pós-migração: o batch-run carrega por lotes e um lote de uma tabela
filha pode referenciar linhas do pai carregadas num lote posterior — as FKs
seriam violadas a meio do run. Depois do carregamento completo, todos os
alvos existem e as FKs são adicionadas e validadas.

Idempotente: ignora constraints que já existam (verifica pg_constraint).

Uso:
    python3 extract/add_fks_neon.py --dry-run   # só mostra as FKs
    python3 extract/add_fks_neon.py             # cria + valida FKs
"""

import argparse
import os

import psycopg2

# (tabela_filha, nome_constraint, colunas, tabela_pai, colunas_pai)
FKS = [
    ("Indicadores Eficacia", "fk_indicadores_processo",
     ["ID Processo"], "Processos Resumo", ["ID Processo"]),
    ("Fases", "fk_fases_processo",
     ["ID Processo"], "Processos Resumo", ["ID Processo"]),
    ("Subseccoes Fases", "fk_subseccoes_processo",
     ["ID Processo"], "Processos Resumo", ["ID Processo"]),
    ("Subseccoes Fases", "fk_subseccoes_fase",
     ["ID Processo", "Nº Fase"], "Fases", ["ID Processo", "Nº Fase"]),
    ("Historico Versoes", "fk_historico_processo",
     ["ID Processo"], "Processos Resumo", ["ID Processo"]),
    ("Quadro Registos", "fk_quadro_processo",
     ["ID Processo"], "Processos Resumo", ["ID Processo"]),
]


def _exists(cur, name):
    cur.execute("SELECT 1 FROM pg_constraint WHERE conname = %s", (name,))
    return cur.fetchone() is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL em falta (variável de ambiente)")
    conn = psycopg2.connect(dsn)
    created, skipped = [], []
    try:
        with conn.cursor() as cur:
            for child, cname, cols, parent, pcols in FKS:
                if _exists(cur, cname):
                    skipped.append(cname)
                    print(f"[fk] {cname}: já existe — skip")
                    continue
                sql = (
                    f'ALTER TABLE "{child}" ADD CONSTRAINT "{cname}" '
                    f'FOREIGN KEY (' + ", ".join(f'"{c}"' for c in cols) + ') '
                    f'REFERENCES "{parent}" ('
                    + ", ".join(f'"{c}"' for c in pcols) + ")"
                )
                if args.dry_run:
                    print(f"[fk] {cname} (DRY-RUN): {child} -> {parent}")
                    continue
                cur.execute(sql)
                conn.commit()
                created.append(cname)
                print(f"[fk] {cname}: criada e validada ({child} -> {parent})")
    finally:
        conn.close()
    mode = "DRY-RUN (nada escrito)" if args.dry_run else "APLICADO"
    print(f"[fim] {mode}: criadas {created or 'nenhuma'} | skip {skipped or 'nenhuma'}")


if __name__ == "__main__":
    main()

"""Gera dados sintéticos (seed) para testar o pipeline em CI sem APIs externas."""

import argparse
import csv
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=50,
                    help="número de linhas a gerar (predefinição: 50)")
    args = ap.parse_args()
    out = Path("seed_contacts.csv")
    rows = [
        {"id": i, "name": f"Contacto {i:04d}",
         "email": f"contacto{i:04d}@exemplo.pt",
         "created_at": f"2026-09-{(i % 28) + 1:02d}T10:00:00Z"}
        for i in range(1, args.rows + 1)
    ]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "name", "email", "created_at"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[seed] {len(rows)} linhas -> {out}")


if __name__ == "__main__":
    main()

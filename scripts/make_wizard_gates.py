"""Gera gates GE (suite + checkpoint) para um dataset do wizard 'Novo ETL'.

Uso:
  python3 scripts/make_wizard_gates.py --dataset wizard_<id> --mart mart_wizard_<id> \
      --columns-json <ficheiro com lista ordenada de colunas> --pk _row_id \
      [--extra-expectations <ficheiro json com expectações extra>]

Cria:
  great_expectations/expectations/<dataset>_suite.json
  great_expectations/checkpoints/<dataset>_checkpoint.yml
"""

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--mart", required=True)
    ap.add_argument("--columns-json", required=True,
                    help="ficheiro com a lista ordenada de colunas do mart")
    ap.add_argument("--pk", default="_row_id")
    ap.add_argument("--extra-expectations", default=None,
                    help="ficheiro json com lista de expectações extra")
    args = ap.parse_args()

    with open(args.columns_json) as fh:
        cols = json.load(fh)
    expectations = [
        {"expectation_type": "expect_table_columns_to_match_ordered_list",
         "kwargs": {"column_list": cols},
         "meta": {"notes": f"Schema canônico do {args.mart}"}},
        {"expectation_type": "expect_column_values_to_not_be_null",
         "kwargs": {"column": args.pk},
         "meta": {"notes": "PK obrigatória"}},
        {"expectation_type": "expect_column_values_to_be_unique",
         "kwargs": {"column": args.pk},
         "meta": {"notes": "Sem duplicados no destino"}},
        {"expectation_type": "expect_table_row_count_to_be_between",
         "kwargs": {"min_value": 1},
         "meta": {"notes": "Dataset não vazio"}},
    ]
    if args.extra_expectations:
        with open(args.extra_expectations) as fh:
            expectations += json.load(fh)

    suite = {
        "data_asset_type": None,
        "expectation_suite_name": f"{args.dataset}_suite",
        "expectations": expectations,
        "meta": {"great_expectations_version": "0.18.0",
                 "notes": f"Gates de qualidade do wizard {args.dataset}"},
    }
    out_suite = REPO / "great_expectations" / "expectations" / f"{args.dataset}_suite.json"
    out_suite.write_text(json.dumps(suite, indent=2, ensure_ascii=False), encoding="utf-8")

    cp = f"""name: {args.dataset}_checkpoint
config_version: 1
class_name: Checkpoint
run_name_template: "%Y%m%d-%H%M%S-{args.dataset}"
expectation_suite_name: {args.dataset}_suite
batch_request:
  datasource_name: marts_datasource
  data_connector_name: default_inferred_data_connector_name
  data_asset_name: {args.mart}
action_list:
  - name: store_validation_result
    action:
      class_name: StoreValidationResultAction
  - name: store_evaluation_params
    action:
      class_name: StoreEvaluationParametersAction
"""
    out_cp = REPO / "great_expectations" / "checkpoints" / f"{args.dataset}_checkpoint.yml"
    out_cp.write_text(cp, encoding="utf-8")

    print(json.dumps({"ok": True, "suite": str(out_suite), "checkpoint": str(out_cp),
                      "n_expectations": len(expectations)}))


if __name__ == "__main__":
    main()

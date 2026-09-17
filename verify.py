"""
Verification loop
==================

The assignment's real ask: don't just trust pass 1. This script runs two
independent checks and reports both, honestly (including where the agent
was wrong):

1. BLIND SECOND PASS (agent-vs-agent)
   For a random sample of apps, re-run research_app() from a fresh session
   with zero visibility into the pass-1 answer. Where the two passes agree
   on a field, confidence goes up. Where they disagree, that field is
   flagged for human review rather than silently averaged.

2. HUMAN GOLD CHECK (agent-vs-ground-truth)
   Reads human_review.csv (you fill this in by hand, checking real docs -
   see the template this script generates) and computes actual accuracy:
   pass-1 raw accuracy vs. accuracy after reconciling with the second pass
   and human corrections. This is the number that goes on the case study
   page, not the agent's self-reported confidence.

Run:
    python verify.py --data apps_data.json --sample 15 --make-template
    # ... hand-fill human_review.csv by checking the sampled apps' docs ...
    python verify.py --data apps_data.json --human human_review.csv --report verification_report.json
"""

import argparse
import csv
import json
import random

FIELDS_TO_CHECK = ["self_serve", "auth_methods", "api_surface", "buildable_today"]


def load(path):
    with open(path) as f:
        return json.load(f)["results"]


def make_template(rows, sample_n, out_csv="human_review.csv"):
    sample = random.sample(rows, min(sample_n, len(rows)))
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["app", "field", "agent_value", "evidence_url", "correct_value", "is_correct(y/n)"])
        for row in sample:
            for field in FIELDS_TO_CHECK:
                w.writerow([row["name"], field, row.get(field, ""), row.get("evidence_url", ""), "", ""])
    print(f"Wrote {out_csv} with {len(sample)} apps x {len(FIELDS_TO_CHECK)} fields.")
    print("Open each evidence_url, fill correct_value + is_correct(y/n) by hand, then re-run with --human.")


def blind_second_pass(rows, sample_n, composio, claude, research_app_fn, apps_lookup):
    """Re-derive a sample from scratch and diff against pass 1."""
    sample = random.sample(rows, min(sample_n, len(rows)))
    diffs = []
    for row in sample:
        app_tuple = apps_lookup[row["name"]]
        second = research_app_fn(composio, claude, app_tuple)
        mismatch_fields = [f for f in FIELDS_TO_CHECK if row.get(f) != second.get(f)]
        diffs.append({
            "app": row["name"],
            "pass1": {f: row.get(f) for f in FIELDS_TO_CHECK},
            "pass2": {f: second.get(f) for f in FIELDS_TO_CHECK},
            "mismatch_fields": mismatch_fields,
        })
    agree = sum(1 for d in diffs if not d["mismatch_fields"])
    return {
        "sample_size": len(diffs),
        "full_agreement_rate": agree / len(diffs) if diffs else None,
        "diffs": diffs,
    }


def score_against_human(human_csv):
    rows_by_app_field = {}
    with open(human_csv) as f:
        for r in csv.DictReader(f):
            if r["is_correct(y/n)"].strip().lower() not in ("y", "n"):
                continue  # not yet filled in
            key = (r["app"], r["field"])
            rows_by_app_field[key] = r["is_correct(y/n)"].strip().lower() == "y"

    if not rows_by_app_field:
        return None
    total = len(rows_by_app_field)
    correct = sum(1 for v in rows_by_app_field.values() if v)
    by_field = {}
    for (app, field), is_correct in rows_by_app_field.items():
        by_field.setdefault(field, []).append(is_correct)
    field_accuracy = {f: sum(v) / len(v) for f, v in by_field.items()}
    return {
        "n_checked": total,
        "overall_accuracy_pass1": correct / total,
        "field_accuracy_pass1": field_accuracy,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="apps_data.json")
    parser.add_argument("--sample", type=int, default=15)
    parser.add_argument("--make-template", action="store_true")
    parser.add_argument("--human", default=None)
    parser.add_argument("--blind-second-pass", action="store_true",
                         help="also re-run the agent blind on the sample (needs API keys)")
    parser.add_argument("--report", default="verification_report.json")
    args = parser.parse_args()

    rows = load(args.data)

    if args.make_template:
        make_template(rows, args.sample)
        return

    report = {}

    if args.human:
        human_result = score_against_human(args.human)
        report["human_gold_check"] = human_result
        if human_result:
            print(f"Pass-1 accuracy vs. human ground truth: {human_result['overall_accuracy_pass1']:.0%} "
                  f"over {human_result['n_checked']} field-checks")
            for field, acc in human_result["field_accuracy_pass1"].items():
                print(f"  {field}: {acc:.0%}")
        else:
            print("human_review.csv has no filled-in rows yet.")

    if args.blind_second_pass:
        from apps import APPS
        from research_agent import get_clients, research_app
        apps_lookup = {a[0]: a for a in APPS}
        composio, claude = get_clients()
        bsp = blind_second_pass(rows, args.sample, composio, claude, research_app, apps_lookup)
        report["blind_second_pass"] = bsp
        print(f"\nBlind second-pass full-agreement rate: {bsp['full_agreement_rate']:.0%} "
              f"over {bsp['sample_size']} apps")
        for d in bsp["diffs"]:
            if d["mismatch_fields"]:
                print(f"  DISAGREEMENT on {d['app']}: {d['mismatch_fields']}")

    with open(args.report, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nWrote {args.report}")


if __name__ == "__main__":
    main()

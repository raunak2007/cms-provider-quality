"""Disagreement vs utility. Produces the Pareto plot and the numbers behind it.

    python analyze.py runs/pilot.json
"""
import json, statistics as stats, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt


def disagreement(ratings, item_ids):
    """Mean across items of the SD across raters. High = raters see it differently."""
    per_item = []
    for iid in item_ids:
        vals = [r[iid] for r in ratings.values() if iid in r]
        if len(vals) == 5:
            per_item.append(stats.stdev(vals))
    return stats.mean(per_item) if per_item else None


def main(path):
    d = json.loads(Path(path).read_text())
    item_ids = [i["id"] for i in d["items"]]

    by_cond = {}
    for row in d["results"]:
        by_cond.setdefault(row["condition"], {"kind": row["kind"], "dis": [], "acc": []})
        s = disagreement(row["ratings"], item_ids)
        if s is not None:
            by_cond[row["condition"]]["dis"].append(s)
        if row["correct"] is not None:
            by_cond[row["condition"]]["acc"].append(1.0 if row["correct"] else 0.0)

    print(f"{'condition':<14}{'kind':<17}{'disagreement':>14}{'utility':>10}{'n':>5}")
    print("-" * 60)
    pts = []
    for c, v in by_cond.items():
        dis, acc, n = stats.mean(v["dis"]), stats.mean(v["acc"]), len(v["dis"])
        print(f"{c:<14}{v['kind']:<17}{dis:>14.3f}{acc:>10.2f}{n:>5}")
        pts.append((c, v["kind"], dis, acc))

    colors = {"baseline": "#5A6668", "functional": "#3A626B",
              "presentational": "#C2711A", "intervention": "#2F7A4F"}
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    for c, kind, dis, acc in pts:
        ax.scatter(dis, acc, s=160, color=colors.get(kind, "#555"), zorder=3)
        ax.annotate(f"{c}\n({kind})", (dis, acc), textcoords="offset points",
                    xytext=(10, -6), fontsize=10)
    base = next((p for p in pts if p[0] == "baseline"), None)
    if base:
        ax.axvline(base[2], color="#CCC", ls="--", lw=1, zorder=1)
        ax.axhline(base[3], color="#CCC", ls="--", lw=1, zorder=1)
        ax.text(0.02, 0.96, "top-left of the dashed lines\nPareto-dominates baseline",
                transform=ax.transAxes, fontsize=9, va="top", color="#666")
    ax.set_xlabel("Disagreement  (mean SD across raters, lower is better)")
    ax.set_ylabel("Utility  (decision accuracy)")
    ax.set_title("Harness interventions on the disagreement / utility frontier")
    ax.grid(alpha=0.25, zorder=0)
    fig.tight_layout()
    fig.savefig("pareto.png", dpi=160)
    print("\nwrote pareto.png")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "runs/pilot.json")

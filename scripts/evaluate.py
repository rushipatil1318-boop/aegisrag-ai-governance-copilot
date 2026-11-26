from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aegisrag import AegisRAG  # noqa: E402
from aegisrag.evaluation import evaluate, rows_as_dicts  # noqa: E402


def main() -> None:
    rag = AegisRAG()
    summary, rows = evaluate(rag)
    output_dir = ROOT / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    row_dicts = rows_as_dicts(rows)
    with (output_dir / "evaluation_details.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=row_dicts[0].keys())
        writer.writeheader()
        writer.writerows(row_dicts)

    labels = ["Recall@K", "MRR", "Keyword\ncoverage", "Citation\ncoverage"]
    values = [
        summary["retrieval_recall_at_k"],
        summary["mean_reciprocal_rank"],
        summary["answer_keyword_coverage"],
        summary["citation_coverage"],
    ]
    plt.figure(figsize=(9, 5.2))
    bars = plt.bar(labels, values, color=["#2f6fed", "#5c8df6", "#16a085", "#20b486"])
    plt.ylim(0, 1.05)
    plt.ylabel("Score")
    plt.title("AegisRAG Offline Evaluation")
    plt.grid(axis="y", alpha=0.2)
    for bar, value in zip(bars, values, strict=True):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig(output_dir / "evaluation_dashboard.png", dpi=180)
    plt.close()

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


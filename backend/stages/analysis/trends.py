"""Publication trend analysis with CAGR calculation."""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
RESEARCH_TITLE = cfg["research"]["title"]
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def _cagr(start_val, end_val, years):
    if start_val == 0 or years == 0:
        return 0
    return (pow((end_val / start_val), (1 / years)) - 1) * 100


def run():
    path = os.path.join(BASE_DIR, "data", "processed", "final_thematic_dataset.csv")
    fallback = os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
    elif os.path.exists(fallback):
        df = pd.read_csv(fallback)
    else:
        print("No dataset found. Run Data Acquisition and Topic Modeling first.")
        return
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    trend = df.groupby("year").size().reset_index(name="count").sort_values("year")

    start_yr = int(trend["year"].min())
    end_yr = int(trend["year"].max())
    total_cagr = _cagr(trend["count"].iloc[0], trend["count"].iloc[-1], len(trend) - 1)

    midpoint = (start_yr + end_yr) // 2
    pre = trend[trend["year"] < midpoint]
    post = trend[trend["year"] >= midpoint]
    pre_cagr = _cagr(pre["count"].iloc[0], pre["count"].iloc[-1], len(pre) - 1) if len(pre) > 1 else 0
    post_cagr = _cagr(post["count"].iloc[0], post["count"].iloc[-1], len(post) - 1) if len(post) > 1 else 0

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(trend["year"], trend["count"], marker="o", linestyle="-", color="#1f77b4", linewidth=2, label="Annual Publications")
    plt.axvline(x=midpoint, color="red", linestyle="--", alpha=0.5, label=f"Mid-Period ({midpoint})")
    plt.title(f"{RESEARCH_TITLE}: Publication Trends", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Publications")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.annotate(f"Total CAGR: {total_cagr:.2f}%", xy=(0.05, 0.95), xycoords="axes fraction", fontsize=10,
                 bbox=dict(boxstyle="round", fc="w"))
    plt.annotate(f"Post-{midpoint} CAGR: {post_cagr:.2f}%", xy=(0.05, 0.88), xycoords="axes fraction", fontsize=10,
                 bbox=dict(boxstyle="round", fc="w", ec="red"))

    trends_dir = os.path.join(OUTPUTS_DIR, "trends")
    os.makedirs(trends_dir, exist_ok=True)
    plt.savefig(os.path.join(trends_dir, "publication_trend.png"), dpi=300, bbox_inches="tight")
    plt.close()

    pd.DataFrame({
        "Metric": ["Total Papers", "Start Year", "End Year", "Total CAGR", f"Pre-{midpoint} CAGR", f"Post-{midpoint} CAGR"],
        "Value": [len(df), start_yr, end_yr, f"{total_cagr:.2f}%", f"{pre_cagr:.2f}%", f"{post_cagr:.2f}%"]
    }).to_csv(os.path.join(trends_dir, "trend_summary.csv"), index=False)

    trend.to_csv(os.path.join(trends_dir, "yearly_counts.csv"), index=False)
    print("Trend analysis complete")

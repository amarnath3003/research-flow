"""Burst detection using Z-score anomaly detection."""
import pandas as pd
import numpy as np
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    df_path = os.path.join(BASE_DIR, "data", "processed", "final_thematic_dataset.csv")
    fallback_path = os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv")

    if os.path.exists(df_path):
        df = pd.read_csv(df_path)
    elif os.path.exists(fallback_path):
        df = pd.read_csv(fallback_path)
    else:
        print("No dataset found.")
        return

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    def get_kw(k):
        if not isinstance(k, str):
            return []
        return [x.strip().lower() for x in k.replace(";", ",").split(",") if x.strip()]

    df["kw_list"] = df["keywords"].apply(get_kw)

    kw_year = []
    for year in sorted(df["year"].unique()):
        yd = df[df["year"] == year]
        all_kw = [kw for sublist in yd["kw_list"] for kw in sublist]
        for kw, count in Counter(all_kw).items():
            kw_year.append({"year": year, "keyword": kw, "count": count})

    pivot = pd.DataFrame(kw_year).pivot(index="year", columns="keyword", values="count").fillna(0)

    bursts = []
    for kw in pivot.sum().sort_values(ascending=False).head(200).index:
        series = pivot[kw]
        mean, std = series.mean(), series.std()
        if std == 0:
            continue
        for year, val in series.items():
            z = (val - mean) / std
            if z > 2.5 and val > 5:
                bursts.append({"keyword": kw, "burst_year": year, "count": val, "z_score": round(z, 2)})

    burst_dir = os.path.join(OUTPUTS_DIR, "bursts")
    os.makedirs(burst_dir, exist_ok=True)

    if bursts:
        burst_df = pd.DataFrame(bursts).sort_values(["burst_year", "z_score"], ascending=[True, False])
        burst_df.to_csv(os.path.join(burst_dir, "burst_detection.csv"), index=False)
        print(f"Bursts detected: {len(burst_df)}")
    else:
        print("No bursts detected.")
        pd.DataFrame(columns=["keyword", "burst_year", "count", "z_score"]).to_csv(
            os.path.join(burst_dir, "burst_detection.csv"), index=False
        )

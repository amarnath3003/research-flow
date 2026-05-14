"""Keyword co-occurrence and co-authorship network exports."""
import pandas as pd
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


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

    # Keyword co-occurrence edges
    keyword_pairs = []
    for kws in df["keywords"]:
        if pd.isna(kws):
            continue
        kw_list = [k.strip() for k in kws.replace(";", ",").split(",") if k.strip()]
        keyword_pairs.extend((a, b) for i, a in enumerate(kw_list) for b in kw_list[i + 1:])

    edge_counts = Counter(keyword_pairs)
    edges_df = pd.DataFrame(
        [(a, b, c) for (a, b), c in edge_counts.items()],
        columns=["Source", "Target", "Weight"]
    ).sort_values("Weight", ascending=False)

    # Keyword nodes
    node_counts = Counter(kw for pair in keyword_pairs for kw in pair)
    nodes_df = pd.DataFrame(node_counts.items(), columns=["Id", "Frequency"]).sort_values("Frequency", ascending=False)

    nets_dir = os.path.join(OUTPUTS_DIR, "networks")
    os.makedirs(nets_dir, exist_ok=True)
    edges_df.to_csv(os.path.join(nets_dir, "keyword_cooccurrence_edges.csv"), index=False)
    nodes_df.to_csv(os.path.join(nets_dir, "keyword_nodes.csv"), index=False)

    # Co-authorship edges
    author_pairs = []
    for authors in df["authors"]:
        if pd.isna(authors):
            continue
        auth_list = [a.strip() for a in authors.split(";") if a.strip()]
        author_pairs.extend((a, b) for i, a in enumerate(auth_list) for b in auth_list[i + 1:])

    auth_edge_counts = Counter(author_pairs)
    auth_edges = pd.DataFrame(
        [(a, b, c) for (a, b), c in auth_edge_counts.items()],
        columns=["Source", "Target", "Weight"]
    ).sort_values("Weight", ascending=False)
    auth_edges.to_csv(os.path.join(nets_dir, "coauthorship_edges.csv"), index=False)
    print("Network analysis complete")

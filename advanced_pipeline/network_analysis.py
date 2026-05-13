import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter


print("Loading dataset...")


df = pd.read_csv(
    "data/processed/topic_dataset.csv"
)


G = nx.Graph()


keyword_pairs = []

for kws in df["keywords"]:

    if pd.isna(kws):
        continue

    split_kws = [
        k.strip().lower()
        for k in kws.split(";")
    ]

    for i in range(len(split_kws)):
        for j in range(i + 1, len(split_kws)):
            keyword_pairs.append(
                (split_kws[i], split_kws[j])
            )


pair_counts = Counter(keyword_pairs)


for (a, b), weight in pair_counts.items():

    if weight >= 3:
        G.add_edge(a, b, weight=weight)


net = Network(height="900px", width="100%")

net.from_nx(G)


net.show(
    "outputs/networks/keyword_network.html",
    notebook=False
)


print("Network generated")

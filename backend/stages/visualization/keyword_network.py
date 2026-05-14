"""Figure 2: Keyword Co-occurrence Network."""
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    nodes = pd.read_csv(os.path.join(OUTPUTS_DIR, "networks", "keyword_nodes.csv"))
    edges = pd.read_csv(os.path.join(OUTPUTS_DIR, "networks", "keyword_cooccurrence_edges.csv"))

    top_n = 40
    nodes_top = nodes.sort_values("Frequency", ascending=False).head(top_n)
    top_kw = nodes_top["Id"].tolist()
    edges_filt = edges[edges["Source"].isin(top_kw) & edges["Target"].isin(top_kw)].sort_values("Weight", ascending=False).head(100)

    G = nx.Graph()
    for _, r in nodes_top.iterrows():
        G.add_node(r["Id"], size=r["Frequency"])
    for _, r in edges_filt.iterrows():
        G.add_edge(r["Source"], r["Target"], weight=r["Weight"])

    core = top_kw[:6]
    peri = top_kw[6:]
    pos = nx.shell_layout(G, [core, peri])

    max_freq = max(G.nodes[n]["size"] for n in G.nodes())
    node_sizes = [(G.nodes[n]["size"] / max_freq) * 4500 + 1000 for n in G.nodes()]
    edge_weights = [G.edges[e]["weight"] for e in G.edges()]
    max_w = max(edge_weights) if edge_weights else 1
    edge_widths = [(w / max_w) * 10 + 1 for w in edge_weights]

    plt.figure(figsize=(24, 20))
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color="#34495e", alpha=0.35,
                           arrows=True, arrowsize=1, connectionstyle="arc3,rad=0.15")
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="#00d2ff", alpha=1,
                           edgecolors="#2c3e50", linewidths=2.5)

    for node, (x, y) in pos.items():
        if node in core:
            plt.text(x, y + 0.08, node, fontsize=15, fontweight="black", ha="center", va="bottom",
                     color="white", bbox=dict(facecolor="#2c3e50", alpha=0.9, boxstyle="round,pad=0.3"))
        else:
            angle = np.arctan2(y, x)
            lx, ly = 1.1 * x, 1.1 * y
            ha = "left" if x > 0 else "right"
            plt.text(lx, ly, node, fontsize=12, fontweight="bold", ha=ha, va="center",
                     color="#34495e", bbox=dict(facecolor="white", alpha=0.85, edgecolor="#bdc3c7", boxstyle="round,pad=0.2"))

    plt.title("Keyword Co-occurrence Network", fontsize=32, pad=60, fontweight="bold", color="#2c3e50")
    plt.axis("off")
    plt.xlim(-1.4, 1.4)
    plt.ylim(-1.4, 1.4)

    figs_dir = os.path.join(OUTPUTS_DIR, "figures")
    os.makedirs(figs_dir, exist_ok=True)
    plt.savefig(os.path.join(figs_dir, "figure2_keyword_network.png"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print("Figure 2 generated")

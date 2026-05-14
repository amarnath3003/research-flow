import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

# Configuration
# Using absolute-style relative paths from root for reliability
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
NODES_FILE = os.path.join(BASE_PATH, "../phase3_analysis/outputs/networks/keyword_nodes.csv")
EDGES_FILE = os.path.join(BASE_PATH, "../phase3_analysis/outputs/networks/keyword_cooccurrence_edges.csv")
OUTPUT_DIR = os.path.join(BASE_PATH, "outputs")

def run_keyword_network():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    nodes_df = pd.read_csv(NODES_FILE)
    edges_df = pd.read_csv(EDGES_FILE)

    # 1. Filter for top keywords
    top_n = 40 # Slightly more nodes to show the core vs periphery better
    nodes_sorted = nodes_df.sort_values('Frequency', ascending=False).head(top_n)
    top_keywords = nodes_sorted['Id'].tolist()
    
    # 2. Filter edges (moderate filtering for clean lines)
    edges_filtered = edges_df[
        edges_df['Source'].isin(top_keywords) & 
        edges_df['Target'].isin(top_keywords)
    ].sort_values('Weight', ascending=False).head(100)

    # Create Graph
    G = nx.Graph()
    for _, row in nodes_sorted.iterrows():
        G.add_node(row['Id'], size=row['Frequency'])
    
    for _, row in edges_filtered.iterrows():
        G.add_edge(row['Source'], row['Target'], weight=row['Weight'])

    # 3. SHELL LAYOUT: Define the core and the periphery
    # Core: Top 6 most frequent keywords
    # Periphery: The rest
    core_nodes = top_keywords[:6]
    periphery_nodes = top_keywords[6:]
    
    # Plotting
    plt.figure(figsize=(24, 20))
    
    # Multi-shell layout places core nodes in a small inner circle and others in a large outer circle
    pos = nx.shell_layout(G, [core_nodes, periphery_nodes])
    
    # Adjust periphery nodes slightly to avoid a perfect circle look (optional but looks more natural)
    # for node in periphery_nodes:
    #     pos[node] *= (1.0 + np.random.uniform(-0.1, 0.1))

    # Node sizes (normalized)
    max_freq = max([G.nodes[n]['size'] for n in G.nodes()])
    node_sizes = [(G.nodes[n]['size'] / max_freq) * 4500 + 1000 for n in G.nodes()]
    
    # Edge widths (weighted)
    import numpy as np
    edge_weights = [G.edges[e]['weight'] for e in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [(w / max_weight) * 10 + 1 for w in edge_weights]

    # Draw elements - Smooth curved edges to highlight interconnections
    nx.draw_networkx_edges(G, pos, width=edge_widths, 
                           edge_color='#34495e', 
                           alpha=0.35, 
                           arrows=True, arrowsize=1,
                           connectionstyle='arc3,rad=0.15') 
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                           node_color='#00d2ff', 
                           alpha=1.0, 
                           edgecolors='#2c3e50', 
                           linewidths=2.5)
    
    # 4. SMART LABELING: Different styles for Core vs Periphery
    for node, (x, y) in pos.items():
        is_core = node in core_nodes
        
        # Determine alignment and placement
        if is_core:
            # Core labels: centered on the node or slightly offset
            plt.text(x, y + 0.08, s=node, 
                     fontsize=15, fontweight='black', 
                     ha='center', va='bottom',
                     color='white',
                     bbox=dict(facecolor='#2c3e50', alpha=0.9, edgecolor='none', boxstyle='round,pad=0.3'))
        else:
            # Periphery labels: outside the shell
            angle = np.arctan2(y, x)
            lx, ly = (1.1 * x), (1.1 * y)
            ha = 'left' if x > 0 else 'right'
            
            plt.text(lx, ly, s=node, 
                     fontsize=12, fontweight='bold', 
                     ha=ha, va='center',
                     color='#34495e',
                     bbox=dict(facecolor='white', alpha=0.85, edgecolor='#bdc3c7', boxstyle='round,pad=0.2'))

    plt.title('Keyword Interconnection Network\n(Core-Periphery Thematic Structure)', fontsize=32, pad=60, fontweight='bold', color='#2c3e50')
    plt.axis('off')
    
    # Ensure the plot has enough room for external labels
    plt.xlim(-1.4, 1.4)
    plt.ylim(-1.4, 1.4)

    # Footer
    plt.figtext(0.5, 0.05, "Core-Periphery layout: Central nodes represent the primary research identity, while outer nodes represent supporting technical domains.", 
                ha="center", fontsize=16, style='italic', color='#7f8c8d', fontweight='bold')
    
    # Add a subtle footer
    plt.figtext(0.5, 0.02, "Node size represents keyword frequency | Edge width represents co-occurrence strength", 
                ha="center", fontsize=12, style='italic', color='gray')

    # Save
    plot_path = os.path.join(OUTPUT_DIR, 'figure2_keyword_network.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Generated keyword network: {plot_path}")

if __name__ == "__main__":
    run_keyword_network()

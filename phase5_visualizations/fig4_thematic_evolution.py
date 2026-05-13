import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuration
INPUT_FILE = "../phase4_interpretation/outputs/evolution/theme_evolution.csv"
OUTPUT_DIR = "outputs"

def run_thematic_evolution():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(INPUT_FILE):
        print("Error: Evolution data not found. Skipping Figure 4.")
        return

    df = pd.read_csv(INPUT_FILE)
    
    # Sort by year
    df = df.sort_values('year')

    # Themes to plot
    themes = [c for c in df.columns if c != 'year']
    
    # Plotting
    plt.figure(figsize=(12, 7))
    plt.stackplot(df['year'], [df[t] for t in themes], labels=themes, alpha=0.8, 
                  colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])

    plt.title('Figure 4: Thematic Evolution Timeline (2010-2024)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Cumulative Theme Frequency', fontsize=12)
    plt.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.xticks(df['year'])
    plt.xlim(df['year'].min(), df['year'].max())

    # Save
    plot_path = os.path.join(OUTPUT_DIR, 'figure4_thematic_evolution.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Generated Figure 4: {plot_path}")

if __name__ == "__main__":
    run_thematic_evolution()

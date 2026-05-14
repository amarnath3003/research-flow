import pandas as pd
import plotly.express as px
import os

# Configuration
INPUT_FILE = "../phase3_analysis/outputs/geopolitical/country_collaboration.csv"
OUTPUT_DIR = "outputs"

# Mapping for common countries to ISO Alpha-3
ISO_MAPPING = {
    'USA': 'USA', 'United States': 'USA', 'USA.': 'USA',
    'China': 'CHN', 'UK': 'GBR', 'United Kingdom': 'GBR',
    'Germany': 'DEU', 'India': 'IND', 'Canada': 'CAN',
    'Australia': 'AUS', 'France': 'FRA', 'Italy': 'ITA',
    'Japan': 'JPN', 'Spain': 'ESP', 'South Korea': 'KOR',
    'Brazil': 'BRA', 'Netherlands': 'NLD', 'Switzerland': 'CHE'
}

def run_collaboration_map():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(INPUT_FILE):
        print("Error: Geopolitical data not found. Skipping collaboration map.")
        return

    df = pd.read_csv(INPUT_FILE)
    df['iso_alpha'] = df['countries'].map(ISO_MAPPING)
    
    # Filter out entries that couldn't be mapped
    df = df.dropna(subset=['iso_alpha'])

    # Create Choropleth
    fig = px.choropleth(df, locations="iso_alpha",
                        color="Total",
                        hover_name="countries",
                        color_continuous_scale=px.colors.sequential.Viridis,
                        title="Global Research Collaboration Map")

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        margin={"r":0,"t":50,"l":0,"b":0}
    )

    # Save as Static Image (Plotly requires kaleido for this, which might not be installed)
    # I'll try to save it, but also export the data for manual plotting if it fails.
    try:
        plot_path = os.path.join(OUTPUT_DIR, 'figure3_collaboration_map.png')
        fig.write_image(plot_path, scale=2)
        print(f"Generated collaboration map: {plot_path}")
    except Exception as e:
        print(f"Plotly static export failed (likely missing kaleido). Saved HTML instead.")
        fig.write_html(os.path.join(OUTPUT_DIR, 'figure3_collaboration_map.html'))

if __name__ == "__main__":
    run_collaboration_map()

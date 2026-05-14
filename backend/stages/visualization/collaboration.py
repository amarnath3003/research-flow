"""Figure 3: Global Research Collaboration Map (choropleth)."""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

ISO_MAP = {
    "USA": "USA", "United States": "USA", "China": "CHN", "UK": "GBR",
    "United Kingdom": "GBR", "Germany": "DEU", "India": "IND", "Canada": "CAN",
    "Australia": "AUS", "France": "FRA", "Italy": "ITA", "Japan": "JPN",
    "Spain": "ESP", "South Korea": "KOR", "Brazil": "BRA", "Netherlands": "NLD",
    "Switzerland": "CHE",
}


def run():
    path = os.path.join(OUTPUTS_DIR, "geopolitical", "country_collaboration.csv")
    if not os.path.exists(path):
        print("Geopolitical data not found.")
        return

    df = pd.read_csv(path)
    df["iso"] = df["country_name"].map(ISO_MAP)
    df = df.dropna(subset=["iso"])

    try:
        import plotly.express as px
        fig = px.choropleth(df, locations="iso", color="Total",
                             hover_name="country_name",
                             color_continuous_scale=px.colors.sequential.Viridis,
                             title="Global Research Collaboration Map")
        fig.update_layout(geo=dict(showframe=False, showcoastlines=True, projection_type="equirectangular"),
                          margin={"r": 0, "t": 50, "l": 0, "b": 0})
        figs_dir = os.path.join(OUTPUTS_DIR, "figures")
        os.makedirs(figs_dir, exist_ok=True)
        try:
            fig.write_image(os.path.join(figs_dir, "figure3_collaboration_map.png"), scale=2)
        except Exception:
            fig.write_html(os.path.join(figs_dir, "figure3_collaboration_map.html"))
        print("Figure 3 generated")
    except ImportError:
        print("Plotly not available, skipping collaboration map")

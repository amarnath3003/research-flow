import pandas as pd
import os
import re

# Configuration
INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/geopolitical"

# Common country keywords for extraction if full affiliation is present
COUNTRIES = [
    "USA", "United States", "UK", "United Kingdom", "China", "India", "Germany", 
    "Canada", "Australia", "France", "Italy", "Spain", "Brazil", "Japan", 
    "South Korea", "Netherlands", "Switzerland", "Norway", "Sweden", "Finland",
    "Zimbabwe", "Canada", "Israel", "Ukraine", "Indonesia", "Tanzania"
]

def extract_countries(text):
    if not isinstance(text, str):
        return []
    found = []
    for country in COUNTRIES:
        if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
            found.append(country)
    return list(set(found))

def run_geopolitical_analysis():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    elif os.path.exists(FALLBACK_FILE):
        df = pd.read_csv(FALLBACK_FILE)
    else:
        print("Error: No dataset found.")
        return

    # Check for affiliation column
    aff_col = None
    for col in ['affiliations', 'affiliation', 'address']:
        if col in df.columns:
            aff_col = col
            break
    
    if not aff_col:
        print("Warning: No explicit affiliation column found. Attempting to parse 'authors' column...")
        aff_col = 'authors'

    # Extract Countries
    df['countries'] = df[aff_col].apply(extract_countries)
    
    # Calculate SCP vs MCP
    # SCP: Only one country found
    # MCP: Multiple countries found
    def categorize_collab(countries):
        if len(countries) == 0: return "Unknown"
        if len(countries) == 1: return "SCP"
        return "MCP"

    df['collab_type'] = df['countries'].apply(categorize_collab)

    # Explode countries for counting
    exploded = df.explode('countries')
    country_counts = exploded.groupby(['countries', 'collab_type']).size().unstack(fill_value=0).reset_index()
    
    if 'SCP' not in country_counts.columns: country_counts['SCP'] = 0
    if 'MCP' not in country_counts.columns: country_counts['MCP'] = 0
    
    country_counts['Total'] = country_counts['SCP'] + country_counts['MCP']
    country_counts['MCP_Ratio'] = (country_counts['MCP'] / country_counts['Total']) * 100
    
    country_counts = country_counts.sort_values('Total', ascending=False)

    # Save results
    country_counts.to_csv(os.path.join(OUTPUT_DIR, 'country_collaboration.csv'), index=False)
    
    print("Geopolitical analysis complete.")
    print(f"Top 10 Countries by Contribution:")
    print(country_counts.head(10))

if __name__ == "__main__":
    run_geopolitical_analysis()

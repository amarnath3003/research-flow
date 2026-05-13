import pandas as pd
import os

# Paths
INPUT_DATASET = "phase1_refinement/final_curated_dataset.csv"
MAPPING_FILE = "phase2_validation/topic_merging_map.csv"
OUTPUT_DATASET = "phase2_validation/final_thematic_dataset.csv"

def apply_merges():
    print("Loading mapping...")
    if not os.path.exists(MAPPING_FILE):
        print(f"Error: {MAPPING_FILE} not found. Please run generate_template.py and fill it first.")
        return
        
    mapping_df = pd.read_csv(MAPPING_FILE)
    
    # Check if user filled in the theme names
    if mapping_df['new_major_theme_name'].isna().all() or (mapping_df['new_major_theme_name'] == "").all():
        print("Error: The 'new_major_theme_name' column is empty. Please fill it before running this script.")
        return

    # Create mapping dictionary: original_topic_id -> new_major_theme_name
    topic_map = dict(zip(mapping_df['original_topic_id'], mapping_df['new_major_theme_name']))
    
    print(f"Loading dataset from {INPUT_DATASET}...")
    df = pd.read_csv(INPUT_DATASET)
    
    # Apply mapping
    print("Applying merges and renaming...")
    df['major_theme'] = df['topic'].map(topic_map)
    
    # Drop rows where mapping failed (if any)
    unmapped_count = df['major_theme'].isna().sum()
    if unmapped_count > 0:
        print(f"Warning: {unmapped_count} papers could not be mapped to a theme. Check your mapping file.")
    
    # Save final dataset
    df.to_csv(OUTPUT_DATASET, index=False)
    
    print("-" * 30)
    print("PHASE 2 SUMMARY")
    print(f"Original Topics: {len(mapping_df)}")
    print(f"New Major Themes: {df['major_theme'].nunique()}")
    print(f"Themes created: {', '.join(df['major_theme'].unique().astype(str))}")
    print("-" * 30)
    print(f"Final thematic dataset saved to {OUTPUT_DATASET}")

if __name__ == "__main__":
    apply_merges()

import pandas as pd
import os

# Paths
INPUT_DATASET = "phase1_refinement/final_curated_dataset.csv"
OUTPUT_TEMPLATE = "phase2_validation/topic_merging_map.csv"

def generate_merging_template():
    if not os.path.exists(INPUT_DATASET):
        print(f"Error: {INPUT_DATASET} not found.")
        return
        
    df = pd.read_csv(INPUT_DATASET)
    topics = sorted(df['topic'].unique())
    
    # Create template
    template_data = []
    for t_id in topics:
        template_data.append({
            "original_topic_id": t_id,
            "original_keywords": "", # Placeholder, user can see keywords in Phase 1 CSV
            "new_major_theme_name": "" # USER: Fill this with the 8-15 high-level names
        })
        
    template_df = pd.DataFrame(template_data)
    template_df.to_csv(OUTPUT_TEMPLATE, index=False)
    print(f"Template created: {OUTPUT_TEMPLATE}")
    print("Action: Map each original_topic_id to one of 8-15 'new_major_theme_name' labels.")

if __name__ == "__main__":
    generate_merging_template()

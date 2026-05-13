import pandas as pd
import os

# Paths
DATASET_PATH = "advanced_pipeline/data/processed/topic_dataset.csv"
CLASSIFICATION_PATH = "phase1_refinement/topic_classification.csv"
OUTPUT_PATH = "phase1_refinement/final_curated_dataset.csv"

def refine_dataset():
    print("Loading classification labels...")
    if not os.path.exists(CLASSIFICATION_PATH):
        print(f"Error: Classification file not found at {CLASSIFICATION_PATH}")
        print("Please run step1_export_topics.py and fill in the CSV first.")
        return
        
    class_df = pd.read_csv(CLASSIFICATION_PATH)
    
    # Filter only topics marked as 'keep'
    # Normalize string to handle case sensitivity or extra spaces
    class_df['keep/remove'] = class_df['keep/remove'].str.strip().str.lower()
    keep_topics = class_df[class_df['keep/remove'] == 'keep']['topic_id'].tolist()
    
    if not keep_topics:
        print("Warning: No topics marked as 'keep'. Please check your CSV.")
        return
        
    print(f"Topics to keep: {len(keep_topics)}")
    
    print(f"Loading original dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)
    initial_count = len(df)
    
    # Filter dataset
    refined_df = df[df['topic'].isin(keep_topics)]
    final_count = len(refined_df)
    
    # Save the refined dataset
    refined_df.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 30)
    print("REFINEMENT SUMMARY")
    print(f"Initial papers: {initial_count}")
    print(f"Refined papers: {final_count}")
    print(f"Removed papers: {initial_count - final_count}")
    print(f"Reduction: {((initial_count - final_count)/initial_count)*100:.2f}%")
    print("-" * 30)
    print(f"Final curated dataset saved to {OUTPUT_PATH}")
    print("\nMethodology Note:")
    print("Multi-stage semantic filtering and manual validation were conducted to preserve thematic alignment with scholarly communication and research security.")

if __name__ == "__main__":
    refine_dataset()

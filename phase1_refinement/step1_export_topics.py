import pandas as pd
import numpy as np
from bertopic import BERTopic
import os

# Paths
MODEL_PATH = "advanced_pipeline/models/bertopic_model"
DATASET_PATH = "advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_PATH = "phase1_refinement/topic_classification.csv"

def export_topic_summary():
    print(f"Loading BERTopic model from {MODEL_PATH}...")
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    model = BERTopic.load(MODEL_PATH)
    
    print(f"Loading dataset from {DATASET_PATH}...")
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        return
        
    df = pd.read_csv(DATASET_PATH)
    
    print("Generating topic summaries...")
    topic_info = model.get_topic_info()
    
    # We want: topic_id, topic_name, top_keywords, document_count, representative_titles, representative_abstracts
    summary_data = []
    
    for _, row in topic_info.iterrows():
        topic_id = row['Topic']
        if topic_id == -1: # Skip outliers for now or label as noise
            name = "Outliers"
            count = row['Count']
            keywords = "N/A"
        else:
            name = row['Name']
            count = row['Count']
            keywords = ", ".join([w[0] for w in model.get_topic(topic_id)[:10]])
        
        # Get representative docs
        # BERTopic has get_representative_docs but it returns the full text
        # We want titles and abstracts separately.
        # We can find docs belonging to this topic in our dataframe.
        topic_docs = df[df['topic'] == topic_id].head(3)
        
        titles = " | ".join(topic_docs['title'].fillna("No Title").tolist())
        abstracts = " | ".join(topic_docs['abstract'].fillna("No Abstract").str[:200].tolist()) + "..."
        
        summary_data.append({
            "topic_id": topic_id,
            "topic_name": name,
            "top_keywords": keywords,
            "document_count": count,
            "representative_titles": titles,
            "representative_abstracts": abstracts,
            "label": "", # User to fill
            "classification": "", # User to fill (CORE, SUPPORTING, NOISE)
            "keep/remove": "" # User to fill (keep, remove)
        })
        
    summary_df = pd.DataFrame(summary_data)
    
    # Reorder columns to put labeling columns at the front for easier manual editing
    cols = ["topic_id", "label", "classification", "keep/remove", "topic_name", "document_count", "top_keywords", "representative_titles", "representative_abstracts"]
    summary_df = summary_df[cols]
    
    summary_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully exported topic summary to {OUTPUT_PATH}")
    print("Next Step: Open this CSV and fill in the 'label', 'classification', and 'keep/remove' columns.")

if __name__ == "__main__":
    export_topic_summary()

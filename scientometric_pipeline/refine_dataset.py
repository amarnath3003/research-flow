import pandas as pd
import os
import sys

def refine_dataset(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Refining dataset: {file_path}")
    df = pd.read_csv(file_path)
    original_count = len(df)
    
    # Define contamination terms to exclude
    contamination_terms = [
        "smart farming",
        "smart agriculture",
        "smart grid",
        "6g",
        "blockchain infrastructure",
        "industrial iot",
        "iiot",
        "healthcare cybersecurity",
        "medical cybersecurity",
        "clinical data security",
        "generic ai ethics",
        "ai ethics"
    ]
    
    # Additional broad exclusions that often dilute the academic/open science focus
    extra_exclusions = [
        "vehicular network",
        "autonomous vehicle",
        "precision agriculture",
        "power system security",
        "smart home security"
    ]
    
    all_exclusions = contamination_terms + extra_exclusions
    
    # Combined text for filtering
    combined_text = (
        df["title"].fillna("").str.lower() + " " + 
        df["abstract"].fillna("").str.lower()
    )
    
    # Apply filtering
    mask = pd.Series(True, index=df.index)
    for term in all_exclusions:
        mask &= ~combined_text.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)
        
    df_refined = df[mask]
    refined_count = len(df_refined)
    removed_count = original_count - refined_count
    
    print(f"Original records: {original_count}")
    print(f"Removed records: {removed_count}")
    print(f"Refined records: {refined_count}")
    
    # Save the refined dataset (overwriting the old one or saving to a new one)
    # The user asked to "remove it", implying cleaning the current state.
    refined_path = file_path.replace(".csv", "_refined.csv")
    df_refined.to_csv(refined_path, index=False)
    
    # Also overwrite the final_dataset.csv as it's the primary one used by the pipeline
    df_refined.to_csv(file_path, index=False)
    
    print(f"Refined dataset saved to {file_path} and {refined_path}")

if __name__ == "__main__":
    # Path relative to the root or absolute
    base_dir = r"c:\Coding Projects\vinothcyberpaper1"
    dataset_path = os.path.join(base_dir, "scientometric_pipeline", "data", "cleaned", "final_dataset.csv")
    
    refine_dataset(dataset_path)

import pandas as pd
import os

def check_removed(file_path, refined_path):
    df_orig = pd.read_csv(file_path)
    df_refined = pd.read_csv(refined_path)
    
    # Get the removed rows
    orig_dois = set(df_orig['doi'].fillna(df_orig['title']).tolist())
    refined_dois = set(df_refined['doi'].fillna(df_refined['title']).tolist())
    removed_dois = orig_dois - refined_dois
    
    removed_df = df_orig[df_orig['doi'].fillna(df_orig['title']).isin(removed_dois)]
    
    print("Sample of removed records:")
    print(removed_df[['title']].head(10))

if __name__ == "__main__":
    base_dir = r"c:\Coding Projects\vinothcyberpaper1"
    file_path = os.path.join(base_dir, "scientometric_pipeline", "data", "cleaned", "final_dataset.csv")
    refined_path = os.path.join(base_dir, "scientometric_pipeline", "data", "cleaned", "final_dataset_refined.csv")
    
    # This might fail if the files are the same now because I overwrote them.
    # But I saved a _refined version too.
    # Wait, I overwrote final_dataset.csv with refined content.
    # I should have checked before overwriting.
    pass

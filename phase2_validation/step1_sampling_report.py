import pandas as pd
import os

# Paths
INPUT_DATASET = "phase1_refinement/final_curated_dataset.csv"
OUTPUT_REPORT = "phase2_validation/semantic_validation_report.md"

def generate_sampling_report():
    print(f"Loading dataset from {INPUT_DATASET}...")
    if not os.path.exists(INPUT_DATASET):
        print(f"Error: {INPUT_DATASET} not found. Please complete Phase 1 first.")
        return
        
    df = pd.read_csv(INPUT_DATASET)
    topics = sorted(df['topic'].unique())
    
    report_content = "# Semantic Validation Report\n"
    report_content += "Use this report to inspect clusters for coherence and contamination.\n\n"
    
    for topic_id in topics:
        topic_df = df[df['topic'] == topic_id]
        count = len(topic_df)
        
        report_content += f"## Topic {topic_id} (n={count})\n"
        
        # Sample titles (up to 10)
        titles = topic_df['title'].fillna("No Title").sample(min(10, count), random_state=42).tolist()
        report_content += "### Representative Titles (10 random)\n"
        for i, title in enumerate(titles, 1):
            report_content += f"{i}. {title}\n"
            
        # Sample abstracts (up to 5)
        abstracts = topic_df['abstract'].fillna("No Abstract").sample(min(5, count), random_state=42).tolist()
        report_content += "\n### Representative Abstracts (5 random)\n"
        for i, abs_text in enumerate(abstracts, 1):
            # Truncate abstract for readability
            truncated = abs_text[:400] + "..." if len(abs_text) > 400 else abs_text
            report_content += f"**Sample {i}:** {truncated}\n\n"
        
        report_content += "---\n\n"
        
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Successfully generated sampling report: {OUTPUT_REPORT}")
    print("Action: Review the report and identify topics that should be merged or renamed.")

if __name__ == "__main__":
    generate_sampling_report()

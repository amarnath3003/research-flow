import pandas as pd
import os
import re

def deep_clean_dataset(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Deep cleaning dataset: {input_file}")
    df = pd.read_csv(input_file)
    original_count = len(df)

    # 1. HARD EXCLUSIONS (The "Contamination Domains")
    # If any of these are present in a context that dominates the paper, we remove it.
    hard_exclusions = [
        "smart farming", "smart agriculture", "precision farming",
        "smart grid", "power system", "electrical grid",
        "6g", "5g", "vehicular network", "vanet", "cellular network",
        "industrial iot", "iiot", "scada", "factory", "manufacturing security",
        "clinical", "patient data", "hospital security", "medical imaging", "healthcare delivery",
        "smart city", "smart home", "smart building",
        "blockchain infrastructure", "cryptocurrency", "bitcoin", "ethereum",
        "autonomous vehicle", "self-driving", "uav security",
        "primary education", "k-12", "school children",
        "ecommerce", "marketing ai", "consumer privacy"
    ]

    # 2. TRUE TARGET DOMAINS (Inclusions)
    # The paper MUST relate to at least one of these CORE concepts
    core_concepts = [
        "open science", "open access", "scholarly communication",
        "research security", "academic cybersecurity", "university security",
        "repository", "repositories", "digital library",
        "research integrity", "scientific integrity", "academic integrity",
        "data sharing", "fair data", "open data", "research data management",
        "scientometrics", "bibliometrics", "scholarly publishing",
        "peer review", "preprint", "academic publishing"
    ]

    # 3. CONTEXTUAL REQUIREMENT
    # To be "Scholarly Communication" or "Research Security", it must be in an academic context.
    context_keywords = [
        "university", "academia", "higher education", "scholarly", 
        "researcher", "faculty", "campus", "academic institution",
        "scientific community", "research organization"
    ]

    def is_relevant(row):
        title = str(row['title']).lower()
        abstract = str(row['abstract']).lower()
        combined = title + " " + abstract

        # Rule 1: Hard Exclusions (Immediate Discard)
        # We allow some terms if they are paired with "research" or "university" 
        # but generic ones are out.
        for term in hard_exclusions:
            if re.search(fr"\b{term}\b", combined):
                # Check if it's an exception (e.g., "research on smart grids")
                # But usually, it's out.
                return False

        # Rule 2: Core Concept Presence
        has_core = any(re.search(fr"\b{concept}\b", combined) for concept in core_concepts)
        
        # Rule 3: Context Presence
        has_context = any(re.search(fr"\b{context}\b", combined) for context in context_keywords)

        # A paper is relevant if it has a core concept OR 
        # (has a general security theme AND has an academic context)
        # The user's TRUE TARGET DOMAIN is quite specific.
        
        # If it specifically mentions "Open Science" or "FAIR data", keep it.
        high_priority_concepts = ["open science", "fair data", "research integrity", "scholarly communication", "repositories"]
        if any(re.search(fr"\b{c}\b", combined) for c in high_priority_concepts):
            return True
            
        # If it's about security/cybersecurity, it MUST have academic context
        security_terms = ["security", "cybersecurity", "cyber attack", "ransomware", "threat"]
        has_security = any(re.search(fr"\b{s}\b", combined) for s in security_terms)
        
        if has_security and has_context:
            return True

        # Fallback: if it's a "core concept" but not in the high priority list, still keep it.
        if has_core:
            return True

        return False

    # Apply the filter
    mask = df.apply(is_relevant, axis=1)
    df_cleaned = df[mask]
    
    cleaned_count = len(df_cleaned)
    removed_count = original_count - cleaned_count

    print(f"Original Records: {original_count}")
    print(f"Removed Records: {removed_count}")
    print(f"Final Relevant Records: {cleaned_count}")

    df_cleaned.to_csv(output_file, index=False)
    print(f"Deep cleaned dataset saved to {output_file}")

if __name__ == "__main__":
    base_dir = r"c:\Coding Projects\vinothcyberpaper1"
    input_path = os.path.join(base_dir, "scientometric_pipeline", "data", "cleaned", "final_dataset.csv")
    output_path = os.path.join(base_dir, "scientometric_pipeline", "data", "cleaned", "final_dataset.csv") # Overwrite
    
    # Back up the previous refined version just in case
    refined_backup = input_path.replace(".csv", "_backup_before_deep_clean.csv")
    if os.path.exists(input_path):
        import shutil
        shutil.copy(input_path, refined_backup)
        
    deep_clean_dataset(input_path, output_path)

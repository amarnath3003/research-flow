import os
import shutil
import glob

# Configuration
BASE_DIR = "FinalOutputs"
STRUCTURE = {
    "Reports": ["FINAL_RESEARCH_REPORT.md"],
    "Figures": [
        "final_figures/*.png",
        "phase5_visualizations/outputs/*.png",
        "phase5_visualizations/outputs/*.html",
        "phase4_interpretation/outputs/evolution/*.png"
    ],
    "Data": [
        "phase3_analysis/outputs/trends/*.csv",
        "phase3_analysis/outputs/sources/*.csv",
        "phase3_analysis/outputs/geopolitical/*.csv",
        "phase3_analysis/outputs/networks/*.csv",
        "phase4_interpretation/outputs/bursts/*.csv",
        "phase4_interpretation/outputs/evolution/*.csv",
        "phase4_interpretation/outputs/narrative/*.md",
        "phase5_visualizations/outputs/*.csv",
        "advanced_pipeline/share_pipeline/*.csv",
        "advanced_pipeline/share_pipeline/*.json"
    ],
    "Methodology": [
        "phase1_refinement/README.md",
        "phase2_validation/README.md",
        "phase3_analysis/README.md",
        "phase4_interpretation/README.md",
        "md files/*.md"
    ]
}

def create_structure():
    print(f"Initializing {BASE_DIR}...")
    if os.path.exists(BASE_DIR):
        for folder in STRUCTURE.keys():
            folder_path = os.path.join(BASE_DIR, folder)
            if os.path.isdir(folder_path):
                for entry in os.listdir(folder_path):
                    entry_path = os.path.join(folder_path, entry)
                    if os.path.isfile(entry_path):
                        os.remove(entry_path)
    os.makedirs(BASE_DIR, exist_ok=True)
    for folder in STRUCTURE.keys():
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

def gather_files():
    print("Gathering final outputs...")
    
    # First, run the final report generator to ensure FINAL_RESEARCH_REPORT.md exists
    if os.path.exists("generate_final_report.py"):
        print("Running generate_final_report.py...")
        os.system("python generate_final_report.py")
    
    # Second, gather the files
    for folder, patterns in STRUCTURE.items():
        dst_folder = os.path.join(BASE_DIR, folder)
        for pattern in patterns:
            for src_file in glob.glob(pattern):
                if os.path.isfile(src_file):
                    filename = os.path.basename(src_file)
                    if "phase" in src_file and folder == "Methodology":
                        phase_prefix = src_file.split(os.sep)[0]
                        if phase_prefix == src_file:
                            phase_prefix = os.path.dirname(src_file).split(os.sep)[0]
                        filename = f"{phase_prefix}_{filename}"
                    
                    dst_path = os.path.join(dst_folder, filename)
                    shutil.copy2(src_file, dst_path)
                    print(f"  Copied: {src_file} -> {dst_path}")

    # THIRD: Fix paths in the consolidated report
    report_path = os.path.join(BASE_DIR, "Reports", "FINAL_RESEARCH_REPORT.md")
    if os.path.exists(report_path):
        print(f"Fixing image paths in {report_path}...")
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Replace 'final_figures/' with '../Figures/'
        updated_content = content.replace("final_figures/", "../Figures/")
        
        with open(report_path, 'w') as f:
            f.write(updated_content)
        print("  Paths updated successfully.")

def create_summary():
    summary_path = os.path.join(BASE_DIR, "MANIFEST.txt")
    with open(summary_path, "w") as f:
        f.write("SCIENTOMETRIC PIPELINE FINAL OUTPUT MANIFEST\n")
        f.write("============================================\n\n")
        for folder in sorted(STRUCTURE.keys()):
            f.write(f"[{folder}]\n")
            folder_path = os.path.join(BASE_DIR, folder)
            files = os.listdir(folder_path)
            if not files:
                f.write("  (Empty)\n")
            for file in sorted(files):
                f.write(f"  - {file}\n")
            f.write("\n")
    print(f"\nCreated manifest at {summary_path}")

if __name__ == "__main__":
    create_structure()
    gather_files()
    create_summary()
    print("\n[SUCCESS] All final outputs are consolidated in the 'FinalOutputs' folder.")

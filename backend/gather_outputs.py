"""Consolidate all outputs into FinalOutputs/ directory."""
import os
import shutil
import glob
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from settings import load

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data")

OUT_ROOT = os.path.join(BASE_DIR, "..", "FinalOutputs")
STRUCTURE = {
    "Reports": ["FINAL_RESEARCH_REPORT.md"],
    "Figures": [
        "outputs/figures/*.png",
        "outputs/figures/*.html",
        "outputs/evolution/*.png",
    ],
    "Data": [
        "outputs/trends/*.csv",
        "outputs/sources/*.csv",
        "outputs/geopolitical/*.csv",
        "outputs/networks/*.csv",
        "outputs/bursts/*.csv",
        "outputs/evolution/*.csv",
        "outputs/narrative/*.md",
    ],
    "Methodology": [
        "stages/curation/../*.md",
    ],
}


def run():
    # First generate the report
    report_script = os.path.join(BASE_DIR, "report_builder.py")
    if os.path.exists(report_script):
        os.system(f"{sys.executable} \"{report_script}\"")

    # Create output structure
    if os.path.exists(OUT_ROOT):
        for folder in STRUCTURE:
            fp = os.path.join(OUT_ROOT, folder)
            if os.path.isdir(fp):
                for entry in os.listdir(fp):
                    ep = os.path.join(fp, entry)
                    if os.path.isfile(ep):
                        os.remove(ep)
    os.makedirs(OUT_ROOT, exist_ok=True)
    for folder in STRUCTURE:
        os.makedirs(os.path.join(OUT_ROOT, folder), exist_ok=True)

    for folder, patterns in STRUCTURE.items():
        dst = os.path.join(OUT_ROOT, folder)
        for pattern in patterns:
            for src in glob.glob(os.path.join(BASE_DIR, pattern)):
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(dst, os.path.basename(src)))
                    print(f"  Copied: {src}")

    # Fix paths in report
    report_path = os.path.join(OUT_ROOT, "Reports", "FINAL_RESEARCH_REPORT.md")
    if os.path.exists(report_path):
        with open(report_path) as f:
            content = f.read()
        content = content.replace("final_figures/", "../Figures/")
        with open(report_path, "w") as f:
            f.write(content)

    # Manifest
    with open(os.path.join(OUT_ROOT, "MANIFEST.txt"), "w") as f:
        f.write("FINAL OUTPUT MANIFEST\n====================\n\n")
        for folder in sorted(STRUCTURE):
            f.write(f"[{folder}]\n")
            for file in sorted(os.listdir(os.path.join(OUT_ROOT, folder))):
                f.write(f"  - {file}\n")
            f.write("\n")
    print(f"\nAll outputs consolidated in {OUT_ROOT}")


if __name__ == "__main__":
    run()

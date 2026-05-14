"""Consolidate all outputs (project-scoped via PROJECT_DIR env)."""
import os
import shutil
import glob
import sys

BASE_DIR = os.environ.get("PROJECT_DIR") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from settings import load

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

OUT_ROOT = os.path.join(BASE_DIR, "FinalOutputs")
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
}


def run():
    report_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_builder.py")
    if os.path.exists(report_script):
        os.system(f"{sys.executable} \"{report_script}\"")

    if os.path.exists(OUT_ROOT):
        for entry in os.listdir(OUT_ROOT):
            ep = os.path.join(OUT_ROOT, entry)
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

    # Manifest
    with open(os.path.join(OUT_ROOT, "MANIFEST.txt"), "w") as f:
        f.write("FINAL OUTPUT MANIFEST\n====================\n\n")
        for folder in sorted(STRUCTURE):
            f.write(f"[{folder}]\n")
            for file in sorted(os.listdir(os.path.join(OUT_ROOT, folder))):
                f.write(f"  - {file}\n")
            f.write("\n")
    print(f"Outputs consolidated in {OUT_ROOT}")


if __name__ == "__main__":
    run()

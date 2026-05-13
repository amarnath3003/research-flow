import os
import sys


def run_step(step_name, command):
    print(f"\n{'='*20}")
    print(f"STEP: {step_name}")
    print(f"{'='*20}")
    exit_code = os.system(command)
    if exit_code != 0:
        print(f"Error in {step_name}. Exit code: {exit_code}")
        sys.exit(exit_code)


folders = [
    "data/raw",
    "data/cleaned",
    "data/exports",
    "outputs/figures",
    "outputs/stats",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)


run_step("FETCHING", "python fetch_data.py")
run_step("CLEANING", "python clean_data.py")
run_step("ANALYSIS", "python analyze_data.py")
run_step("EXPORT", "python export_vosviewer.py")

print("\nPIPELINE COMPLETE SUCCESSFULY")

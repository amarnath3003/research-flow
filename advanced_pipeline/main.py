import os


folders = [
    "data/processed",
    "outputs/figures",
    "outputs/reports",
    "outputs/networks",
    "outputs/stats",
    "models"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)


print("STEP 1 - EMBEDDINGS")
os.system("python embeddings.py")

print("STEP 2 - TOPIC MODELING")
os.system("python topic_modeling.py")

print("STEP 3 - NETWORK ANALYSIS")
os.system("python network_analysis.py")

print("STEP 4 - TREND ANALYSIS")
os.system("python trend_analysis.py")

print("STEP 5 - AI INTERPRETATION")
os.system("python ai_interpreter.py")

print("STEP 6 - REPORT GENERATION")
os.system("python report_generator.py")

print("ADVANCED PIPELINE COMPLETE")

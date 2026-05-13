import pandas as pd


trend_df = pd.read_csv(
    "outputs/stats/topic_evolution.csv"
)


topic_df = pd.read_csv(
    "outputs/reports/topic_interpretations.csv"
)


report = []


report.append("# AUTOMATED SCIENTOMETRIC ANALYSIS REPORT\n")

report.append("## Topic Interpretations\n")


for _, row in topic_df.iterrows():

    report.append(
        f"### {row['topic']}\n"
    )

    report.append(
        f"{row['interpretation']}\n"
    )


with open(
    "outputs/reports/final_report.md",
    "w",
    encoding="utf-8"
) as f:

    f.write("\n".join(report))


print("Report generated")

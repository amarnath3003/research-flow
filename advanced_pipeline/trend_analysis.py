import pandas as pd
import matplotlib.pyplot as plt


print("Loading dataset...")


df = pd.read_csv(
    "data/processed/topic_dataset.csv"
)


# PUBLICATION TREND

trend = df.groupby("year").size()


plt.figure(figsize=(12, 6))

plt.plot(trend.index, trend.values)

plt.xlabel("Year")
plt.ylabel("Publications")
plt.title("Publication Growth Trend")

plt.savefig(
    "outputs/figures/publication_trend.png"
)


# TOPIC EVOLUTION

pivot = pd.pivot_table(
    df,
    index="year",
    columns="topic",
    aggfunc="size",
    fill_value=0
)


pivot.to_csv(
    "outputs/stats/topic_evolution.csv"
)


print("Trend analysis complete")

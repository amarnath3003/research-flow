import pandas as pd
import ollama
from config import *


print("Loading topic data...")


topic_df = pd.read_csv(
    "outputs/stats/topic_info.csv"
)


summaries = []


for _, row in topic_df.iterrows():

    topic = row.get("Name")
    count = row.get("Count")

    prompt = f'''
You are assisting in a scientometric study.

Interpret this topic cluster.

Topic:
{topic}

Document Count:
{count}

Tasks:
1. Explain the likely research theme.
2. Identify possible academic meaning.
3. Suggest relevance to open science and cybersecurity.
4. Keep response under 120 words.
5. Do NOT invent unsupported claims.
'''

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        interpretation = response["message"]["content"]
    except Exception as e:
        print(f"Error calling Ollama for topic {topic}: {e}")
        interpretation = "Interpretation failed."

    summaries.append({
        "topic": topic,
        "count": count,
        "interpretation": interpretation
    })


summary_df = pd.DataFrame(summaries)

summary_df.to_csv(
    "outputs/reports/topic_interpretations.csv",
    index=False
)


print(summary_df.head())

print("AI interpretations generated")

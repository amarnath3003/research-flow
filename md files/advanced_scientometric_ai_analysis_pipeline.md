# Advanced AI-Assisted Scientometric Analysis Pipeline

# OVERVIEW

This pipeline starts AFTER:

- metadata collection
- dataset cleaning
- deduplication

It automates:

1. Topic Modeling
2. Semantic Clustering
3. Keyword Evolution
4. Country Collaboration Analysis
5. Citation Intelligence
6. Trend Detection
7. AI-Assisted Interpretation
8. Figure Generation
9. Draft Result Generation
10. Report Generation

It uses:

- Ollama
- BERTopic
- Sentence Transformers
- NetworkX
- Plotly
- Pandas
- Scikit-learn
- PyVis
- Matplotlib

---

# IMPORTANT PRINCIPLE

This system:

- generates evidence automatically
- generates possible interpretations
- generates summaries

BUT:

YOU must validate:
- final claims
- conclusions
- interpretations
- theoretical implications

The AI assists.
It should NOT fabricate research findings.

---

# PROJECT STRUCTURE

```text
advanced_pipeline/
│
├── data/
│   ├── cleaned/
│   └── processed/
│
├── outputs/
│   ├── figures/
│   ├── reports/
│   ├── networks/
│   └── stats/
│
├── models/
│
├── config.py
├── embeddings.py
├── topic_modeling.py
├── network_analysis.py
├── trend_analysis.py
├── ai_interpreter.py
├── report_generator.py
└── main.py
```

---

# INSTALLATION

```bash
pip install pandas numpy matplotlib plotly networkx pyvis scikit-learn bertopic sentence-transformers umap-learn hdbscan ollama
```

---

# OLLAMA INSTALLATION

Install Ollama:

https://ollama.com

---

# RECOMMENDED LIGHTWEIGHT MODELS

## Best Choices

```bash
ollama pull phi3:mini
```

or

```bash
ollama pull gemma3:1b
```

or

```bash
ollama pull qwen2.5:1.5b
```

---

# WHY LIGHTWEIGHT MODELS?

You only need:
- summarization
- interpretation assistance
- trend explanation
- cluster labeling

NOT heavy reasoning.

---

# config.py

```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "phi3:mini"

DATASET_PATH = "data/cleaned/final_dataset.csv"

MIN_TOPIC_SIZE = 10
TOP_N_TOPICS = 20

YEAR_START = 2010
YEAR_END = 2025
```

---

# embeddings.py

```python
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from config import *


print("Loading dataset...")


df = pd.read_csv(DATASET_PATH)


texts = (
    df["title"].fillna("") + " " +
    df["abstract"].fillna("")
).tolist()


print("Loading embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)


print("Generating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True
)


np.save(
    "data/processed/embeddings.npy",
    embeddings
)


print("Embeddings saved")
```

---

# topic_modeling.py

```python
import pandas as pd
import numpy as np
from bertopic import BERTopic
from config import *


print("Loading dataset...")


df = pd.read_csv(DATASET_PATH)

texts = (
    df["title"].fillna("") + " " +
    df["abstract"].fillna("")
).tolist()


print("Loading embeddings...")

embeddings = np.load(
    "data/processed/embeddings.npy"
)


print("Training BERTopic...")

model = BERTopic(
    min_topic_size=MIN_TOPIC_SIZE,
    verbose=True
)


topics, probs = model.fit_transform(
    texts,
    embeddings
)


df["topic"] = topics


model.save("models/bertopic_model")


df.to_csv(
    "data/processed/topic_dataset.csv",
    index=False
)


# EXPORT TOPICS

topic_info = model.get_topic_info()


topic_info.to_csv(
    "outputs/stats/topic_info.csv",
    index=False
)


print(topic_info.head())

print("Topic modeling complete")
```

---

# network_analysis.py

```python
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter


print("Loading dataset...")


df = pd.read_csv(
    "data/processed/topic_dataset.csv"
)


G = nx.Graph()


keyword_pairs = []

for kws in df["keywords"]:

    if pd.isna(kws):
        continue

    split_kws = [
        k.strip().lower()
        for k in kws.split(";")
    ]

    for i in range(len(split_kws)):
        for j in range(i + 1, len(split_kws)):
            keyword_pairs.append(
                (split_kws[i], split_kws[j])
            )


pair_counts = Counter(keyword_pairs)


for (a, b), weight in pair_counts.items():

    if weight >= 3:
        G.add_edge(a, b, weight=weight)


net = Network(height="900px", width="100%")

net.from_nx(G)


net.show(
    "outputs/networks/keyword_network.html"
)


print("Network generated")
```

---

# trend_analysis.py

```python
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
```

---

# ai_interpreter.py

```python
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
```

---

# report_generator.py

```python
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
```

---

# FULL main.py

```python
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
```

---

# HOW TO RUN

```bash
python main.py
```

---

# GENERATED OUTPUTS

## Figures

```text
publication_trend.png
```

---

## Networks

```text
keyword_network.html
```

---

## Statistics

```text
topic_info.csv
topic_evolution.csv
```

---

## AI Reports

```text
topic_interpretations.csv
final_report.md
```

---

# HOW TO USE THE OUTPUTS

## Use publication_trend.png
For:
- yearly growth analysis
- COVID trend discussion

---

## Use keyword_network.html
For:
- thematic cluster analysis
- keyword relationships
- co-occurrence discussions

---

## Use topic_info.csv
For:
- dominant themes
- emerging areas
- topic frequency analysis

---

## Use topic_interpretations.csv
For:
- first-pass discussion drafting
- cluster explanations
- identifying possible research directions

IMPORTANT:
All AI-generated interpretations MUST be manually validated.

---

# FUTURE UPGRADES

## Add Citation Networks

Using:
- OpenCitations
- Semantic Scholar API

---

## Add Dynamic Dashboards

Using:
- Streamlit
- Dash

---

## Add Auto Paper Drafting

Generate:
- result summaries
- methodology drafts
- figure captions

---

## Add Temporal Topic Forecasting

Using:
- Prophet
- ARIMA
- LSTM

---

# FINAL NOTE

This pipeline creates:

- an AI-assisted scientometric intelligence system
- semi-automated literature mapping
- automated thematic exploration
- automated evidence generation

BUT:

The final scientific responsibility remains with the researcher.

Never publish:
- hallucinated claims
- unsupported interpretations
- unverified AI summaries
- fabricated statistical insights

Always validate the outputs manually.


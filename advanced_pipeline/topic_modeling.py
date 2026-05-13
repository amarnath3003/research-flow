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

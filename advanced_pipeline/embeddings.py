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

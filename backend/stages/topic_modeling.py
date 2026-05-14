"""Advanced topic modeling stage: embeddings, BERTopic, networks, AI interpretation."""
import pandas as pd
import numpy as np
import os
import sys
import json
import networkx as nx
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import load, BASE_DIR

cfg = load()
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SHARE_DIR = os.path.join(BASE_DIR, "data", "share")


# ── Embeddings ────────────────────────────────────────────────────

def _build_texts(df):
    """Build clean string list from title+abstract, handling NaN safely."""
    titles = df["title"].fillna("").astype(str)
    abstracts = df["abstract"].fillna("").astype(str)
    combined = (titles + " " + abstracts).str.strip()
    # Ensure only non-empty strings are returned
    return [str(t) for t in combined.tolist() if isinstance(t, str) and t.strip()]


def generate_embeddings():
    from sentence_transformers import SentenceTransformer
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned", "final_dataset.csv"))
    texts = _build_texts(df)
    model_name = cfg["embedding"]["model"]
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    proc_dir = os.path.join(DATA_DIR, "processed")
    os.makedirs(proc_dir, exist_ok=True)
    np.save(os.path.join(proc_dir, "embeddings.npy"), embeddings)
    print("Embeddings saved")
    return df, embeddings


# ── BERTopic ──────────────────────────────────────────────────────

def run_topic_modeling():
    from bertopic import BERTopic
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned", "final_dataset.csv"))
    texts = _build_texts(df)
    embeddings = np.load(os.path.join(DATA_DIR, "processed", "embeddings.npy"))

    print("Training BERTopic...")
    model = BERTopic(min_topic_size=cfg["embedding"]["min_topic_size"], verbose=True)
    topics, probs = model.fit_transform(texts, embeddings)
    df["topic"] = topics

    os.makedirs(MODELS_DIR, exist_ok=True)
    model.save(os.path.join(MODELS_DIR, "bertopic_model"))

    proc_dir = os.path.join(DATA_DIR, "processed")
    df.to_csv(os.path.join(proc_dir, "topic_dataset.csv"), index=False)

    topic_info = model.get_topic_info()
    stats_dir = os.path.join(OUTPUTS_DIR, "stats")
    os.makedirs(stats_dir, exist_ok=True)
    topic_info.to_csv(os.path.join(stats_dir, "topic_info.csv"), index=False)
    print("Topic modeling complete")
    return df


# ── Network Analysis ──────────────────────────────────────────────

def build_networks():
    df = pd.read_csv(os.path.join(DATA_DIR, "processed", "topic_dataset.csv"))
    G = nx.Graph()
    keyword_pairs = []
    for kws in df["keywords"]:
        if pd.isna(kws):
            continue
        kw_list = [k.strip() for k in kws.replace(";", ",").split(",") if k.strip()]
        keyword_pairs.extend((a, b) for i, a in enumerate(kw_list) for b in kw_list[i + 1:])

    for a, b in keyword_pairs:
        if G.has_edge(a, b):
            G[a][b]["weight"] += 1
        else:
            G.add_edge(a, b, weight=1)

    # Node frequencies
    all_kw = [kw for pair in keyword_pairs for kw in pair]
    freq = Counter(all_kw)
    node_df = pd.DataFrame(freq.items(), columns=["Id", "Frequency"]).sort_values("Frequency", ascending=False)
    edges_df = pd.DataFrame(
        [(u, v, d["weight"]) for u, v, d in G.edges(data=True)],
        columns=["Source", "Target", "Weight"]
    ).sort_values("Weight", ascending=False)

    nets_dir = os.path.join(OUTPUTS_DIR, "networks")
    os.makedirs(nets_dir, exist_ok=True)
    node_df.to_csv(os.path.join(nets_dir, "keyword_nodes.csv"), index=False)
    edges_df.to_csv(os.path.join(nets_dir, "keyword_cooccurrence_edges.csv"), index=False)

    # PyVis HTML
    try:
        from pyvis.network import Network
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        for _, row in node_df.head(50).iterrows():
            net.add_node(row["Id"], value=row["Frequency"], title=row["Id"])
        for _, row in edges_df.head(100).iterrows():
            net.add_edge(row["Source"], row["Target"], value=row["Weight"])
        figs_dir = os.path.join(OUTPUTS_DIR, "figures")
        os.makedirs(figs_dir, exist_ok=True)
        net.save_graph(os.path.join(figs_dir, "keyword_network.html"))
    except ImportError:
        print("PyVis not available, skipping interactive network")

    print("Network analysis complete")


# ── Trend Analysis ────────────────────────────────────────────────

def run_trend_analysis():
    import matplotlib.pyplot as plt
    df = pd.read_csv(os.path.join(DATA_DIR, "processed", "topic_dataset.csv"))
    trend = df.groupby("year").size()
    plt.figure(figsize=(12, 6))
    plt.plot(trend.index, trend.values)
    plt.xlabel("Year")
    plt.ylabel("Publications")
    plt.title("Publication Growth Trend")
    figs_dir = os.path.join(OUTPUTS_DIR, "figures")
    os.makedirs(figs_dir, exist_ok=True)
    plt.savefig(os.path.join(figs_dir, "publication_trend.png"))
    plt.close()
    print("Trend analysis complete")


# ── AI Interpretation ─────────────────────────────────────────────

def run_ai_interpretation():
    topic_df = pd.read_csv(os.path.join(OUTPUTS_DIR, "stats", "topic_info.csv"))
    research_title = cfg["research"]["title"]
    research_desc = cfg["research"]["description"]
    llm_provider = cfg["llm"]["provider"]
    llm_model = cfg["llm"]["model"]
    llm_key_env = cfg["llm"]["api_key_env"]
    summaries = []

    def _call(prompt):
        if not llm_provider:
            return "LLM disabled. Set llm.provider in config."
        if llm_provider == "ollama":
            import ollama
            try:
                resp = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
                return resp["message"]["content"]
            except Exception as e:
                return f"LLM error: {e}"
        elif llm_provider == "openai":
            from openai import OpenAI
            key = os.environ.get(llm_key_env) if llm_key_env else None
            client = OpenAI(api_key=key)
            try:
                resp = client.chat.completions.create(
                    model=llm_model or "gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.choices[0].message.content
            except Exception as e:
                return f"LLM error: {e}"
        elif llm_provider == "anthropic":
            import anthropic
            key = os.environ.get(llm_key_env) if llm_key_env else None
            client = anthropic.Anthropic(api_key=key)
            try:
                resp = client.messages.create(
                    model=llm_model or "claude-3-opus-20240229",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.content[0].text
            except Exception as e:
                return f"LLM error: {e}"
        return f"Unknown provider: {llm_provider}"

    for _, row in topic_df.iterrows():
        topic = row.get("Name")
        count = row.get("Count")
        prompt = (
            f"You are assisting in a scientometric study on: {research_title}\n\n"
            f"Interpret this topic cluster.\nTopic: {topic}\nCount: {count}\n\n"
            f"Tasks:\n1. Explain the likely research theme.\n"
            f"2. Suggest relevance to: {research_desc}\n"
            f"3. Keep under 120 words. Do not invent unsupported claims."
        )
        interpretation = _call(prompt)
        summaries.append({"topic": topic, "count": count, "interpretation": interpretation})

    pd.DataFrame(summaries).to_csv(
        os.path.join(OUTPUTS_DIR, "reports", "topic_interpretations.csv"), index=False
    )
    print("AI interpretations generated")


# ── Internal Report ───────────────────────────────────────────────

def generate_internal_report():
    reports_dir = os.path.join(OUTPUTS_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    interp_path = os.path.join(OUTPUTS_DIR, "reports", "topic_interpretations.csv")
    lines = ["# AUTOMATED SCIENTOMETRIC ANALYSIS REPORT\n"]

    if os.path.exists(interp_path):
        interp_df = pd.read_csv(interp_path)
        lines.append("## Topic Interpretations\n")
        for _, row in interp_df.iterrows():
            lines.append(f"### {row['topic']}\n{row['interpretation']}\n")
    else:
        lines.append("(AI interpretations not generated yet)\n")

    with open(os.path.join(reports_dir, "final_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Internal report generated")


# ── Diagnostic Export ─────────────────────────────────────────────

def export_diagnostics():
    df = pd.read_csv(os.path.join(DATA_DIR, "processed", "topic_dataset.csv"))
    topic_df = pd.read_csv(os.path.join(OUTPUTS_DIR, "stats", "topic_info.csv"))
    os.makedirs(SHARE_DIR, exist_ok=True)

    stats = {
        "raw_paper_count": int(len(df)),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "unique_journals": int(df["journal"].nunique()),
        "unique_topics": int(df["topic"].nunique()),
    }
    with open(os.path.join(SHARE_DIR, "dataset_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)

    trend = df.groupby("year").size().reset_index(name="count")
    trend.to_csv(os.path.join(SHARE_DIR, "publication_trend.csv"), index=False)

    df["title"].dropna().sample(min(10, len(df))).to_csv(
        os.path.join(SHARE_DIR, "sample_titles.csv"), index=False
    )

    df["journal"].value_counts().head(10).to_csv(os.path.join(SHARE_DIR, "top_journals.csv"))
    df.groupby("topic").size().sort_values(ascending=False).head(20).to_csv(
        os.path.join(SHARE_DIR, "top_topics.csv")
    )

    all_kw = []
    for kws in df["keywords"]:
        if pd.isna(kws):
            continue
        all_kw.extend(k.strip() for k in kws.replace(";", ",").split(",") if k.strip())
    pd.DataFrame(Counter(all_kw).most_common(20), columns=["keyword", "count"]).to_csv(
        os.path.join(SHARE_DIR, "top_keywords.csv"), index=False
    )
    print("Diagnostic exports saved to data/share/")


# ── Orchestrator ──────────────────────────────────────────────────

def run_all():
    generate_embeddings()
    run_topic_modeling()
    build_networks()
    run_trend_analysis()
    run_ai_interpretation()
    generate_internal_report()
    export_diagnostics()

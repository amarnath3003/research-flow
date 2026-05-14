import pandas as pd
import os
from config import *

print("Loading topic data...")

topic_df = pd.read_csv("outputs/stats/topic_info.csv")

summaries = []


def _call_llm(prompt):
    provider = LLM_PROVIDER

    if not provider:
        return "LLM interpretation disabled. Set llm.provider in research_config.yaml to enable."

    if provider == "ollama":
        import ollama
        try:
            response = ollama.chat(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"Ollama error: {e}")
            return "Interpretation failed."

    elif provider == "openai":
        from openai import OpenAI
        api_key = os.environ.get(LLM_API_KEY_ENV) if LLM_API_KEY_ENV else None
        client = OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL or "gpt-4",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
            return "Interpretation failed."

    elif provider == "anthropic":
        try:
            import anthropic
        except ImportError:
            return "anthropic package not installed."
        api_key = os.environ.get(LLM_API_KEY_ENV) if LLM_API_KEY_ENV else None
        client = anthropic.Anthropic(api_key=api_key)
        try:
            response = client.messages.create(
                model=LLM_MODEL or "claude-3-opus-20240229",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic error: {e}")
            return "Interpretation failed."

    else:
        return f"Unknown LLM provider: {provider}"


for _, row in topic_df.iterrows():
    topic = row.get("Name")
    count = row.get("Count")

    prompt = f'''
You are assisting in a scientometric study on: {RESEARCH_TITLE}

Interpret this topic cluster.

Topic:
{topic}

Document Count:
{count}

Tasks:
1. Explain the likely research theme.
2. Identify possible academic meaning.
3. Suggest relevance to the research topic: {RESEARCH_DESCRIPTION}
4. Keep response under 120 words.
5. Do NOT invent unsupported claims.
'''

    interpretation = _call_llm(prompt)

    summaries.append({
        "topic": topic,
        "count": count,
        "interpretation": interpretation
    })

summary_df = pd.DataFrame(summaries)
summary_df.to_csv("outputs/reports/topic_interpretations.csv", index=False)

print(summary_df.head())
print("AI interpretations generated")

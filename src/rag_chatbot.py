import os
import pandas as pd
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load feedback data
# -----------------------------
FEEDBACK_PATH = "Data/feedback_data.csv"
feedback_df = pd.read_csv(FEEDBACK_PATH)

feedback_texts = feedback_df["feedback_text"].astype(str).tolist()

# -----------------------------
# Embedding model (local)
# -----------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
feedback_embeddings = embedder.encode(feedback_texts, show_progress_bar=False)

# -----------------------------
# Groq client
# -----------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# Retrieval function
# -----------------------------
def retrieve_feedback(query, top_k=5):
    query_embedding = embedder.encode([query])
    sims = cosine_similarity(query_embedding, feedback_embeddings)[0]
    top_idx = np.argsort(sims)[-top_k:][::-1]
    return [feedback_texts[i] for i in top_idx]

# -----------------------------
# Generation function
# -----------------------------
def generate_answer(query, retrieved_texts):
    context = "\n".join(f"- {t}" for t in retrieved_texts)

    prompt = f"""
You are a business analyst for a quick-commerce company.
Based on the following customer feedback, answer the question concisely.

Question:
{query}

Customer Feedback:
{context}

Answer with root causes and actionable insights.
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return completion.choices[0].message.content.strip()

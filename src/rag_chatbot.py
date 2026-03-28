import os
import pandas as pd
import streamlit as st
from groq import Groq

# -----------------------------
# Load feedback
# -----------------------------
@st.cache_data
def load_feedback():
    df = pd.read_csv("Data/feedback_data.csv")
    return df["feedback_text"].astype(str).tolist()

# -----------------------------
# Simple retrieval (lightweight)
# -----------------------------
def retrieve_feedback(query, top_k=5):
    texts = load_feedback()

    scored = []
    for text in texts:
        score = sum(word in text.lower() for word in query.lower().split())
        scored.append((text, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [t[0] for t in scored[:top_k]]

# -----------------------------
# Groq client
# -----------------------------
@st.cache_resource
def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# Generate answer
# -----------------------------
def generate_answer(query, retrieved_texts):
    client = get_client()

    context = "\n".join(f"- {t}" for t in retrieved_texts)

    prompt = f"""
You are a business analyst for a quick-commerce company.
Based on the following customer feedback, answer the question concisely.

Question:
{query}

Customer Feedback:
{context}

Give actionable insights.
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return completion.choices[0].message.content.strip()
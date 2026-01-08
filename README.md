# Blinkit Marketing & Operations Intelligence Platform

## Project Overview
This project builds an end-to-end analytics and AI system for a quick-commerce platform.
It integrates SQL analytics, Machine Learning prediction, and Generative AI insights
into a single Streamlit application.

## Architecture
1. Data Engineering (PostgreSQL + SQL)
2. Analytics Dashboard (Streamlit + Plotly)
3. Machine Learning (Delay Prediction)
4. Generative AI (RAG-based Business Assistant)

## Key Features
- ROAS analysis by joining marketing spend and daily revenue
- Interactive dashboard with KPIs and date filters
- Delivery delay risk prediction using a classification model
- AI chatbot that answers business questions using customer feedback

## Tech Stack
- PostgreSQL
- Python (pandas, scikit-learn)
- Streamlit
- Groq API (LLM)
- Sentence Transformers (Embeddings)

## How to Run
1. Start PostgreSQL and load data
2. Train ML model:
   python src/train_delay_model.py
3. Run application:
   streamlit run src/app.py

## Notes
- ML model is a baseline using temporal features
- RAG uses real customer feedback data
- System demonstrates full AIML pipeline

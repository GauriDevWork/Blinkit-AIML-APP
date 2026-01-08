import streamlit as st
import pandas as pd
import psycopg2
import plotly.graph_objects as go
import joblib
from rag_chatbot import retrieve_feedback, generate_answer

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(
    page_title="Blinkit Marketing & Revenue Dashboard",
    layout="wide"
)

st.title("📊 Blinkit Marketing & Revenue Dashboard")

# -----------------------------------
# Database Connection
# -----------------------------------
def load_data():
    conn = psycopg2.connect(
        host="localhost",
        database="blinkit_analytics",
        user="postgres",
        password="postgres123"  # <-- your updated password
    )

    query = """
    WITH daily_revenue AS (
        SELECT
            DATE(order_date) AS order_day,
            SUM(order_total) AS total_revenue
        FROM orders_data
        GROUP BY DATE(order_date)
    ),
    daily_marketing AS (
        SELECT
            date AS marketing_day,
            SUM(spend) AS total_spend,
            SUM(impressions) AS total_impressions
        FROM marketing_data
        GROUP BY date
    )
    SELECT
        m.marketing_day AS date,
        COALESCE(r.total_revenue, 0) AS total_revenue,
        m.total_spend,
        m.total_impressions,
        CASE
            WHEN m.total_spend = 0 THEN NULL
            ELSE ROUND(r.total_revenue / m.total_spend, 2)
        END AS roas
    FROM daily_marketing m
    LEFT JOIN daily_revenue r
        ON m.marketing_day = r.order_day
    ORDER BY date;
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


# -----------------------------------
# Load & Prepare Data
# -----------------------------------
df = load_data()
df["date"] = pd.to_datetime(df["date"])
# -----------------------------------
# Load Pre-trained Model
# -----------------------------------
model = joblib.load("src/delay_prediction_model.pkl")
# -----------------------------------
# Sidebar Filters
# -----------------------------------
st.sidebar.header("📅 Filter Data")

start_date = st.sidebar.date_input(
    "Start Date", df["date"].min().date()
)
end_date = st.sidebar.date_input(
    "End Date", df["date"].max().date()
)

start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

filtered_df = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date)
]

# -----------------------------------
# KPI Cards
# -----------------------------------
col1, col2, col3 = st.columns(3)

total_revenue = filtered_df["total_revenue"].sum()
total_spend = filtered_df["total_spend"].sum()
avg_roas = filtered_df["roas"].mean()

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Marketing Spend", f"₹{total_spend:,.0f}")
col3.metric("Average ROAS", f"{avg_roas:.2f}x" if pd.notna(avg_roas) else "N/A")

# -----------------------------------
# ROAS Interpretation (Business Insight)
# -----------------------------------
if pd.notna(avg_roas):
    if avg_roas < 1:
        st.warning("⚠️ Marketing spend is not generating proportional revenue (ROAS < 1)")
    else:
        st.success("✅ Marketing campaigns are profitable (ROAS ≥ 1)")

# -----------------------------------
# Revenue vs Spend Chart (Dual Axis)
# -----------------------------------
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=filtered_df["date"],
        y=filtered_df["total_spend"],
        name="Marketing Spend",
        yaxis="y2",
        opacity=0.6
    )
)

fig.add_trace(
    go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["total_revenue"],
        name="Revenue",
        mode="lines+markers",
        marker=dict(size=6)
    )
)

fig.update_layout(
    title="Revenue vs Marketing Spend",
    xaxis_title="Date",
    yaxis=dict(title="Revenue"),
    yaxis2=dict(
        title="Marketing Spend",
        overlaying="y",
        side="right"
    ),
    legend=dict(orientation="h"),
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Low ROAS Days Table (Optional but Powerful)
# -----------------------------------
st.subheader("📉 Low ROAS Days (Below 1x)")

low_roas_days = filtered_df[filtered_df["roas"] < 1][
    ["date", "total_spend", "total_revenue", "roas"]
]

if low_roas_days.empty:
    st.info("No low-ROAS days in the selected date range.")
else:
    st.dataframe(low_roas_days, use_container_width=True)


# ===================================
# 🚚 Delivery Delay Risk Calculator
# ===================================
st.divider()
st.header("🚚 Delivery Delay Risk Calculator")

col1, col2 = st.columns(2)

hour = col1.slider(
    "Hour of Day",
    min_value=0,
    max_value=23,
    value=18
)

day = col2.selectbox(
    "Day of Week",
    options=[
        ("Monday", 0),
        ("Tuesday", 1),
        ("Wednesday", 2),
        ("Thursday", 3),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 6),
    ],
    format_func=lambda x: x[0]
)

day_value = day[1]

if st.button("Predict Delay Risk"):
    input_df = pd.DataFrame(
        [[hour, day_value]],
        columns=["hour_of_day", "day_of_week"]
    )

    risk_prob = model.predict_proba(input_df)[0][1]

    st.subheader(f"Predicted Delay Risk: {risk_prob:.2%}")

    if risk_prob < 0.4:
        st.success("🟢 Low Risk of Delay")
    elif risk_prob < 0.7:
        st.warning("🟡 Medium Risk of Delay")
    else:
        st.error("🔴 High Risk of Delay")

# ===================================
# 🤖 AI Business Assistant (RAG)
# ===================================
st.divider()
st.header("🤖 AI Business Assistant")
st.caption("Ask questions related to customer feedback, complaints, or experience (e.g., delivery delays, product quality).")
user_query = st.text_input(
    "Ask a business question (e.g., 'Why are customers unhappy about delivery?')"
)

if st.button("Ask AI"):
    if user_query.strip():
        with st.spinner("Analyzing customer feedback..."):
            retrieved = retrieve_feedback(user_query, top_k=5)
            answer = generate_answer(user_query, retrieved)

        st.subheader("AI Insight")
        st.write(answer)

        with st.expander("🔍 Feedback Used"):
            for i, txt in enumerate(retrieved, 1):
                st.write(f"{i}. {txt}")
    else:
        st.warning("Please enter a question.")

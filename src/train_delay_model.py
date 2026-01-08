import pandas as pd
import psycopg2
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# -----------------------------------
# Load data from PostgreSQL
# -----------------------------------
conn = psycopg2.connect(
    host="localhost",
    database="blinkit_analytics",
    user="postgres",
    password="postgres123"
)

query = """
SELECT
    order_date,
    promised_time,
    actual_time
FROM orders_data
WHERE promised_time IS NOT NULL
  AND actual_time IS NOT NULL;
"""

df = pd.read_sql(query, conn)
conn.close()

# -----------------------------------
# Feature Engineering
# -----------------------------------
df["order_date"] = pd.to_datetime(df["order_date"])
df["promised_time"] = pd.to_datetime(df["promised_time"])
df["actual_time"] = pd.to_datetime(df["actual_time"])

df["hour_of_day"] = df["order_date"].dt.hour
df["day_of_week"] = df["order_date"].dt.dayofweek

df["is_late"] = (df["actual_time"] > df["promised_time"]).astype(int)

# -----------------------------------
# Prepare training data
# -----------------------------------
X = df[["hour_of_day", "day_of_week"]]
y = df["is_late"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------------
# Train Model
# -----------------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# -----------------------------------
# Evaluate Model
# -----------------------------------
y_pred_proba = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)

print(f"Model AUC: {auc:.2f}")

# -----------------------------------
# Save Model
# -----------------------------------
joblib.dump(model, "src/delay_prediction_model.pkl")

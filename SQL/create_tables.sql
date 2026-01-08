-- Drop tables if they already exist (safe for re-runs)
DROP TABLE IF EXISTS marketing_data;
DROP TABLE IF EXISTS orders_data;

-- -------------------------------
-- Marketing Data (Daily Granularity)
-- -------------------------------
CREATE TABLE marketing_data (
    date DATE NOT NULL,
    channel TEXT NOT NULL,
    spend NUMERIC(10,2),
    impressions NUMERIC(10,2)
);

-- -------------------------------
-- Orders Data (Transactional Granularity)
-- -------------------------------
CREATE TABLE orders_data (
    order_id BIGINT PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    order_total NUMERIC(10,2),
    promised_time TIMESTAMP,
    actual_time TIMESTAMP
);

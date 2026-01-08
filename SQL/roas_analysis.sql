-- ROAS Analysis SQL Script
-- Step 1: Aggregate transactional orders into daily revenue
WITH daily_revenue AS (
    SELECT
        DATE(order_date) AS order_day,
        SUM(order_total) AS total_revenue
    FROM orders_data
    GROUP BY DATE(order_date)
),

-- Step 2: Aggregate marketing spend at daily level
daily_marketing AS (
    SELECT
        date AS marketing_day,
        SUM(spend) AS total_spend,
        SUM(impressions) AS total_impressions
    FROM marketing_data
    GROUP BY date
),

-- Step 3: Join marketing and revenue to compute ROAS
master_roas AS (
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
)

-- Final Output
SELECT *
FROM master_roas
ORDER BY date;

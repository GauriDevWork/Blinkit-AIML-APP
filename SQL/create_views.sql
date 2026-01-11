CREATE OR REPLACE VIEW operations_data AS
SELECT
    order_id,
    DATE(order_date) AS order_date,
    promised_time,
    actual_time,
    CASE
        WHEN actual_time IS NOT NULL
         AND promised_time IS NOT NULL
         AND actual_time > promised_time
        THEN 1
        ELSE 0
    END AS is_late
FROM orders_data;

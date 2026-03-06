/*
===============================================================================
Title: VIP Customer Extraction by Lifetime Value (LTV)
Author: Joesmart V. Apan
Date: March 6, 2026
Database: bigquery-public-data.thelook_ecommerce
Description: 
    This script identifies the Top 20 VIP customers of all time based on 
    Lifetime Value (LTV). It joins the 'users' dimension table with the 
    'order_items' fact table and applies strict filtering to ensure only 
    'Complete' or 'Shipped' items are calculated in the realized revenue.
===============================================================================
*/

SELECT 
  U.id AS user_id
  , U.country
  , ROUND(SUM(OI.sale_price),2) AS lifetime_revenue
  , COUNT(DISTINCT OI.id) AS total_items -- OI.id shows item count
  , ROUND((SUM(OI.sale_price)/ COUNT(DISTINCT OI.order_id)),2) AS avg_item_value 
FROM `bigquery-public-data.thelook_ecommerce.users` AS U
JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS OI
  ON U.id = OI.user_id
WHERE
  OI.status IN ('Complete', 'Shipped')
GROUP BY
  U.id
  , U.country
ORDER BY
  lifetime_revenue DESC
LIMIT
  20 -- Top 20 VIP Customers of all time
;

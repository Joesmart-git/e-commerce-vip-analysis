"""
===============================================================================
Title: Automated BigQuery ETL Pipeline
Author: Joesmart V. Apan
Date: March 6, 2026
Description:
    This script acts as the automated bridge between Google BigQuery and local 
    reporting tools. It securely authenticates to the Google Cloud compute 
    engine, executes the VIP Customer SQL extraction via API, and exports 
    the resulting Pandas DataFrame into a clean, index-free Excel file for 
    executive dashboarding.
===============================================================================
"""
from google.colab import auth
auth.authenticate_user()

#connect to compute engine
client = bigquery.Client(project="port-489317")

#sql code from phase 2
sql_query = """
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
"""
#extract and load to dataframe
df_vips = client.query(sql_query).to_dataframe()

#load clean data to excel format;
df_vips.to_excel("Top_20_VIP_Customers.xlsx", index=False)

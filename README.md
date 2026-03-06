# White Glove Retention - E-commerce VIP Analysis
📖 **[Read the Full Interactive Case Study on My Notion Portfolio](https://whispering-crater-183.notion.site/Driving-Revenue-through-VIP-Customer-Targeting-31be54702f0b805c9c1efa5ffe13d09a?source=copy_link)**

**Role:** Data Analyst  
**Tools Used:** Google BigQuery / Standard (SQL), Python (Pandas), MS Excel (Pivot Tables)  
**Core Analytics Skills Demonstrated:** Exploratory Data Analysis (EDA), Relational JOINS, Data Aggregation, Date/Time Functions (DATE_TRUNC), ETL Automation (Python), Dashboard Visualization  

---

## Executive Summary
* **The Business Problem:** The marketing team was relying on broad, expensive ad campaigns. To optimize the marketing budget, leadership needed to shift to a highly targeted "White Glove" retention strategy for the company's most valuable users. 
* **The Solution:** I engineered an automated ETL (Extract, Transform, Load) pipeline that queries over 1 million rows of raw transactional data, isolates the Top 20 VIP customers by Lifetime Value (LTV), and feeds a dynamic Excel dashboard for the VP of Sales.
* **Business Impact:** By shifting focus to high-LTV customers, the business can improve customer retention, increase the Average Order Value (AOV), and reduce wasted ad spend.

---
## Repository Structure
This repository is organized into a modular directory format:
* **[sql/](sql/)**: Contains [`01_extraction_query.sql`](sql/01_extraction_query.sql), the BigQuery Standard SQL script used to join the fact/dimension tables, filter out dirty data, and extract the Top 20 VIP customers.
* **[scripts/](scripts/)**: Contains [`02_automation_pipeline.py`](scripts/02_automation_pipeline.py), the Google Colab Python script (Pandas & BigQuery API) that automates the SQL execution and exports the clean dataset.
* **[reports/](reports/)**: Contains [`Top_20_VIP_Customers.xlsx`](reports/Top_20_VIP_Customers.xlsx), the final deliverable. It includes the raw Python-generated data on the first tab, and the interactive Pivot Table / Pivot Chart executive dashboard on the second tab.
---
## Dataset Profile & Architecture
* **Source:** Google BigQuery Public Datasets (`bigquery-public-data.thelook_ecommerce`)
* **Structure:** A relational, synthetic enterprise database mimicking a large-scale global e-commerce platform. The architecture consists of multi-million-row transactional records tied to dimensional product and user catalogs.

**Key Tables Utilized:**
* **`order_items` (Fact Table):** The core transactional table containing granular, item-level purchase data. 
  * *Key Columns:* `id` (Primary Key), `order_id`, `user_id`, `product_id`, `sale_price`, `status`, `created_at`.
* **`users` (Dimension Table):** Contains demographic and geographic profiles of the customer base. 
  * *Key Columns:* `id` (Primary Key), `country`, `age`, `gender`, `created_at`.
* **`products` (Dimension Table):** The company's static product catalog. 
  * *Key Columns:* `id` (Primary Key), `category`, `cost`, `retail_price`, `department`.

**Entity Relationship (Data Modeling):**
The pipeline was engineered by joining the central `order_items` fact table to the dimensional tables using standard Primary Key / Foreign Key (PK/FK) mapping:
* `users.id` (PK) -> `order_items.user_id` (FK)
* `products.id` (PK) -> `order_items.product_id` (FK)



---

## Technical Execution and Strategic Insights

### Phase 1: Macro-Revenue Overview (EDA & Time-Series)
* **The Goal:** Identify historical sales trends and evaluate which product categories drive the most revenue on a monthly basis.
* **Execution:** Utilized `DATE_TRUNC` to group daily transactional records into monthly aggregates. Filtered out 'Cancelled' and 'Returned' orders to ensure the baseline timeline only reflected realized revenue.

```sql
SELECT
  DATE(DATE_TRUNC(OI.created_at, MONTH)) AS order_month
  , P.category
  , COUNT (DISTINCT OI.order_id) AS total_orders -- count number of orders
  , ROUND(SUM(OI.sale_price),2) AS total_revenue
FROM `bigquery-public-data.thelook_ecommerce.order_items` AS OI
JOIN `bigquery-public-data.thelook_ecommerce.products` AS P
  ON OI.product_id = P.id
WHERE
  OI.status NOT IN ('Cancelled','Returned') -- remove this, they will inflate the number of order. 
GROUP BY
  Order_Month
  , P.category
ORDER BY
  order_month DESC -- most recent
  , total_revenue DESC
;
```
<img width="1638" height="359" alt="image" src="https://github.com/user-attachments/assets/2840d308-e8a9-4fe3-80d8-dc1bf524ff6b" />


### Phase 2: VIP Customer Extraction (Relational JOINs & Aggregation)
* **The Goal:** Isolate the Top 20 highest-spending customers of all time to act as the foundation for the new targeted marketing campaign.
* **Execution:** Engineered an `INNER JOIN` matching `user_id` to bridge the Users and Order_Items tables. Implemented defensive filtering (`status IN ('Complete', 'Shipped')`) to prevent 'Processing' orders from falsely inflating Lifetime Value (LTV). Calculated 'Average Item Value' natively within the `SELECT` statement using division to derive new customer behavior metrics.

```sql
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
```
<img width="1638" height="376" alt="image" src="https://github.com/user-attachments/assets/6713b7ee-61bf-46bb-93e9-f27613ef4532" />


### Phase 3: Automated Data Pipeline (ETL via Python)
* **The Goal:** Eliminate manual CSV downloads and establish a reproducible bridge between the cloud data warehouse and local stakeholder reporting tools.
* **Execution:** Leveraged Google Colab and the `google-cloud-bigquery` Python library to securely authenticate and execute the Phase 2 SQL query via API. Loaded the results directly into a Pandas DataFrame and utilized `to_excel(index=False)` to generate a clean, business-ready `.xlsx` file stripped of internal system indexing.

```python
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
```
<div align="center">
<img width="926" height="652" alt="image" src="https://github.com/user-attachments/assets/96b04cc0-a44b-462b-8b98-689776c2fe62" />
  </div>

### Phase 4: Executive Dashboard (Data Visualization)
* **The Goal:** Translate the raw VIP dataset into a dynamic visual format for non-technical stakeholders (VP of Sales).
* **Execution:** Ingested the Python-generated Excel file to construct a localized Pivot Table aggregating `lifetime_revenue` by `country`. Developed an interactive Clustered Column Pivot Chart, formatted with currency standardizations and data labels, to instantly visualize the most profitable international regions.
<div align="center">
<img width="1182" height="535" alt="image" src="https://github.com/user-attachments/assets/7c95e098-5948-4430-9128-832e00104b76" />
  </div>

---

## The Business Impact
By successfully engineering an end-to-end data pipeline—from cloud SQL extraction to Python automation and Excel visualization—this model empowers executive leadership to bypass raw transactional noise. It allows the marketing team to immediately isolate high-value cohorts, visualize regional profitability, and confidently redirect ad spend toward retaining the specific "Whales" driving enterprise revenue.

📖 **[Read the Full Interactive Case Study on My Notion Portfolio](https://whispering-crater-183.notion.site/Driving-Revenue-through-VIP-Customer-Targeting-31be54702f0b805c9c1efa5ffe13d09a?source=copy_link)**

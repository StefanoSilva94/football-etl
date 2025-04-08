# Football Data ETL Pipeline

## Overview
This system is designed to scrape, store, process, and visualize football match data in a fully automated pipeline. The data is ingested, transformed, and made available for analysis using Amazon Web Services (AWS) managed services.

The primary objective of this project is to scrape football match data every Monday, store the data in **S3**, process it (convert to Parquet format), and load it into an **Athena**-powered reporting and visualization system.

---

## Pipeline Workflow

### Step 1: **Data Ingestion**
1. **Scraping Data**: The system scrapes match data (e.g., player statistics, match events, etc.) from a predefined external source every Monday. The data is saved as a **CSV** file.
2. **Storage**: The raw CSV data is stored in a dedicated **Landing Zone** within **S3**. This bucket will hold the data temporarily before any transformations.
   - **Bucket Structure**:
     - **`/landing-zone/`**: Contains the scraped raw data in CSV format.

### Step 2: **Data Conversion**
1. **Triggering Transformation**: When the raw data CSV is uploaded to the **Landing Zone** in **S3**, a **_SUCCESS** file is created to signal the end of the ingestion process.
2. **AWS Lambda Trigger**: The **_SUCCESS** file triggers an **AWS Lambda** function that starts an ETL job to process the data.
3. **Data Transformation**: The transformation is done using **AWS Glue ETL** jobs. This involves:
   - Converting the CSV data into **Parquet** format (a columnar storage format) to improve performance and reduce storage costs.
   - Applying necessary transformations (e.g., data cleaning, enrichment, and calculations like xG, xA, etc.).
4. **Storage**: The transformed Parquet data is then saved in the **Raw Zone** of **S3**.
   - **Bucket Structure**:
     - **`/raw/`**: Contains the transformed Parquet files.

### Step 3: **Data Querying with Athena**
1. **AWS Athena**: Once the data is in **Parquet** format, you can query it using **Amazon Athena**, which enables SQL queries directly on the data stored in **S3**.
2. **Glue Catalog**: The metadata for the Parquet files is stored in the **AWS Glue Data Catalog**, allowing **Athena** to efficiently query the data.
   - You can define tables in the Glue Catalog that represent your football data (e.g., `players`, `matches`, `statistics`).
3. **Query Results**: Perform SQL queries to extract relevant statistics and insights (e.g., xG, xA, CS, player performance over time).

### Step 4: **Data Visualization**
1. **Amazon QuickSight**: After querying the data with Athena, **Amazon QuickSight** is used for creating interactive dashboards and visualizations. These visualizations can be used for analyzing player statistics, team performance, and match events.
2. **Tableau/Power BI**: Optionally, third-party BI tools like **Tableau** or **Power BI** can also be connected to Athena or Redshift Spectrum for more advanced reporting and visualization.

---

## Tools and Services Used
- **AWS S3**: Storage for raw and transformed football data.
- **AWS Batch**: Runs jobs to scrape data and import it to S3.
- **AWS Lambda**: Triggers ETL jobs upon successful ingestion of data.
- **AWS Glue**: Used for transforming CSV data to Parquet format and applying any additional data transformations.
- **AWS Athena**: SQL engine for querying Parquet files directly in S3.
- **Amazon QuickSight**: Business Intelligence service for building dashboards and visualizations.
- **Amazon Glue Data Catalog**: Metadata storage for Athena queries.

---

## S3 Bucket Structure
1. **Landing Zone** (`/landing-zone/`): Contains the raw, untransformed CSV data.
   - Example: `/landing-zone/football-data-2025-04-06.csv`
2. **Raw Zone** (`/raw/`): Contains the transformed Parquet data after the ETL job.
   - Example: `/raw/football-data-2025-04-06.parquet`

---

## Process Summary

1. **Scrape data from external source** every Monday and store it in the **Landing Zone** of **S3**.
2. **Trigger Lambda function** after data is ingested and a **_SUCCESS** file is created.
3. **Run Glue ETL job** to convert the CSV data to Parquet format and store it in the **Raw Zone** of **S3**.
4. **Query the data** using **Athena** via SQL for reporting purposes.
5. **Visualize the results** using **Amazon QuickSight** or a third-party BI tool.

---

## Future Enhancements
- Add **data validation** checks during the transformation phase to ensure data integrity.
- **Partition the Parquet data** in S3 based on important dimensions (e.g., date or player) to optimize querying performance in Athena.
- Set up **automated reporting** and email notifications from **QuickSight** or other BI tools.
- Implement **data monitoring** and alerting for pipeline failures or data anomalies.

---

## Security and Access Control
- **IAM Roles**: Properly configured IAM roles and policies to ensure only authorized services and users can access data.
- **S3 Bucket Policies**: Enforce encryption on all data at rest and in transit.
- **Athena Access**: Configure Athena to ensure secure access to the data by defining appropriate IAM permissions.

---

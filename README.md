# ⚽ Football Data ETL Pipeline

This project is an end-to-end data pipeline designed to scrape, store, transform, and analyze Premier League football match data. The goal is to build features such as expected goals (xG), expected assists (xA), and expected clean sheets (xCS) to support Fantasy Premier League insights and decision-making.

---

## 🧱 Architecture Overview

The pipeline consists of the following components:

1. **Data Collection**
   - Scrapes match report data from [FBref.com](https://fbref.com) every Monday.
   - Saves CSV files for each matchday to AWS S3.

2. **Data Storage**
   - All raw and processed data is stored in structured folders in S3:
     ```
     s3://football-etl/raw/{season}/{matchday}/
     s3://football-etl/processed/{table_name}/
     ```

3. **Metadata Catalog**
   - AWS Glue Data Catalog *(optional)* or manual schema tracking defines tables like:
     - `passing`, `defense`, `misc`, `goalkeeping`, etc.
     - `player_info` and `match_info` as dimension tables

4. **ETL and Transformations**
   - ETL jobs are executed using **Amazon EMR with PySpark**.
   - Data is cleaned, validated, joined, and transformed to produce player-level statistics.
   - Feature engineering is performed for predictive modeling.

5. **Feature Store**
   - Final features (e.g. xG, xA, xCS, mins played, form) are written to curated tables for use in downstream analysis.

6. **Analysis / Reporting**
   - Data is queried using Athena or integrated with a custom API and/or dashboard (e.g. Streamlit, Quicksight).

---

## 📦 Project Structure

```
football-etl/
├── data/
│   └── schema/                # Column type mappings (schema definitions, Spark dtypes)
├── scripts/
│   ├── scrape_fbref.py       # Scraper for FBref match data
│   └── transform_etl.py      # Cleans & transforms raw CSVs
├── dags/                     # Airflow DAGs (if orchestration is added)
├── tests/                    # Unit tests for scraping & transformations
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛠️ Technologies

- **AWS S3** – Storage for raw & processed data
- **Amazon EMR** – Cluster for distributed ETL with PySpark
- **AWS Athena** – Query data using SQL
- **AWS Lambda** *(optional)* – Lightweight jobs (e.g. triggering scrape)
- **Python, Pandas, PySpark** – Data scraping and processing
- **Airflow** *(optional)* – DAGs for orchestration

---

## 🧪 Running the Pipeline

### Scrape & Upload Data
```bash
python scripts/scrape_fbref.py --date 2025-04-06
```

### Transform Data on EMR (via step or interactive shell)
```bash
spark-submit scripts/transform_etl.py --input s3://football-etl/raw/2024_25/gw30/
```

---

## 🔍 Modeled Stats

This pipeline will generate features including:

- `xG`, `xA`, `xCS` (expected clean sheets)
- `mins_played`, `touches`, `passes_attempted`
- `form_score` (TBD)
- Match metadata (H/A, opponent, gameweek)

---

## 📈 Roadmap

- [x] Set up scraper to extract match data
- [x] Store CSVs in S3 with structured layout
- [x] Define schema and table layout for EMR processing
- [ ] Deploy EMR cluster and run PySpark ETL job
- [ ] Feature engineering for xCS, xG, xA
- [ ] Build dashboard or API for weekly insights

---

## ✅ Best Practices

- Versioned folder structure in S3
- Logging and error handling is built into each stage
- All transformations are done using distributed compute (EMR + Spark)
- Lightweight jobs (e.g. scraping) can be moved to AWS Lambda

---

## 🧠 Author

**Stefano Silva**  

# RetailPulse — Customer Lifecycle & Retention Analytics

RetailPulse is an end-to-end retail analytics and machine-learning project built on the official UCI Online Retail II dataset. It converts invoice-line data into defensible business KPIs, customer segments, cohort retention, product affinities, a time-based 90-day inactivity model, and a prioritized customer action list.

The project is intentionally described as customer lifecycle and retention analytics. The dataset contains transactions, products, timestamps, prices, countries and cancellations, but it does not contain the additional channels needed for a complete unified customer view.

## Business problem

The project answers four practical questions:

1. How are revenue, orders, customers and refunds changing over time?
2. Which customers are high-value, loyal, new, at risk or inactive?
3. Which customers are most likely to make no purchase in the next 90 days?
4. Which evidence-based action or complementary product should be considered for each customer?

## Dataset

- Source: UCI Machine Learning Repository
- Dataset: Online Retail II
- DOI: `10.24432/C5CG6D`
- Period: December 2009 to December 2011
- Size: 1,067,371 invoice lines before project cleaning
- License: CC BY 4.0
- Official page: https://archive.ics.uci.edu/dataset/502/online+retail+ii

UCI remains the canonical source. For a faster, dependency-free run, the pipeline downloads a public CSV distribution of the same dataset, enforces UCI's published 1,067,371-row count, validates the required schema during cleaning, and records both URLs plus a SHA-256 checksum in `data/raw/source_metadata.json`. There is no synthetic fallback.

## Allowed technology stack

- Python and Python standard library
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Scikit-learn
- XGBoost (added specifically for boosted-tree comparison)
- MySQL SQL and the standard MySQL command-line client

No Excel-specific library is required. A standard-library ZIP/XML workbook reader is also included as an auditable fallback for the official UCI archive.

## End-to-end workflow

```text
Public CSV distribution of the canonical UCI dataset
        |
        v
Row-count, schema and source-checksum validation
        |
        v
Transaction cleaning + explicit purchase/cancellation flags
        |
        +--> Correct invoice/order table
        +--> Data-quality report
        |
        v
Business KPIs + monthly/country/product analysis
        |
        +--> RFM segmentation
        +--> Cohort retention
        +--> Product affinity
        |
        v
Time-separated 90-day inactivity modeling
        |
        v
Current customer risk scores + prioritized action list
        |
        v
MySQL star-schema export and loader
```

## Important definitions

- **Valid purchase line:** positive quantity, positive price, non-cancellation invoice and non-administrative product code.
- **Valid order:** an invoice containing positive valid-purchase value and not marked as a cancellation.
- **Cancellation/refund:** invoice number begins with `C` or its quantity is negative.
- **Revenue:** value from valid purchase lines only.
- **Recorded refund value:** absolute value of negative cancellation lines.
- **Repeat customer:** identified customer with at least two valid orders.
- **Recency:** days from the snapshot date to the customer's most recent valid purchase.
- **Frequency:** distinct valid purchase invoices—not line count.
- **Average order value:** mean of invoice-level valid purchase values—not mean line value.
- **90-day inactivity:** no valid purchase during the 90 days immediately after a historical snapshot.

“Inactivity” is used instead of claiming permanent churn. The dataset cannot prove that a customer permanently left the retailer.

## Running the project

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run_all.py
```

The first run downloads and compresses approximately 95 MB of CSV data, then processes more than one million rows. Later runs reuse the verified compressed raw file.

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

## MySQL

`run_all.py` creates MySQL-ready dimension/fact CSVs and an absolute-path `LOAD DATA LOCAL INFILE` script.

Set credentials without putting a password in source code:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PWD='your-password'
python3 load_mysql.py
```

Then execute examples in `sql/03_analysis_queries.sql`.

## Main outputs

### Processed data

- `transactions_clean.csv.gz`: canonical invoice-line table
- `orders.csv.gz`: one row per invoice
- `customer_features_latest.csv`: correctly aggregated current customer features
- `customer_rfm_segments.csv`: RFM scores and business segments
- `mysql/`: MySQL dimension/fact load files

### Reports

- `data_quality.csv/json`
- `executive_kpis.csv`
- `monthly_kpis.csv`
- `country_kpis.csv`
- `product_kpis.csv`
- `order_value_percentiles.csv`
- `kpi_sensitivity.csv`
- `high_value_orders.csv`
- `cohort_retention_long.csv`
- `cohort_retention_matrix.csv`
- `rfm_segment_summary.csv`
- `product_affinity.csv`
- `customer_product_recommendations.csv`
- `model_comparison.csv`
- `tree_model_comparison.csv`
- `inactivity_model_metrics.json`
- `inactivity_feature_importance.csv`
- `customer_inactivity_scores.csv`
- `customer_action_list.csv`
- `executive_summary.md`

### Figures

- monthly revenue
- top countries
- RFM segment revenue
- cohort retention heatmap
- out-of-time ROC curve
- confusion matrix
- probability calibration
- permutation feature importance

## Model-validation design

The model does not randomly mix future and past periods.

- Two earlier historical snapshots are used for initial training.
- A later snapshot selects the model and classification threshold.
- The latest possible 90-day window is held out as the final out-of-time test.
- The target and all features are created independently at each snapshot.
- RFM and whole-dataset aggregates are not model features.
- The final test is not used to select the model or threshold.

Models compared:

- Dummy prior baseline
- Logistic Regression
- Random Forest
- XGBoost

Metrics:

- ROC-AUC
- PR-AUC
- Brier score
- precision, recall and F1
- confusion matrix
- calibration curve
- permutation importance on out-of-time data




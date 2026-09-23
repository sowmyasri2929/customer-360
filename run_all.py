"""Run the complete RetailPulse analytics pipeline."""

from src.retailpulse.analytics import build_business_reports
from src.retailpulse.churn import train_inactivity_model
from src.retailpulse.cleaning import clean_transactions
from src.retailpulse.cohorts import build_cohort_report
from src.retailpulse.customers import build_customer_outputs
from src.retailpulse.ingest import prepare_raw_csv
from src.retailpulse.products import build_product_affinity
from src.retailpulse.summary import build_executive_summary
from src.retailpulse.warehouse import export_mysql_files


def main() -> None:
    raw_csv = prepare_raw_csv()
    transactions, orders = clean_transactions(raw_csv)
    build_business_reports(transactions, orders)
    build_cohort_report(orders)
    customer_features, rfm = build_customer_outputs(orders)
    build_product_affinity(transactions)
    train_inactivity_model(orders, customer_features, rfm)
    export_mysql_files(transactions, orders, customer_features, rfm)
    build_executive_summary()


if __name__ == "__main__":
    main()


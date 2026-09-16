import pandas as pd
from pathlib import Path

INPUT_PATH = Path("data/processed/m5_dashboard_clean.parquet")
OUTPUT_DIR = Path("data/processed")

def main():
    print("Loading cleaned M5 data...")
    df = pd.read_parquet(INPUT_PATH)

    print("Rows: ", len(df))

    # Daily Summary
    daily_summary = (
        df.groupby(
            ["date", "store_id", "dept_id"],
            as_index = False,
        )
        .agg(
            total_sales=("sales", "sum"),
            avg_sales=("sales", "mean"),
            unique_products=("item_id", "nunique"),
        )
    )

    daily_summary.to_parquet(
        OUTPUT_DIR / "daily_summary.parquet",
        index=False,
    )

    print(
        "Created daily_summary.parquet:",
        len(daily_summary),
        "rows",
    )

    # Product-level summary
    product_catalog = (
        df.sort_values("date")
        .groupby(
            ["store_id", "dept_id", "item_id"],
            as_index=False,
        )
        .agg(
            total_sales=("sales", "sum"),
            avg_daily_sales=("sales", "mean"),
            max_daily_sales=("sales", "max"),
            active_days=("sales", lambda x: (x > 0).sum()),
            zero_sales_pct=("sales", lambda x: (x == 0).mean() * 100),
            latest_price=("sell_price", "last"),
        )
    )

    product_catalog.to_parquet(
        OUTPUT_DIR / "product_catalog.parquet",
        index=False,
    )

    print(
        "Created product_catalog.parquet",
        len(product_catalog),
        "rows",
    )

if __name__ == "__main__":
    main()
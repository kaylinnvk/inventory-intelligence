from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path("data/processed")

CLEAN_DATA_PATH = DATA_DIR / "m5_dashboard_clean.parquet"
FORECAST_OUTPUT_PATH = DATA_DIR / "streamlit_forecast_output.parquet"
RECOMMENDATION_PATH = DATA_DIR / "recommendations.parquet"

@st.cache_data
def load_daily_summary():
    return pd.read_parquet(
        DATA_DIR / "daily_summary.parquet"
    )

@st.cache_data
def load_product_catalog():
    return pd.read_parquet(
        DATA_DIR / "product_catalog.parquet"
    )

@st.cache_data
def load_product_history(store_id, item_id):
    # Product Explorer doesn't load all 8.2 mil rows into memory
    # It requests only the selected product-store history
    columns = [
        "date",
        "item_id",
        "dept_id",
        "store_id",
        "sales",
        "sell_price",
        "weekday",
        "is_weekend",
        "is_event",
        "snap",
    ]

    return pd.read_parquet(
        CLEAN_DATA_PATH,
        columns=columns,
        filters=[
            ("store_id", "==", store_id),
            ("item_id", "==", item_id),
        ],
    )

@st.cache_data
def load_forecasts():
    if not FORECAST_OUTPUT_PATH.exists():
        return pd.DataFrame()

    df = pd.read_parquet(FORECAST_OUTPUT_PATH)
    df["date"] = pd.to_datetime(df["date"])

    return df

@st.cache_data
def load_recommendations():
    if not RECOMMENDATION_PATH.exists():
        return pd.DataFrame()

    return pd.read_parquet(RECOMMENDATION_PATH)
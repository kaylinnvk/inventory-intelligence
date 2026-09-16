from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path("data/processed")

CLEAN_DATA_PATH = DATA_DIR / "m5_dashboard_clean.parquet"
FORECAST_OUTPUT_PATHS = (
    DATA_DIR / "streamlit_forecast_output.parquet",
    DATA_DIR / "forecasts.parquet",
)
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
    forecast_path = next(
        (path for path in FORECAST_OUTPUT_PATHS if path.exists()),
        None,
    )
    if forecast_path is None:
        return pd.DataFrame()

    df = pd.read_parquet(forecast_path)
    df["date"] = pd.to_datetime(df["date"])

    return df


@st.cache_data
def load_overview_history(store_id=None, dept_id=None):
    """Load only the fields needed for aggregate historical insights."""
    filters = []
    if store_id and store_id != "All":
        filters.append(("store_id", "==", store_id))
    if dept_id and dept_id != "All":
        filters.append(("dept_id", "==", dept_id))

    return pd.read_parquet(
        CLEAN_DATA_PATH,
        columns=["date", "sales", "is_weekend", "snap", "is_event"],
        filters=filters or None,
    )

@st.cache_data
def load_recommendations():
    if not RECOMMENDATION_PATH.exists():
        return pd.DataFrame()

    return pd.read_parquet(RECOMMENDATION_PATH)

import plotly.express as px
import streamlit as st

from src.data_loader import load_forecasts


st.title("Inventory Recommendations")

st.caption(
    "Prioritize replenishment based on forecast demand "
    "relative to recent historical demand."
)

df = load_forecasts()

if df.empty:
    st.info(
        "Forecast output is not available yet."
    )
    st.stop()


# =========================================================
# Filters
# =========================================================

st.sidebar.header("Inventory Filters")

store = st.sidebar.selectbox(
    "Store",
    sorted(df["store_id"].unique()),
    key="inventory_store",
)

store_data = df[
    df["store_id"] == store
].copy()


# =========================================================
# Store-level KPIs
# =========================================================

high_risk_products = (
    store_data.loc[
        store_data["risk_level"] == "High",
        "item_id",
    ]
    .nunique()
)

medium_risk_products = (
    store_data.loc[
        store_data["risk_level"] == "Medium",
        "item_id",
    ]
    .nunique()
)

total_products = store_data["item_id"].nunique()


col1, col2, col3 = st.columns(3)

col1.metric(
    "Products Monitored",
    f"{total_products:,}",
)

col2.metric(
    "High Demand Pressure",
    f"{high_risk_products:,}",
)

col3.metric(
    "Medium Demand Pressure",
    f"{medium_risk_products:,}",
)


# =========================================================
# Risk distribution
# =========================================================

st.subheader("Demand Pressure Distribution")

risk_summary = (
    store_data
    .groupby("risk_level", as_index=False)
    .size()
)

fig = px.bar(
    risk_summary,
    x="risk_level",
    y="size",
    category_orders={
        "risk_level": [
            "Low",
            "Medium",
            "High",
        ]
    },
    labels={
        "risk_level": "Risk Level",
        "size": "Forecast Days",
    },
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# =========================================================
# Priority products
# =========================================================

st.subheader("Priority Products")

priority = (
    store_data[
        store_data["risk_level"] == "High"
    ]
    .groupby(
        ["item_id", "inventory_recommendation"],
        as_index=False,
    )
    .agg(
        high_risk_days=("date", "nunique"),
        forecast_demand=("predicted_sales", "sum"),
    )
    .sort_values(
        [
            "high_risk_days",
            "forecast_demand",
        ],
        ascending=False,
    )
)

st.dataframe(
    priority,
    use_container_width=True,
    hide_index=True,
)
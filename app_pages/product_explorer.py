import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import (
    load_product_catalog,
    load_product_history,
)

st.title("Product Explorer")
st.caption(
    "Explore historical demand and pricing for individual products."
)

catalog = load_product_catalog()

# ====================================
# Filters
# ====================================

st.sidebar.header("Product Filters")

store = st.sidebar.selectbox(
    "Store",
    sorted(catalog["store_id"].unique()),
)

store_catalog = catalog[
    catalog["store_id"] == store
]

department = st.sidebar.selectbox(
    "Department",
    sorted(store_catalog["dept_id"].unique()),
)

department_catalog = store_catalog[
    store_catalog["dept_id"] == department
]

product = st.sidebar.selectbox(
    "Product",
    sorted(department_catalog["item_id"].unique()),
)

# ====================================
# Selected Product
# ====================================

summary = department_catalog[
    department_catalog["item_id"] == product
].iloc[0]

history = load_product_history(
    store_id=store,
    item_id=product,
).sort_values("date")

# ====================================
# Header
# ====================================

st.subheader(product)

st.caption(
    f"{store} • {department}"
)

# ====================================
# KPI Cards
# ====================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Units Sold",
    f"{summary['total_sales']:,.0f}"
)

col2.metric(
    "Average Daily Sales",
    f"{summary['avg_daily_sales']:,.0f}"
)

col3.metric(
    "Peak Daily Sales",
    f"{summary['max_daily_sales']:,.0f}"
)

# In IEEE 754 floating-point math, NaN is not equal to itself. 
if summary["latest_price"] == summary["latest_price"]:
    price_text = f"${summary['latest_price']:.2f}"
else:
    price_text = "N/A"

col4.metric(
    "Latest Price",
    price_text,
)

# ====================================
# Historical Demand
# ====================================

st.subheader("Historical Demand")

demand_fig = px.line(
    history,
    x="date",
    y="sales",
    labels={
        "date": "Date",
        "sales": "Units Sold",
    },
)

st.plotly_chart(
    demand_fig,
    width="stretch",
)

# ====================================
# Demand Patterns: Weekday vs Weekend
# ====================================

col1, col2 = st.columns(2)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

weekday_sales = (
    history
    .groupby("weekday", as_index=False)["sales"]
    .mean()
)

weekday_sales["weekday"] = (
    weekday_sales["weekday"]
    .astype(
        pd.CategoricalDtype(
            categories=weekday_order,
            ordered=True,
        )
    )
)

weekday_sales = weekday_sales.sort_values(
    "weekday"
)

with col1:
    st.subheader("Demand by Weekday")

    weekday_fig = px.bar(
        weekday_sales,
        x="weekday",
        y="sales",
        labels={
            "weekday": "Weekday",
            "sales" : "Average Units Sold",
        },
    )

    st.plotly_chart(
        weekday_fig,
        width="stretch",
    )

with col2:
    st.subheader("Weekend Effect")

    weekend_sales = (
        history
        .groupby("is_weekend", as_index=False)["sales"]
        .mean()
    )

    weekend_sales["day_type"] = (
        weekend_sales["is_weekend"]
        .map({
            0: "Weekday",
            1: "Weekend",
        })
    )

    weekend_fig = px.bar(
        weekend_sales,
        x="day_type",
        y="sales",
        labels={
            "day_type": "Day Type",
            "sales" : "Average Units Sold",
        },
    )

    st.plotly_chart(
        weekend_fig,
        width="stretch",
    )

# ====================================
# SNAP + events
# ====================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("SNAP Effect")

    snap_sales = (
        history
        .groupby("snap", as_index=False)["sales"]
        .mean()
    )

    snap_sales["snap_status"] = (
        snap_sales["snap"].map({
            0: "Non-SNAP Day",
            1: "SNAP Day",
        })
    )

    snap_fig = px.bar(
        snap_sales,
        x="snap_status",
        y="sales",
        labels={
            "snap_status": "",
            "sales": "Average Units Sold",
        },
    )

    st.plotly_chart(
        snap_fig,
        width="stretch",
    )

with col2:
    st.subheader("Event Effect")

    event_sales = (
        history
        .groupby("is_event", as_index=False)["sales"]
        .mean()
    )

    event_sales["event_status"] = (
        event_sales["is_event"].map({
            0: "Normal Day",
            1: "Event Day",
        })
    )

    event_fig = px.bar(
        event_sales,
        x="event_status",
        y="sales",
        labels={
            "event_status": "",
            "sales": "Average Units Sold",
        },
    )

    st.plotly_chart(
        event_fig,
        width="stretch",
    )

# ====================================
# SNAP + events
# ====================================

st.subheader("Price History")

price_history = history.dropna(
    subset=["sell_price"]
)

price_fig = px.line(
    price_history,
    x="date",
    y="sell_price",
    labels={
        "date": "Date",
        "sell_price": "Price",
    },
)

st.plotly_chart(
    price_fig,
    width="stretch"
)

# ====================================
# Additional Statistics
# ====================================

with st.expander("Additional Product Statistics"):
    st.write(
        f"Active sales days: "
        f"{summary['active_days']:,.0f}"
    )

    st.write(
        f"Zero-sales observations: "
        f"{summary['zero_sales_pct']:.1f}%"
    )
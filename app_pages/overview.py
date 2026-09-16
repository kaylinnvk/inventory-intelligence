import streamlit as st
import plotly.express as px

from src.data_loader import load_daily_summary

st.title("Inventory Intelligence")
st.caption("Demand Forecasting & Inventory Optimization")

df = load_daily_summary()

# ====================================
# Filters
# ====================================

st.sidebar.header("Filters")

store_options = ["All"] + sorted(
    df["store_id"].unique().tolist()
)

store = st.sidebar.selectbox(
    "Store",
    store_options,
)

dept_options = ["All"] + sorted(
    df["dept_id"].unique().tolist()
)

department = st.sidebar.selectbox(
    "Department",
    dept_options,
)

# ====================================
# Apply filters
# ====================================

filtered = df.copy()

if store != "All":
    filtered = filtered[
        filtered["store_id"] == store
    ]

if department != "All":
    filtered = filtered[
        filtered["dept_id"] == department
    ]

# ====================================
# KPI Cards
# ====================================

total_sales = filtered["total_sales"].sum()

daily_sales = (
    filtered
    .groupby("date")["total_sales"]
    .sum()
)

avg_daily_sales = daily_sales.mean()

product_count = filtered["unique_products"].max()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Units Sold",
    f"{total_sales:,.0f}"
)

col2.metric(
    "Average Daily Sales",
    f"{avg_daily_sales:,.0f}"
)

col3.metric(
    "Products",
    f"{product_count:,.0f}"
)

# ====================================
# Historical Demand Chart
# ====================================

demand_over_time = (
    filtered
    .groupby("date", as_index=False)["total_sales"]
    .sum()
)

fig = px.line(
    demand_over_time,
    x="date",
    y="total_sales",
    title="Historical Demand",
    labels={
        "date": "Date",
        "total_sales": "Units Sold",
    },
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.write("Data Preview")
st.dataframe(df.head())
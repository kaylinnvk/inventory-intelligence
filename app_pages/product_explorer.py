import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.charts import BLUE_LIGHT, WALMART_BLUE, WALMART_YELLOW, style_chart
from src.data_loader import load_product_catalog, load_product_history
from src.ui import insight_card, page_header, sidebar_filters_heading


# =========================================================
# Helpers
# =========================================================

def effect(frame, flag_column):
    averages = frame.groupby(flag_column)["sales"].mean()

    baseline = averages.get(0)
    affected = averages.get(1)

    if baseline is None or affected is None or baseline == 0:
        return None

    return (affected / baseline - 1) * 100


def effect_text(value):
    return "N/A" if value is None else f"{value:+.1f}%"


# =========================================================
# Data + filters
# =========================================================

catalog = load_product_catalog()

sidebar_filters_heading()

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


# =========================================================
# Selected product data
# =========================================================

summary = department_catalog[
    department_catalog["item_id"] == product
].iloc[0]

history = (
    load_product_history(
        store_id=store,
        item_id=product,
    )
    .sort_values("date")
)

history["rolling_sales"] = (
    history["sales"]
    .rolling(
        window=28,
        min_periods=7,
    )
    .mean()
)

recent_28_day_avg = (
    history["sales"]
    .tail(28)
    .mean()
)


# =========================================================
# Header
# =========================================================

page_header(
    "Product Explorer",
    "Inspect product-level demand, price, and historical demand associations.",
)

st.subheader(product)
st.caption(f"{store} | {department}")


# =========================================================
# KPI row
# =========================================================

price_text = (
    f"${summary['latest_price']:.2f}"
    if pd.notna(summary["latest_price"])
    else "N/A"
)

kpi_columns = st.columns(6)

kpi_columns[0].metric(
    "Total Units Sold",
    f"{summary['total_sales']:,.0f}",
)

kpi_columns[1].metric(
    "Average Daily Sales",
    f"{summary['avg_daily_sales']:,.2f}",
)

kpi_columns[2].metric(
    "Peak Daily Sales",
    f"{summary['max_daily_sales']:,.0f}",
)

kpi_columns[3].metric(
    "Latest Price",
    price_text,
)

kpi_columns[4].metric(
    "Active Sales Days",
    f"{summary['active_days']:,.0f}",
)

kpi_columns[5].metric(
    "Zero-Sales Rate",
    f"{summary['zero_sales_pct']:.1f}%",
)


# =========================================================
# Historical Demand — full width
# =========================================================

with st.container(border=True):
    header_col, stat_col = st.columns([4, 1])

    with header_col:
        st.subheader("Historical Demand")

    with stat_col:
        st.metric(
            "Recent 28-Day Avg.",
            f"{recent_28_day_avg:.2f}",
        )

    demand_fig = go.Figure()

    demand_fig.add_trace(
        go.Scatter(
            x=history["date"],
            y=history["sales"],
            mode="lines",
            name="Daily demand",
            line=dict(
                color=BLUE_LIGHT,
                width=1,
            ),
            opacity=0.45,
        )
    )

    demand_fig.add_trace(
        go.Scatter(
            x=history["date"],
            y=history["rolling_sales"],
            mode="lines",
            name="28-day trend",
            line=dict(
                color=WALMART_BLUE,
                width=3,
            ),
        )
    )

    st.plotly_chart(
        style_chart(
            demand_fig,
            height=360,
            show_legend=True,
        ),
        width="stretch",
        config={"displayModeBar": False},
    )


# =========================================================
# Supporting charts
# =========================================================

st.subheader("Demand Patterns")

weekday_col, price_col = st.columns(
    2,
    gap="medium",
)


# -------------------------
# Demand by Weekday
# -------------------------

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
    .groupby(
        "weekday",
        as_index=False,
    )["sales"]
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

weekday_sales["bar_color"] = (
    weekday_sales["weekday"]
    .isin(["Saturday", "Sunday"])
    .map(
        {
            False: WALMART_BLUE,
            True: WALMART_YELLOW,
        }
    )
)


with weekday_col:
    with st.container(border=True):
        st.subheader("Demand by Weekday")

        weekday_fig = go.Figure(
            go.Bar(
                x=weekday_sales["weekday"],
                y=weekday_sales["sales"],
                marker_color=weekday_sales["bar_color"],
                hovertemplate=(
                    "%{x}: %{y:.2f} average units"
                    "<extra></extra>"
                ),
            )
        )

        st.plotly_chart(
            style_chart(
                weekday_fig,
                height=310,
            ),
            width="stretch",
            config={"displayModeBar": False},
        )


# -------------------------
# Price History
# -------------------------

with price_col:
    with st.container(border=True):
        st.subheader("Price History")

        price_history = history.dropna(
            subset=["sell_price"]
        )

        if price_history.empty:
            st.info(
                "No price history is available for this product."
            )

        else:
            price_fig = px.line(
                price_history,
                x="date",
                y="sell_price",
            )

            price_fig.update_traces(
                line=dict(
                    color="#2995D3",
                    width=2,
                    shape="hv",
                )
            )

            price_fig.update_yaxes(
                tickprefix="$",
                tickformat=".2f",
            )

            st.plotly_chart(
                style_chart(
                    price_fig,
                    height=310,
                ),
                width="stretch",
                config={"displayModeBar": False},
            )


# =========================================================
# Demand Drivers
# =========================================================

st.subheader("Demand Drivers")

driver_col1, driver_col2, driver_col3 = st.columns(
    3,
    gap="medium",
)

with driver_col1:
    insight_card(
        "Weekend Uplift",
        effect_text(
            effect(
                history,
                "is_weekend",
            )
        ),
        "vs weekdays",
        "blue",
    )

with driver_col2:
    insight_card(
        "SNAP Uplift",
        effect_text(
            effect(
                history,
                "snap",
            )
        ),
        "vs non-SNAP days",
        "yellow",
    )

with driver_col3:
    insight_card(
        "Event Change",
        effect_text(
            effect(
                history,
                "is_event",
            )
        ),
        "vs non-event days",
        "yellow",
    )
import plotly.express as px
import streamlit as st

from src.charts import WALMART_BLUE, style_chart
from src.data_loader import load_daily_summary, load_overview_history, load_product_catalog
from src.ui import compact_number, insight_card, sidebar_filters_heading


def percentage_effect(frame, flag_column):
    """Return the average demand change for flagged days versus unflagged days."""
    grouped = frame.groupby(flag_column)["sales"].mean()
    baseline, comparison = grouped.get(0), grouped.get(1)
    if baseline is None or comparison is None or baseline == 0:
        return None
    return (comparison / baseline - 1) * 100


def change_label(value):
    return "N/A" if value is None else f"{value:+.1f}%"


def effect_insight(value, affected_days, baseline_days):
    if value is None:
        return None

    if value >= 0:
        change = f"{value:+.1f}% higher"
    else:
        change = f"{abs(value):.1f}% lower"

    return (
        "Historical average demand was "
        f"**{change}** on {affected_days} "
        f"than {baseline_days}."
    )


def top_products_table(product_data, daily_observations):
    """Rank one row per product, summing product-store series when needed."""
    products = (
        product_data.groupby(["item_id", "dept_id"], as_index=False)
        .agg(total_sales=("total_sales", "sum"))
        .assign(avg_daily_sales=lambda frame: frame["total_sales"] / daily_observations)
        .nlargest(8, "total_sales")
        .rename(
            columns={
                "item_id": "Product",
                "dept_id": "Department",
                "total_sales": "Units Sold",
                "avg_daily_sales": "Avg. Daily Sales",
            }
        )
    )
    return products


daily_summary = load_daily_summary()
catalog = load_product_catalog()

sidebar_filters_heading()
store = st.sidebar.selectbox("Store", ["All"] + sorted(daily_summary["store_id"].unique()))
department = st.sidebar.selectbox("Department", ["All"] + sorted(daily_summary["dept_id"].unique()))

filtered = daily_summary.copy()
filtered_catalog = catalog.copy()
if store != "All":
    filtered = filtered[filtered["store_id"] == store]
    filtered_catalog = filtered_catalog[filtered_catalog["store_id"] == store]
if department != "All":
    filtered = filtered[filtered["dept_id"] == department]
    filtered_catalog = filtered_catalog[filtered_catalog["dept_id"] == department]

history = load_overview_history(store, department)
st.title("Inventory Intelligence")
st.caption("Historical demand patterns and replenishment decision support.")

demand_over_time = filtered.groupby("date", as_index=False)["total_sales"].sum()
daily_sales = demand_over_time["total_sales"]

kpi_columns = st.columns(4)
kpi_columns[0].metric("Total Units Sold", compact_number(daily_sales.sum()))
kpi_columns[1].metric("Average Daily Sales", compact_number(daily_sales.mean()))
kpi_columns[2].metric("Products", compact_number(filtered_catalog["item_id"].nunique()))
kpi_columns[3].metric("Product-Store Series", compact_number(len(filtered_catalog)))

with st.container(border=True):
    st.subheader("Historical Demand")
    demand_fig = px.line(demand_over_time, x="date", y="total_sales")
    demand_fig.update_traces(line=dict(color=WALMART_BLUE, width=2.5))
    st.plotly_chart(style_chart(demand_fig, height=360), width="stretch", config={"displayModeBar": False})

store_column, dept_column = st.columns(2)
with store_column:
    with st.container(border=True):
        st.subheader("Sales by Store")
        store_sales = (
            filtered.groupby("store_id", as_index=False)["total_sales"]
            .sum()
            .sort_values("total_sales", ascending=False)
        )
        store_fig = px.bar(store_sales, x="store_id", y="total_sales", color_discrete_sequence=[WALMART_BLUE])
        st.plotly_chart(style_chart(store_fig, height=285), width="stretch", config={"displayModeBar": False})
with dept_column:
    with st.container(border=True):
        st.subheader("Sales by Department")
        department_sales = (
            filtered.groupby("dept_id", as_index=False)["total_sales"]
            .sum()
            .sort_values("total_sales", ascending=False)
        )
        dept_fig = px.bar(department_sales, x="dept_id", y="total_sales", color_discrete_sequence=[WALMART_BLUE])
        st.plotly_chart(style_chart(dept_fig, height=285), width="stretch", config={"displayModeBar": False})

weekend_change = percentage_effect(history, "is_weekend")
snap_change = percentage_effect(history, "snap")
event_change = percentage_effect(history, "is_event")
st.subheader("Demand Drivers")
driver_columns = st.columns(3)
drivers = [
    ("Weekend Effect", weekend_change, "vs weekdays"),
    ("SNAP Effect", snap_change, "vs non-SNAP days"),
    ("Event Effect", event_change, "vs non-event days"),
]
for column, (label, effect, description) in zip(driver_columns, drivers):
    with column:
        insight_card(label, change_label(effect), description)

top_column, insight_column = st.columns(2)
with top_column:
    with st.container(border=True):
        st.subheader("Top Products")
        top_products = top_products_table(
            filtered_catalog,
            daily_observations=demand_over_time["date"].nunique(),
        )
        st.dataframe(top_products, width="stretch", hide_index=True)
with insight_column:
    with st.container(border=True):
        st.subheader("Key Insights")
        highest_store = filtered.groupby("store_id")["total_sales"].sum().idxmax()
        highest_dept = filtered.groupby("dept_id")["total_sales"].sum().idxmax()
        insights = [
            f"**{highest_store}** has the highest historical sales volume in this view.",
            f"**{highest_dept}** is the highest-volume department in this view.",
        ]
        for effect, affected_days, baseline_days in [
            (weekend_change, "weekends", "weekdays"),
            (snap_change, "SNAP days", "non-SNAP days"),
            (event_change, "event days", "non-event days"),
        ]:
            insight = effect_insight(effect, affected_days, baseline_days)
            if insight:
                insights.append(insight)
        for insight in insights:
            st.markdown(f"- {insight}")

with st.expander("View underlying data"):
    st.dataframe(filtered, width="stretch", hide_index=True)

import plotly.express as px
import streamlit as st

from src.charts import PRESSURE_HIGH, WALMART_BLUE, WALMART_YELLOW, style_chart
from src.data_loader import load_forecasts
from src.ui import compact_number, page_header, sidebar_filters_heading


df = load_forecasts()
if df.empty:
    page_header("Inventory", "Focus replenishment attention on products with elevated forecast demand.")
    st.info("Forecast output is not available yet.")
    st.stop()

sidebar_filters_heading()
store = st.sidebar.selectbox("Store", sorted(df["store_id"].unique()), key="inventory_store")
store_data = df[df["store_id"] == store].copy()

high_products = store_data.loc[store_data["risk_level"] == "High", "item_id"].nunique()
medium_products = store_data.loc[store_data["risk_level"] == "Medium", "item_id"].nunique()
total_products = store_data["item_id"].nunique()
high_pressure_percent = high_products / total_products * 100 if total_products else 0

page_header("Inventory", f"Demand-pressure priorities for {store} based on current forecast output.")
kpi_columns = st.columns(4)
kpi_columns[0].metric("Products Monitored", compact_number(total_products))
kpi_columns[1].metric("High Demand Pressure", compact_number(high_products))
kpi_columns[2].metric("Medium Demand Pressure", compact_number(medium_products))
kpi_columns[3].metric("High-Pressure %", f"{high_pressure_percent:.1f}%")

distribution_column, action_column = st.columns(2)
with distribution_column:
    with st.container(border=True):
        st.subheader("Demand Pressure Distribution")
        risk_summary = store_data.groupby("risk_level", as_index=False).size().rename(columns={"size": "days"})
        pressure_order = ["Low", "Medium", "High"]
        risk_summary["risk_level"] = risk_summary["risk_level"].astype("category").cat.set_categories(pressure_order, ordered=True)
        risk_summary = risk_summary.sort_values("risk_level")
        distribution = px.pie(
            risk_summary,
            names="risk_level",
            values="days",
            hole=0.62,
            color="risk_level",
            color_discrete_map={"Low": WALMART_BLUE, "Medium": WALMART_YELLOW, "High": PRESSURE_HIGH},
        )
        distribution.update_traces(textinfo="percent", hovertemplate="%{label}: %{value} forecast days (%{percent})<extra></extra>")
        distribution.add_annotation(
            text=f"<b>{risk_summary['days'].sum():,.0f}</b><br>forecast days",
            showarrow=False,
            font=dict(size=14),
        )
        st.plotly_chart(
            style_chart(distribution, height=290, show_legend=True, hovermode="closest"),
            width="stretch",
            config={"displayModeBar": False},
        )
with action_column:
    with st.container(border=True):
        st.subheader("Action Summary")
        st.metric("Products Requiring Attention", compact_number(high_products))
        st.metric("Products with Medium Pressure", compact_number(medium_products))
        st.caption("High demand pressure indicates forecast demand is elevated relative to the historical baseline used by the current system. It is a replenishment-priority signal, not a confirmed stockout prediction.")

st.subheader("Priority Products")
priority = (
    store_data[store_data["risk_level"] == "High"]
    .groupby(["item_id", "inventory_recommendation"], as_index=False)
    .agg(high_pressure_days=("date", "nunique"), forecast_demand=("predicted_sales", "sum"))
    .sort_values(["high_pressure_days", "forecast_demand"], ascending=False)
)
priority.insert(0, "priority", range(1, len(priority) + 1))
priority_table = priority.rename(
    columns={
        "priority": "Priority",
        "item_id": "Product",
        "forecast_demand": "Forecast Demand",
        "high_pressure_days": "High-Pressure Days",
        "inventory_recommendation": "Recommended Action",
    }
)

if priority_table.empty:
    st.info("No products are currently classified with high demand pressure for this store.")
else:
    st.dataframe(priority_table.head(15), width="stretch", hide_index=True)
    with st.expander("View all priority products"):
        st.dataframe(priority_table, width="stretch", hide_index=True)

with st.expander("View forecast output"):
    st.dataframe(store_data, width="stretch", hide_index=True)

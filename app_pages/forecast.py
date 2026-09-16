import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.charts import BLUE_LIGHT, WALMART_YELLOW, style_chart
from src.data_loader import load_forecasts, load_product_history
from src.ui import compact_number, page_header, sidebar_filters_heading


forecast_data = load_forecasts()
if forecast_data.empty:
    page_header("Demand Forecast", "Compare forecast output with observed demand when validation data is available.")
    st.info("Forecast results are not available yet. Generate a forecast output file to view this page.")
    st.stop()

sidebar_filters_heading()
store = st.sidebar.selectbox("Store", sorted(forecast_data["store_id"].unique()), key="forecast_store")
store_forecasts = forecast_data[forecast_data["store_id"] == store]
product = st.sidebar.selectbox("Product", sorted(store_forecasts["item_id"].unique()), key="forecast_product")
product_forecast = store_forecasts[store_forecasts["item_id"] == product].sort_values("date")

history = load_product_history(store_id=store, item_id=product).sort_values("date")
actuals = history[history["date"].between(product_forecast["date"].min(), product_forecast["date"].max())][["date", "sales"]].copy()
comparison = product_forecast.merge(actuals, on="date", how="left", validate="one_to_one").rename(columns={"sales": "actual_sales"})

errors = comparison["actual_sales"] - comparison["predicted_sales"]
mae = errors.abs().mean()
rmse = np.sqrt((errors**2).mean())
actual_total = comparison["actual_sales"].sum(min_count=1)
predicted_total = comparison["predicted_sales"].sum()
horizon = comparison["date"].nunique()

page_header("Demand Forecast", f"{product} | {store} | {horizon}-day forecast horizon")
kpi_columns = st.columns(4)
kpi_columns[0].metric("Actual Demand", compact_number(actual_total))
kpi_columns[1].metric("Predicted Demand", compact_number(predicted_total))
kpi_columns[2].metric("MAE", compact_number(mae))
kpi_columns[3].metric("RMSE", compact_number(rmse))

with st.container(border=True):
    st.subheader("Actual vs Predicted Demand")
    forecast_fig = go.Figure()
    forecast_fig.add_trace(
        go.Scatter(
            x=comparison["date"],
            y=comparison["actual_sales"],
            mode="lines+markers",
            name="Actual",
            line=dict(color=BLUE_LIGHT, width=2),
            marker=dict(size=4),
        )
    )
    forecast_fig.add_trace(
        go.Scatter(
            x=comparison["date"],
            y=comparison["predicted_sales"],
            mode="lines+markers",
            name="Predicted",
            line=dict(color=WALMART_YELLOW, width=3),
            marker=dict(size=5),
        )
    )
    st.plotly_chart(style_chart(forecast_fig, height=335, show_legend=True), width="stretch", config={"displayModeBar": False})

summary_column, pressure_column = st.columns(2)
with summary_column:
    with st.container(border=True):
        st.subheader("Forecast Summary")
        peak_value = comparison["predicted_sales"].max()
        bias = predicted_total - actual_total if actual_total == actual_total else None
        summary_metrics = st.columns(3)
        summary_metrics[0].metric("Total Predicted", compact_number(predicted_total))
        summary_metrics[1].metric("Difference vs Actual", compact_number(bias))
        summary_metrics[2].metric("Peak Predicted", compact_number(peak_value))
with pressure_column:
    with st.container(border=True):
        st.subheader("Demand Pressure")
        risk_counts = product_forecast["risk_level"].value_counts() if "risk_level" in product_forecast else {}
        pressure_metrics = st.columns(3)
        pressure_metrics[0].metric("Low Days", risk_counts.get("Low", 0))
        pressure_metrics[1].metric("Medium Days", risk_counts.get("Medium", 0))
        pressure_metrics[2].metric("High Days", risk_counts.get("High", 0))

with st.expander("View Daily Forecast"):
    table_columns = [column for column in ["date", "actual_sales", "predicted_sales", "risk_level", "inventory_status"] if column in comparison]
    st.dataframe(comparison[table_columns], width="stretch", hide_index=True)

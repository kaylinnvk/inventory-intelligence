<p align="center">
  <img src="assets/logo.png" alt="Inventory Intelligence" width="520">
</p>

A Streamlit-based decision-support dashboard built on the **M5 Forecasting dataset**. It combines historical demand analysis, 28-day demand forecasting, and inventory-oriented recommendations to support replenishment decisions.

## Scope

The current prototype focuses on the **FOODS** category across three Walmart stores:

- `CA_1`
- `TX_1`
- `WI_1`

It covers **1,437 products**, **4,311 product-store series**, and **1,913 days** of historical sales.

## Dashboard

The app contains four main pages:

- **Overview** — high-level demand trends and key drivers
- **Product Explorer** — product-level demand, price, and weekday patterns
- **Demand Forecast** — 28-day forecast results and model validation
- **Inventory** — demand-pressure priorities and replenishment guidance

## Tech Stack

`Python` · `Pandas` · `LightGBM` · `Plotly` · `Streamlit` · `Parquet`

## Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Repository

| Path | Purpose |
| --- | --- |
| `streamlit_app.py` | Streamlit entry point |
| `app_pages/` | Dashboard pages |
| `src/` | Shared loaders and utilities |
| `scripts/` | Data preparation |
| `notebooks/` | EDA and modeling |
| `data/` | Dashboard data |
| `assets/` | Logo and styling |

## Goal

The project connects forecasting with decision support:

> **Forecasting:** What will demand be?  
> **Inventory Intelligence:** What should we do about it?

> **Note:** The M5 dataset does not contain actual on-hand inventory. Current inventory outputs therefore represent **demand pressure / replenishment priority**, not confirmed stockout risk.
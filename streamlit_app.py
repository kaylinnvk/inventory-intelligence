import streamlit as st

st.set_page_config(
    page_title="Inventory Intelligence",
    page_icon="📦",
    layout="wide"
)

pages = [
    st.Page(
        "app_pages/overview.py",
        title="Overview",
        icon=":material/dashboard:",
        default=True
    ),
    st.Page(
        "app_pages/product_explorer.py",
        title="Product Explorer",
        icon=":material/search:"
    ),
    st.Page(
        "app_pages/forecast.py",
        title="Demand Forecast",
        icon=":material/trending_up:"
    ),
    st.Page(
        "app_pages/inventory.py",
        title="Inventory",
        icon=":material/inventory_2:"
    )
]

page = st.navigation(pages)
page.run()
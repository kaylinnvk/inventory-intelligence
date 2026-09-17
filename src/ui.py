from pathlib import Path
from html import escape
import streamlit as st


WALMART_BLUE = "#007CC2"
WALMART_YELLOW = "#FDBB2E"


def _sidebar_theme_css() -> str:
    """Return fixed light-theme CSS variables for the sidebar."""
    return """
    :root {
        --sidebar-bg: #F7F8FA;
        --sidebar-card: rgba(255, 255, 255, 0.90);
        --sidebar-active: rgba(253, 187, 46, 0.16);
        --sidebar-border: rgba(15, 23, 42, 0.12);
        --sidebar-muted: #6B7280;
        --sidebar-shadow: rgba(15, 23, 42, 0.05);
    }
    """


def compact_number(value: float | int | None) -> str:
    """Format dashboard KPIs without hiding useful smaller values."""
    if value is None:
        return "N/A"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if number != number:
        return "N/A"
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if abs(number) >= 1_000:
        return f"{number / 1_000:.1f}K"
    if number.is_integer():
        return f"{number:,.0f}"
    return f"{number:,.2f}"


def sidebar_branding():
    """Render the shared compact brand card before Streamlit navigation."""
    st.sidebar.markdown(
        """
        <div class="sidebar-brand-card">
            <span class="sidebar-brand-accent"></span>
            <div>
                <div class="sidebar-brand-title">Inventory Intelligence</div>
                <div class="sidebar-brand-subtitle">M5 Decision Support</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_filters_heading():
    """Separate page-specific filters from the shared page navigation."""
    st.sidebar.markdown(
        "<div class='sidebar-filter-heading'>Filters</div>",
        unsafe_allow_html=True,
    )


def load_css():
    css_path = Path("assets/styles.css")

    if css_path.exists():
        theme_css = _sidebar_theme_css()

        st.markdown(
            f"<style>{css_path.read_text()}\n{theme_css}</style>",
            unsafe_allow_html=True,
        )


def page_header(
    title: str,
    subtitle: str,
    eyebrow: str | None = None,
):
    """Render a spacious, native heading stack that remains visible at page top."""
    with st.container():
        if eyebrow:
            st.caption(eyebrow.upper())
        st.title(title)
        st.caption(subtitle)


def insight_card(
    label: str,
    value: str,
    description: str,
    accent: str = "blue",
):
    """Render a theme-aware, bordered demand-driver KPI card."""
    with st.container(border=True):
        st.caption(escape(label).upper())
        st.markdown(f"### {escape(str(value))}")
        st.caption(escape(description))

from pathlib import Path
from html import escape
import streamlit as st


WALMART_BLUE = "#007CC2"
WALMART_YELLOW = "#FDBB2E"


def _sidebar_theme_css(theme_type: str | None) -> str:
    """Return sidebar-only CSS variables for the active Streamlit theme."""
    if theme_type == "dark":
        palette = {
            "bg": "#171A21",
            "card": "rgba(255, 255, 255, 0.06)",
            "active": "rgba(253, 187, 46, 0.14)",
            "border": "rgba(255, 255, 255, 0.14)",
            "muted": "#AAB2C0",
            "shadow": "rgba(0, 0, 0, 0.22)",
        }
    else:
        palette = {
            "bg": "#F7F8FA",
            "card": "rgba(255, 255, 255, 0.90)",
            "active": "rgba(253, 187, 46, 0.16)",
            "border": "rgba(15, 23, 42, 0.12)",
            "muted": "#6B7280",
            "shadow": "rgba(15, 23, 42, 0.05)",
        }

    return f"""
    :root {{
        --sidebar-bg: {palette['bg']};
        --sidebar-card: {palette['card']};
        --sidebar-active: {palette['active']};
        --sidebar-border: {palette['border']};
        --sidebar-muted: {palette['muted']};
        --sidebar-shadow: {palette['shadow']};
    }}
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
        theme_type = st.context.theme.get("type") or "light"
        theme_css = _sidebar_theme_css(theme_type)
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
    """Render a compact, right-aligned demand-driver card."""
    accent_class = "insight-yellow" if accent == "yellow" else "insight-blue"
    st.html(
        f"""
        <div class="insight-card {accent_class}">
            <div class="insight-label">{escape(label)}</div>
            <div class="insight-value">{escape(str(value))}</div>
            <div class="insight-description">{escape(description)}</div>
        </div>
        """
    )

from pathlib import Path

import streamlit as st


WALMART_BLUE = "#007CC2"
WALMART_YELLOW = "#FDBB2E"


def load_css():
    css_path = Path("assets/styles.css")

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text()}</style>",
            unsafe_allow_html=True,
        )


def page_header(
    title: str,
    subtitle: str,
    eyebrow: str | None = None,
):
    eyebrow_html = ""

    if eyebrow:
        eyebrow_html = (
            f'<div class="section-label">{eyebrow}</div>'
        )

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            {eyebrow_html}

            <h1 style="
                margin-top: 0.25rem;
                margin-bottom: 0.35rem;
            ">
                {title}
            </h1>

            <div style="
                color: #9CA3AF;
                font-size: 0.95rem;
            ">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(
    label: str,
    value: str,
    description: str,
    accent: str = "blue",
):
    accent_class = (
        "insight-yellow"
        if accent == "yellow"
        else "insight-blue"
    )

    st.markdown(
        f"""
        <div class="insight-card {accent_class}">
            <div class="insight-label">
                {label}
            </div>

            <div class="insight-value">
                {value}
            </div>

            <div class="insight-description">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
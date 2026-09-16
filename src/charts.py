WALMART_BLUE = "#007CC2"
WALMART_YELLOW = "#FDBB2E"

BLUE_LIGHT = "#7CC4EA"
BLUE_MEDIUM = "#2995D3"

GRID_COLOR = "rgba(128, 128, 128, 0.18)"


def style_chart(
    fig,
    height=320,
    show_legend=False,
):
    fig.update_layout(
        height=height,
        margin=dict(
            l=15,
            r=15,
            t=15,
            b=15,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        showlegend=show_legend,
        font=dict(
            family="Arial, sans-serif",
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zeroline=False,
    )

    if show_legend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            )
        )

    return fig
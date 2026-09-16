WALMART_BLUE = "#007CC2"
WALMART_YELLOW = "#FDBB2E"
PRESSURE_HIGH = "#E45757"

BLUE_LIGHT = "#7CC4EA"
BLUE_MEDIUM = "#2995D3"

GRID_COLOR = "rgba(128, 128, 128, 0.18)"


def style_chart(
    fig,
    height=320,
    show_legend=False,
    hovermode="x unified",
):
    fig.update_layout(
        height=height,
        margin=dict(l=32, r=20, t=52 if show_legend else 24, b=32),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode=hovermode,
        showlegend=show_legend,
        font=dict(
            family="Arial, sans-serif",
            size=12,
        ),
        bargap=0.22,
        hoverlabel=dict(namelength=-1),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=11),
    )

    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        gridwidth=1,
        zeroline=False,
        title=None,
        tickfont=dict(size=11),
    )

    fig.update_xaxes(title=None)

    if show_legend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="left",
                x=0,
            )
        )

    return fig

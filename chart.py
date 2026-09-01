"""Kuvaajan rakentaminen. Erillään käyttöliittymästä, jotta on testattavissa."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core import INTRADAY, macd, rsi

# Plotlyn modebariin lisättävät piirtotyökalut.
DRAW_TOOLS = [
    "drawline",
    "drawopenpath",
    "drawrect",
    "eraseshape",
]

PLOTLY_CONFIG = {
    "scrollZoom": True,          # rullalla zoomaus kuten TradingView'ssä
    "displaylogo": False,
    "modeBarButtonsToAdd": DRAW_TOOLS,
    "doubleClick": "reset",
    "toImageButtonOptions": {"format": "png", "scale": 2},
}

UP = "#26a69a"
DOWN = "#ef5350"


def _rangebreaks(interval: str) -> list[dict]:
    """Poista tyhjät kohdat: viikonloput ja pörssin kiinnioloajat."""
    breaks: list[dict] = [dict(bounds=["sat", "mon"])]
    if interval in INTRADAY:
        # Yhdysvaltain pörssin kaupankäyntiaika 09:30–16:00 paikallista aikaa.
        breaks.append(dict(bounds=[16, 9.5], pattern="hour"))
    return breaks


def build_figure(
    df: pd.DataFrame,
    title: str,
    interval: str,
    sma_lengths: list[int],
    log_scale: bool = True,
    show_rsi: bool = True,
    show_macd: bool = False,
    rsi_length: int = 14,
    height: int = 720,
) -> go.Figure:
    """Kynttilägraafi ja valinnaiset indikaattorit omissa paneeleissaan."""
    panels = 1 + int(show_rsi) + int(show_macd)
    heights = {1: [1.0], 2: [0.74, 0.26], 3: [0.62, 0.19, 0.19]}[panels]

    fig = make_subplots(
        rows=panels,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=heights,
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=title,
            increasing_line_color=UP,
            decreasing_line_color=DOWN,
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    for n in sma_lengths:
        col = f"SMA{n}"
        if col in df:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[col], name=col,
                    line=dict(width=1.2), hovertemplate="%{y:.4f}<extra>" + col + "</extra>",
                ),
                row=1,
                col=1,
            )

    row = 2
    if show_rsi:
        r = rsi(df["Close"], rsi_length)
        fig.add_trace(
            go.Scatter(
                x=df.index, y=r, name=f"RSI {rsi_length}",
                line=dict(width=1.2, color="#b39ddb"),
                hovertemplate="%{y:.1f}<extra>RSI</extra>",
            ),
            row=row,
            col=1,
        )
        for level, dash in ((70, "dot"), (50, "dashdot"), (30, "dot")):
            fig.add_hline(
                y=level, line=dict(width=0.8, dash=dash, color="#666666"),
                row=row, col=1,
            )
        fig.update_yaxes(range=[0, 100], row=row, col=1, title_text="RSI")
        row += 1

    if show_macd:
        m = macd(df["Close"])
        colors = [UP if v >= 0 else DOWN for v in m["Hist"]]
        fig.add_trace(
            go.Bar(x=df.index, y=m["Hist"], name="Hist", marker_color=colors, opacity=0.5),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=m["MACD"], name="MACD", line=dict(width=1.2, color="#42a5f5")),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=m["Signal"], name="Signal", line=dict(width=1.2, color="#ffa726")),
            row=row, col=1,
        )
        fig.update_yaxes(title_text="MACD", row=row, col=1)

    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=28, b=8),
        template="plotly_dark",
        dragmode="pan",              # hiiren veto panoroi, ei zoomaa laatikkoon
        hovermode="x unified",
        hoverdistance=1,
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
        bargap=0,
        newshape=dict(line=dict(color="#ffca28", width=1.5)),
    )

    # Ristikkokursori: pystyviiva läpi kaikkien paneelien, vaakaviiva hinnalle.
    fig.update_xaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#888888",
        rangeslider_visible=False,
        rangebreaks=_rangebreaks(interval),
    )
    fig.update_yaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#888888",
    )

    fig.update_yaxes(
        type="log" if log_scale else "linear",
        side="right",
        tickformat=".4f",
        row=1,
        col=1,
    )
    fig.update_xaxes(showticklabels=True, row=panels, col=1)
    return fig

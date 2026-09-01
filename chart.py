"""Chart building, kept apart from the UI so it can be tested on its own."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core import INTRADAY, macd, rsi

# Drawing tools added to the Plotly toolbar.
DRAW_TOOLS = [
    "drawline",
    "drawopenpath",
    "drawrect",
    "eraseshape",
]

PLOTLY_CONFIG = {
    "scrollZoom": True,          # wheel zoom, the way TradingView does it
    "responsive": True,          # follow the size of its container
    "displaylogo": False,
    "modeBarButtonsToAdd": DRAW_TOOLS,
    "doubleClick": "reset",
    "toImageButtonOptions": {"format": "png", "scale": 2},
}

UP = "#26a69a"
DOWN = "#ef5350"


def _rangebreaks(interval: str) -> list[dict]:
    """Drop the empty gaps: weekends and hours when the market is shut."""
    breaks: list[dict] = [dict(bounds=["sat", "mon"])]
    if interval in INTRADAY:
        # US market hours, 09:30 to 16:00 local time.
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
    """Candles, with optional indicators in panels of their own."""
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
        dragmode="pan",              # dragging pans instead of box zooming
        hovermode="x unified",
        hoverdistance=1,
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
        bargap=0,
        newshape=dict(line=dict(color="#ffca28", width=1.5)),
    )

    # Crosshair: a vertical line through every panel and a horizontal one on price.
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
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(
        fixedrange=False,
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


def resizable_html(fig: go.Figure, height: int = 760, auto_y: bool = True) -> str:
    """Wrap the chart in a box you can drag taller from its bottom edge.

    Streamlit renders this inside an iframe. The ResizeObserver tells both
    Plotly and Streamlit about the new height so the iframe grows with the box.

    auto_y refits the price axis to whatever candles are visible whenever the
    x axis moves, the way TradingView behaves.
    """
    fig = go.Figure(fig)
    fig.update_layout(height=None, autosize=True)
    body = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config=PLOTLY_CONFIG,
        div_id="gd",
    )
    return f"""
<div id="wrap" style="height:{height}px;min-height:280px;resize:vertical;overflow:hidden;">
  {body}
</div>
<div style="height:6px;cursor:ns-resize;background:#3a3a3a;border-radius:3px;margin-top:2px;"></div>
<script>
  const wrap = document.getElementById("wrap");
  const gd = document.getElementById("gd");
  const autoY = {str(auto_y).lower()};
  let busy = false;

  function sync() {{
    const h = wrap.clientHeight;
    gd.style.height = h + "px";
    if (window.Plotly) window.Plotly.Plots.resize(gd);
    window.parent.postMessage(
      {{type: "streamlit:setFrameHeight", height: h + 16}}, "*"
    );
  }}

  // Refit the price axis to the candles currently in view.
  function fitY() {{
    if (busy || !window.Plotly) return;
    const c = gd.data.find(t => t.type === "candlestick");
    const xr = gd.layout.xaxis && gd.layout.xaxis.range;
    if (!c || !xr) return;

    const x0 = new Date(xr[0]).getTime();
    const x1 = new Date(xr[1]).getTime();
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < c.x.length; i++) {{
      const xi = new Date(c.x[i]).getTime();
      if (xi >= x0 && xi <= x1) {{
        if (c.low[i] < lo) lo = c.low[i];
        if (c.high[i] > hi) hi = c.high[i];
      }}
    }}
    if (!isFinite(lo) || !isFinite(hi) || lo <= 0) return;

    let range;
    if (gd.layout.yaxis.type === "log") {{
      const a = Math.log10(lo), b = Math.log10(hi);
      const pad = (b - a) * 0.08 || 0.01;
      range = [a - pad, b + pad];
    }} else {{
      const pad = (hi - lo) * 0.08 || hi * 0.01;
      range = [lo - pad, hi + pad];
    }}
    busy = true;
    window.Plotly.relayout(gd, {{"yaxis.range": range}}).then(() => {{ busy = false; }});
  }}

  new ResizeObserver(sync).observe(wrap);
  setTimeout(function () {{
    sync();
    if (autoY && gd.on) {{
      gd.on("plotly_relayout", function (ev) {{
        // Only an x axis change triggers a refit, so a manual y zoom sticks.
        if (ev["xaxis.range[0]"] !== undefined || ev["xaxis.autorange"]) fitY();
      }});
      fitY();
    }}
  }}, 200);
</script>
"""

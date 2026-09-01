"""Ratio charts for two instruments, for example HYG/IEF.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import digest
from chart import PLOTLY_CONFIG, build_figure, resizable_html
from core import (
    PERIODS_BY_INTERVAL,
    TIMEFRAMES,
    add_sma,
    level,
    load_prices,
    percentile_range,
    ratio_ohlc,
    resample_ohlc,
    summary,
)
from presets import PRESETS, THEMES, Pair, all_pairs, flat
from tickers import describe

st.set_page_config(page_title="Ratio charts", layout="wide")

FLAT = flat()
CUSTOM = "— custom —"

# What loads on startup.
DEFAULT_TIMEFRAME = "Daily"   # any key from core.TIMEFRAMES
DEFAULT_PERIOD = "1y"         # used where the timeframe allows it, longest available otherwise
DEFAULT_PAIR = PRESETS["Credit risk"][0]

REFERENCE_DAYS = 756          # about three years of trading days

for key, value in {
    "theme": "Credit risk",
    "pair": DEFAULT_PAIR.label,
    "ticker_a": DEFAULT_PAIR.a,
    "ticker_b": DEFAULT_PAIR.b,
}.items():
    st.session_state.setdefault(key, value)


# --- Data ---------------------------------------------------------------

@st.cache_data(ttl=900, show_spinner=False)
def cached_prices(ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
    return load_prices(ticker, period=period, interval=interval)


def _pct(series: pd.Series, bars: int) -> float:
    if len(series) <= bars:
        return float("nan")
    return float((series.iloc[-1] / series.iloc[-1 - bars] - 1) * 100)


@st.cache_data(ttl=900, show_spinner=False)
def reference_range(a: str, b: str) -> dict[str, float] | None:
    """The pair's own range, measured over three years of daily data."""
    try:
        ca = cached_prices(a, "5y")["Close"]
        cb = cached_prices(b, "5y")["Close"]
    except Exception:
        return None
    r = (ca / cb).dropna().tail(REFERENCE_DAYS)
    if len(r) < 200:
        return None
    return percentile_range(r)


def _reading(p: Pair, three_month: float, above_ma: bool, position: float) -> tuple[str, str]:
    """Classify the direction and say what it means for this pair."""
    if three_month > 2 and above_ma:
        state, text = "Rising", p.rising
    elif three_month < -2 and not above_ma:
        state, text = "Falling", p.falling
    else:
        state, text = "Flat", "no clear direction"

    text = text[0].upper() + text[1:]
    if position >= 90:
        text += ". Close to its yearly high"
    elif position <= 10:
        text += ". Close to its yearly low"
    return state, text


@st.cache_data(ttl=900, show_spinner=False)
def screen(period: str = "2y") -> pd.DataFrame:
    """Changes and readings for every preset pair in one table."""
    rows = []
    for theme, p in all_pairs():
        try:
            ca = cached_prices(p.a, period)["Close"]
            cb = cached_prices(p.b, period)["Close"]
        except Exception:
            continue
        r = (ca / cb).dropna()
        if len(r) < 60:
            continue

        window = r.tail(252)
        span = float(window.max() - window.min())
        position = float((window.iloc[-1] - window.min()) / span * 100) if span else float("nan")
        three_month = _pct(r, 63)
        pct_of_history = float((r < r.iloc[-1]).mean() * 100)
        above_ma = bool(r.iloc[-1] > r.rolling(50).mean().iloc[-1])
        state, reading = _reading(p, three_month, above_ma, position)

        rows.append(
            {
                "Theme": theme,
                "Pair": p.name,
                "Topic": p.topic,
                "Level": level(pct_of_history),
                "State": state,
                "Reading": reading,
                "1M %": _pct(r, 21),
                "3M %": three_month,
                "12M %": _pct(r, 252),
                "52w position %": position,
            }
        )
    return pd.DataFrame(rows)


# --- Sidebar ------------------------------------------------------------

def on_theme_change() -> None:
    theme = st.session_state.theme
    if theme in PRESETS:
        p = PRESETS[theme][0]
        st.session_state.pair = p.label
        st.session_state.ticker_a = p.a
        st.session_state.ticker_b = p.b


def on_pair_change() -> None:
    p = FLAT.get(st.session_state.pair)
    if p:
        st.session_state.ticker_a = p.a
        st.session_state.ticker_b = p.b


with st.sidebar:
    st.header("Pair")
    st.selectbox("Theme", [CUSTOM, *PRESETS], key="theme", on_change=on_theme_change)

    selected: Pair | None = None
    selected_theme = ""
    if st.session_state.theme in PRESETS:
        options = [p.label for p in PRESETS[st.session_state.theme]]
        if st.session_state.pair not in options:
            st.session_state.pair = options[0]
        st.selectbox("Preset pair", options, key="pair", on_change=on_pair_change)
        selected = FLAT[st.session_state.pair]
        selected_theme = st.session_state.theme

    col_a, col_b = st.columns(2)
    col_a.text_input("Numerator", key="ticker_a")
    col_b.text_input("Denominator", key="ticker_b")

    st.header("Timeframe")
    tf_names = list(TIMEFRAMES)
    tf_name = st.selectbox("Candle", tf_names, index=tf_names.index(DEFAULT_TIMEFRAME))
    interval, rule = TIMEFRAMES[tf_name]
    periods = PERIODS_BY_INTERVAL[interval]
    period = st.selectbox(
        "History",
        periods,
        index=periods.index(DEFAULT_PERIOD) if DEFAULT_PERIOD in periods else len(periods) - 1,
    )

    st.header("Indicators")
    sma_input = st.text_input("Moving averages (comma separated)", "20, 50")
    show_rsi = st.checkbox("RSI", value=False)
    rsi_length = st.number_input("RSI length", 2, 100, 14, disabled=not show_rsi)
    show_macd = st.checkbox("MACD", value=False)
    log_scale = st.checkbox("Log scale", value=False)
    height = st.slider("Starting height", 400, 1200, 760, step=20)
    resizable = st.checkbox("Draggable height", value=True)

ticker_a = st.session_state.ticker_a.strip().upper()
ticker_b = st.session_state.ticker_b.strip().upper()
sma_lengths = [int(p.strip()) for p in sma_input.split(",") if p.strip().isdigit()]

# Only keep the preset caption while the tickers still match it.
if selected and (ticker_a, ticker_b) != (selected.a, selected.b):
    selected = None
    selected_theme = ""


# --- Tabs ---------------------------------------------------------------

tab_chart, tab_screen = st.tabs(["Chart", "Overview"])

with tab_chart:
    try:
        with st.spinner("Fetching data…"):
            a = cached_prices(ticker_a, period, interval)
            b = cached_prices(ticker_b, period, interval)
        ratio = add_sma(resample_ohlc(ratio_ohlc(a, b), rule), sma_lengths)
    except Exception as exc:  # noqa: BLE001 – show the failure to the user
        st.error(f"Could not load data: {exc}")
        st.stop()

    if len(ratio) < 2:
        st.warning("Not enough data to draw. Try a longer history.")
        st.stop()

    # --- above the chart: what the legs are, what the pair reads, where it stands ---

    st.subheader(f"{ticker_a} / {ticker_b}")

    about_a, about_b = describe(ticker_a), describe(ticker_b)
    if about_a:
        st.markdown(f"**{ticker_a}** (numerator). {about_a}")
    if about_b:
        st.markdown(f"**{ticker_b}** (denominator). {about_b}")

    if selected:
        st.markdown(
            f"**{selected.topic}.** The ratio rises when {ticker_a} outperforms "
            f"{ticker_b}, which means {selected.rising}. A falling ratio means "
            f"{selected.falling}."
        )
        if selected.note:
            st.markdown(f"**Worth knowing.** {selected.note}")
    if selected_theme in THEMES:
        st.markdown(f"**Why {selected_theme.lower()} matters.** {THEMES[selected_theme]}")

    ref = reference_range(ticker_a, ticker_b)
    if ref:
        current = level(ref["percentile"])
        meaning = {
            "High": selected.rising if selected else "the ratio is near the top of its range",
            "Low": selected.falling if selected else "the ratio is near the bottom of its range",
            "Normal": "this is an ordinary level",
        }[current]
        st.info(
            f"**{current}: {ref['now']:.4f}** sits above "
            f"{ref['percentile']:.0f}% of the last three years. "
            f"Low is under {ref['low']:.4f}, the median is {ref['median']:.4f} "
            f"and high is over {ref['high']:.4f}. "
            f"{meaning[0].upper() + meaning[1:]}."
        )

    if selected and selected.convention:
        st.warning(selected.convention)

    # --- the chart ---

    fig = build_figure(
        ratio,
        title=f"{ticker_a}/{ticker_b}",
        interval=interval,
        sma_lengths=sma_lengths,
        log_scale=log_scale,
        show_rsi=show_rsi,
        show_macd=show_macd,
        rsi_length=int(rsi_length),
        height=height,
    )
    if resizable:
        components.html(resizable_html(fig, height), height=height + 16, scrolling=False)
    else:
        st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    # --- below the chart: headline numbers and the raw data ---

    s = summary(ratio)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last", f"{s['last']:.4f}")
    c2.metric("Change over period", f"{s['change_pct']:+.1f}%")
    c3.metric("Lowest", f"{s['min']:.4f}")
    c4.metric("Highest", f"{s['max']:.4f}")

    with st.expander("Data as a table"):
        st.dataframe(ratio.tail(300).iloc[::-1], width="stretch")

with tab_screen:
    st.subheader("Every preset pair")
    st.caption(
        "Two years of daily data. State comes from the three month change together "
        "with the 50 day average. The 52w position shows where the ratio sits in its "
        "yearly range, where 0% is the low and 100% the high."
    )
    if st.button("Run the overview"):
        with st.spinner("Fetching around 40 tickers, the first run takes a moment…"):
            df = screen()
        if df.empty:
            st.warning("No data came back.")
        else:
            report = digest.build(df)
            st.markdown(f"### The big picture\n{report['paragraph']}")

            if report["conflicts"]:
                for line in report["conflicts"]:
                    st.warning(line)

            if report["outliers"]:
                st.markdown("**Moves worth a look**")
                for line in report["outliers"]:
                    st.markdown(f"- {line}")

            st.divider()
            st.dataframe(
                df.sort_values("3M %", ascending=False),
                width="stretch",
                hide_index=True,
                column_config={
                    c: st.column_config.NumberColumn(c, format="%.1f")
                    for c in ["1M %", "3M %", "12M %", "52w position %"]
                },
            )

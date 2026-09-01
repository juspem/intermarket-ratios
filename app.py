"""Suhdelukugraafi kahdelle instrumentille, esim. HYG/IEF.

Käynnistys:  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import RESAMPLE_RULES, add_sma, load_prices, ratio_ohlc, resample_ohlc, summary
from presets import PRESETS, flat

st.set_page_config(page_title="Suhdelukugraafi", layout="wide")

FLAT = flat()
OMA = "— oma valinta —"

for key, value in {
    "cat": "Luottoriski",
    "pair": "HYG / IEF",
    "ticker_a": "HYG",
    "ticker_b": "IEF",
}.items():
    st.session_state.setdefault(key, value)


# --- Datan haku ---------------------------------------------------------

@st.cache_data(ttl=900, show_spinner=False)
def cached_prices(ticker: str, period: str) -> pd.DataFrame:
    return load_prices(ticker, period=period, interval="1d")


def _pct(series: pd.Series, bars: int) -> float:
    if len(series) <= bars:
        return float("nan")
    return float((series.iloc[-1] / series.iloc[-1 - bars] - 1) * 100)


@st.cache_data(ttl=900, show_spinner=False)
def screen(period: str) -> pd.DataFrame:
    """Laske kaikkien valmiiden parien muutokset yhteen taulukkoon."""
    rows = []
    for cat, items in PRESETS.items():
        for a, b, desc in items:
            try:
                ca = cached_prices(a, period)["Close"]
                cb = cached_prices(b, period)["Close"]
            except Exception:
                continue
            r = (ca / cb).dropna()
            if len(r) < 30:
                continue
            window = r.tail(252)
            span = float(window.max() - window.min())
            pos = float((window.iloc[-1] - window.min()) / span * 100) if span else float("nan")
            rows.append(
                {
                    "Teema": cat,
                    "Pari": f"{a} / {b}",
                    "1 kk %": _pct(r, 21),
                    "3 kk %": _pct(r, 63),
                    "12 kk %": _pct(r, 252),
                    "Sijainti 52vk %": pos,
                    "Selite": desc,
                }
            )
    return pd.DataFrame(rows)


# --- Sivupalkki ---------------------------------------------------------

def on_cat_change() -> None:
    cat = st.session_state.cat
    if cat in PRESETS:
        a, b, _ = PRESETS[cat][0]
        st.session_state.pair = f"{a} / {b}"
        st.session_state.ticker_a = a
        st.session_state.ticker_b = b


def on_pair_change() -> None:
    key = st.session_state.pair
    if key in FLAT:
        a, b, _ = FLAT[key]
        st.session_state.ticker_a = a
        st.session_state.ticker_b = b


with st.sidebar:
    st.header("Pari")
    st.selectbox("Teema", [OMA, *PRESETS], key="cat", on_change=on_cat_change)

    selite = ""
    if st.session_state.cat in PRESETS:
        options = [f"{a} / {b}" for a, b, _ in PRESETS[st.session_state.cat]]
        if st.session_state.pair not in options:
            st.session_state.pair = options[0]
        st.selectbox("Valmis pari", options, key="pair", on_change=on_pair_change)
        selite = FLAT[st.session_state.pair][2]

    col_a, col_b = st.columns(2)
    col_a.text_input("Osoittaja", key="ticker_a")
    col_b.text_input("Nimittäjä", key="ticker_b")

    st.header("Näkymä")
    period = st.selectbox("Historia", ["1y", "2y", "5y", "10y", "max"], index=2)
    tf_name = st.selectbox("Kynttilän aikaväli", list(RESAMPLE_RULES), index=0)
    log_scale = st.checkbox("Logaritminen asteikko", value=True)
    sma_input = st.text_input("Liukuvat keskiarvot (pilkulla)", "20, 50")
    show_ratio_line = st.checkbox("Näytä myös pelkkä close-viiva", value=False)

ticker_a = st.session_state.ticker_a.strip().upper()
ticker_b = st.session_state.ticker_b.strip().upper()
sma_lengths = [int(p.strip()) for p in sma_input.split(",") if p.strip().isdigit()]


# --- Välilehdet ---------------------------------------------------------

tab_chart, tab_screen = st.tabs(["Graafi", "Yleiskatsaus"])

with tab_chart:
    st.subheader(f"{ticker_a} / {ticker_b}")
    if selite:
        st.caption(selite)

    try:
        with st.spinner("Haetaan dataa…"):
            a = cached_prices(ticker_a, period)
            b = cached_prices(ticker_b, period)
        ratio = resample_ohlc(ratio_ohlc(a, b), RESAMPLE_RULES[tf_name])
        ratio = add_sma(ratio, sma_lengths)
    except Exception as exc:  # noqa: BLE001 – näytetään virhe käyttäjälle
        st.error(f"Datan haku epäonnistui: {exc}")
        st.stop()

    if len(ratio) < 2:
        st.warning("Liian vähän dataa piirrettäväksi. Kokeile pidempää historiaa.")
        st.stop()

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=ratio.index,
            open=ratio["Open"],
            high=ratio["High"],
            low=ratio["Low"],
            close=ratio["Close"],
            name=f"{ticker_a}/{ticker_b}",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        )
    )
    if show_ratio_line:
        fig.add_trace(
            go.Scatter(
                x=ratio.index, y=ratio["Close"], name="Close",
                line=dict(width=1, color="#888888"),
            )
        )
    for n in sma_lengths:
        col = f"SMA{n}"
        if col in ratio:
            fig.add_trace(
                go.Scatter(x=ratio.index, y=ratio[col], name=col, line=dict(width=1.2))
            )

    fig.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, yanchor="bottom"),
        template="plotly_dark",
    )
    fig.update_yaxes(type="log" if log_scale else "linear")
    if RESAMPLE_RULES[tf_name] is None:
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

    st.plotly_chart(fig, width="stretch")

    s = summary(ratio)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Viimeisin", f"{s['viimeisin']:.4f}")
    c2.metric("Muutos jaksolla", f"{s['muutos_%']:+.1f} %")
    c3.metric("Jakson matalin", f"{s['min']:.4f}")
    c4.metric("Jakson korkein", f"{s['max']:.4f}")

    with st.expander("Data taulukkona"):
        st.dataframe(ratio.tail(250).iloc[::-1], width="stretch")

    st.caption(
        "Close-arvot ovat eksakteja. High/Low ovat suhteen teoreettiset ääriarvot "
        "kynttilän sisällä, eli hieman todellista leveämpiä. Data: Yahoo Finance, "
        "osingot ja splitit huomioitu."
    )

with tab_screen:
    st.subheader("Kaikki valmiit parit")
    st.caption(
        "Sijainti 52vk kertoo, missä kohtaa vuoden vaihteluväliä suhde on nyt: "
        "0 % = pohjalla, 100 % = huipulla."
    )
    if st.button("Laske yleiskatsaus"):
        with st.spinner("Haetaan noin 40 tickerin data, ensimmäinen kerta kestää hetken…"):
            df = screen(period)
        if df.empty:
            st.warning("Dataa ei saatu haettua.")
        else:
            st.dataframe(
                df.sort_values("3 kk %", ascending=False),
                width="stretch",
                hide_index=True,
                column_config={
                    c: st.column_config.NumberColumn(c, format="%.1f")
                    for c in ["1 kk %", "3 kk %", "12 kk %", "Sijainti 52vk %"]
                },
            )

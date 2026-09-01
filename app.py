"""Suhdelukugraafi kahdelle instrumentille, esim. HYG/IEF.

Käynnistys:  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import streamlit.components.v1 as components

from chart import PLOTLY_CONFIG, build_figure, resizable_html
from core import (
    PERIODS_BY_INTERVAL,
    TIMEFRAMES,
    add_sma,
    load_prices,
    ratio_ohlc,
    resample_ohlc,
    summary,
)
from presets import PRESETS, flat

st.set_page_config(page_title="Suhdelukugraafi", layout="wide")

FLAT = flat()
OMA = "— oma valinta —"

# Oletusvalinnat käynnistyksessä.
VAKIO_KYNTTILA = "Päivä"   # mikä tahansa avain core.TIMEFRAMES-sanakirjasta
VAKIO_HISTORIA = "1y"      # käytetään jos aikaväli sallii, muuten pisin mahdollinen

for key, value in {
    "cat": "Luottoriski",
    "pair": "HYG / IEF",
    "ticker_a": "HYG",
    "ticker_b": "IEF",
}.items():
    st.session_state.setdefault(key, value)


# --- Datan haku ---------------------------------------------------------

@st.cache_data(ttl=900, show_spinner=False)
def cached_prices(ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
    return load_prices(ticker, period=period, interval=interval)


def _pct(series: pd.Series, bars: int) -> float:
    if len(series) <= bars:
        return float("nan")
    return float((series.iloc[-1] / series.iloc[-1 - bars] - 1) * 100)


@st.cache_data(ttl=900, show_spinner=False)
def screen(period: str = "2y") -> pd.DataFrame:
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

    st.header("Aikaväli")
    tf_names = list(TIMEFRAMES)
    tf_name = st.selectbox("Kynttilä", tf_names, index=tf_names.index(VAKIO_KYNTTILA))
    interval, rule = TIMEFRAMES[tf_name]
    periods = PERIODS_BY_INTERVAL[interval]
    period = st.selectbox(
        "Historia",
        periods,
        index=periods.index(VAKIO_HISTORIA) if VAKIO_HISTORIA in periods else len(periods) - 1,
    )

    st.header("Indikaattorit")
    sma_input = st.text_input("Liukuvat keskiarvot (pilkulla)", "20, 50")
    show_rsi = st.checkbox("RSI", value=False)
    rsi_length = st.number_input("RSI pituus", 2, 100, 14, disabled=not show_rsi)
    show_macd = st.checkbox("MACD", value=False)
    log_scale = st.checkbox("Logaritminen asteikko", value=True)
    height = st.slider("Aloituskorkeus", 400, 1200, 760, step=20)
    resizable = st.checkbox("Raahattava korkeus", value=True)

ticker_a = st.session_state.ticker_a.strip().upper()
ticker_b = st.session_state.ticker_b.strip().upper()
sma_lengths = [int(p.strip()) for p in sma_input.split(",") if p.strip().isdigit()]


# --- Välilehdet ---------------------------------------------------------

tab_chart, tab_screen = st.tabs(["Graafi", "Yleiskatsaus"])

with tab_chart:
    head, metrics = st.columns([2, 3])
    head.subheader(f"{ticker_a} / {ticker_b}")

    try:
        with st.spinner("Haetaan dataa…"):
            a = cached_prices(ticker_a, period, interval)
            b = cached_prices(ticker_b, period, interval)
        ratio = add_sma(resample_ohlc(ratio_ohlc(a, b), rule), sma_lengths)
    except Exception as exc:  # noqa: BLE001 – näytetään virhe käyttäjälle
        st.error(f"Datan haku epäonnistui: {exc}")
        st.stop()

    if len(ratio) < 2:
        st.warning("Liian vähän dataa piirrettäväksi. Kokeile pidempää historiaa.")
        st.stop()

    s = summary(ratio)
    c1, c2, c3, c4 = metrics.columns(4)
    c1.metric("Viimeisin", f"{s['viimeisin']:.4f}")
    c2.metric("Muutos jaksolla", f"{s['muutos_%']:+.1f} %")
    c3.metric("Matalin", f"{s['min']:.4f}")
    c4.metric("Korkein", f"{s['max']:.4f}")

    if selite:
        st.caption(selite)

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
        st.caption(
            "Raahaa kuvaajan oikeasta alakulmasta muuttaaksesi korkeutta. Rulla zoomaa, "
            "veto panoroi, tuplaklikkaus palauttaa näkymän. Piirtotyökalut ovat oikean "
            "yläkulman työkalupalkissa, ja piirretyt viivat katoavat kun asetuksia vaihtaa."
        )
    else:
        st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)
        st.caption(
            "Rulla zoomaa, veto panoroi, tuplaklikkaus palauttaa näkymän. Piirtotyökalut "
            "ovat oikean yläkulman työkalupalkissa, ja piirretyt viivat katoavat kun "
            "asetuksia vaihtaa."
        )

    with st.expander("Data taulukkona"):
        st.dataframe(ratio.tail(300).iloc[::-1], width="stretch")

with tab_screen:
    st.subheader("Kaikki valmiit parit")
    st.caption(
        "Päivädataa kahden vuoden ajalta. Sijainti 52vk kertoo, missä kohtaa vuoden "
        "vaihteluväliä suhde on nyt: 0 % = pohjalla, 100 % = huipulla."
    )
    if st.button("Laske yleiskatsaus"):
        with st.spinner("Haetaan noin 40 tickerin data, ensimmäinen kerta kestää hetken…"):
            df = screen()
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

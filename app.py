"""Suhdelukugraafi kahdelle instrumentille, esim. HYG/IEF.

Käynnistys:  streamlit run app.py
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
    load_prices,
    ratio_ohlc,
    resample_ohlc,
    summary,
    taso,
    vaihteluvali,
)
from presets import PRESETS, Pair, all_pairs, flat
from tickers import kuvaus

st.set_page_config(page_title="Suhdelukugraafi", layout="wide")

FLAT = flat()
OMA = "— oma valinta —"

# Oletusvalinnat käynnistyksessä.
VAKIO_KYNTTILA = "Päivä"   # mikä tahansa avain core.TIMEFRAMES-sanakirjasta
VAKIO_HISTORIA = "1y"      # käytetään jos aikaväli sallii, muuten pisin mahdollinen
VAKIO_PARI = PRESETS["Luottoriski"][0]

for key, value in {
    "cat": "Luottoriski",
    "pair": VAKIO_PARI.label,
    "ticker_a": VAKIO_PARI.a,
    "ticker_b": VAKIO_PARI.b,
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


def _tulkinta(p: Pair, kolme_kk: float, yli_ka: bool, sijainti: float) -> tuple[str, str]:
    """Luokittele suunta ja muodosta lause siitä mitä se parille tarkoittaa."""
    if kolme_kk > 2 and yli_ka:
        tila, teksti = "Nouseva", p.nousu
    elif kolme_kk < -2 and not yli_ka:
        tila, teksti = "Laskeva", p.lasku
    else:
        tila, teksti = "Sivuttain", "ei selvää suuntaa"

    teksti = teksti[0].upper() + teksti[1:]
    if sijainti >= 90:
        teksti += ". Lähellä vuoden huippua"
    elif sijainti <= 10:
        teksti += ". Lähellä vuoden pohjaa"
    return tila, teksti


VERTAILU_PAIVIA = 756  # noin kolme vuotta pörssipäiviä


@st.cache_data(ttl=900, show_spinner=False)
def vertailuluvut(a: str, b: str) -> dict[str, float] | None:
    """Parin oma vaihteluväli kolmen vuoden päivädatasta."""
    try:
        ca = cached_prices(a, "5y")["Close"]
        cb = cached_prices(b, "5y")["Close"]
    except Exception:
        return None
    r = (ca / cb).dropna().tail(VERTAILU_PAIVIA)
    if len(r) < 200:
        return None
    return vaihteluvali(r)


@st.cache_data(ttl=900, show_spinner=False)
def screen(period: str = "2y") -> pd.DataFrame:
    """Laske kaikkien valmiiden parien muutokset ja tulkinta yhteen taulukkoon."""
    rows = []
    for cat, p in all_pairs():
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
        sijainti = float((window.iloc[-1] - window.min()) / span * 100) if span else float("nan")
        kolme_kk = _pct(r, 63)
        pros = float((r < r.iloc[-1]).mean() * 100)
        yli_ka = bool(r.iloc[-1] > r.rolling(50).mean().iloc[-1])
        tila, tulkinta = _tulkinta(p, kolme_kk, yli_ka, sijainti)

        rows.append(
            {
                "Teema": cat,
                "Pari": p.nimi,
                "Aihe": p.lyhyt,
                "Taso": taso(pros),
                "Tila": tila,
                "Tulkinta": tulkinta,
                "1 kk %": _pct(r, 21),
                "3 kk %": kolme_kk,
                "12 kk %": _pct(r, 252),
                "Sijainti 52vk %": sijainti,
            }
        )
    return pd.DataFrame(rows)


# --- Sivupalkki ---------------------------------------------------------

def on_cat_change() -> None:
    cat = st.session_state.cat
    if cat in PRESETS:
        p = PRESETS[cat][0]
        st.session_state.pair = p.label
        st.session_state.ticker_a = p.a
        st.session_state.ticker_b = p.b


def on_pair_change() -> None:
    p = FLAT.get(st.session_state.pair)
    if p:
        st.session_state.ticker_a = p.a
        st.session_state.ticker_b = p.b


with st.sidebar:
    st.header("Pari")
    st.selectbox("Teema", [OMA, *PRESETS], key="cat", on_change=on_cat_change)

    valittu: Pair | None = None
    if st.session_state.cat in PRESETS:
        options = [p.label for p in PRESETS[st.session_state.cat]]
        if st.session_state.pair not in options:
            st.session_state.pair = options[0]
        st.selectbox("Valmis pari", options, key="pair", on_change=on_pair_change)
        valittu = FLAT[st.session_state.pair]

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
    log_scale = st.checkbox("Logaritminen asteikko", value=False)
    height = st.slider("Aloituskorkeus", 400, 1200, 760, step=20)
    resizable = st.checkbox("Raahattava korkeus", value=True)

ticker_a = st.session_state.ticker_a.strip().upper()
ticker_b = st.session_state.ticker_b.strip().upper()
sma_lengths = [int(p.strip()) for p in sma_input.split(",") if p.strip().isdigit()]

# Selite näytetään vain jos tickerit vastaavat yhä valittua paria.
if valittu and (ticker_a, ticker_b) != (valittu.a, valittu.b):
    valittu = None


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

    if valittu:
        st.markdown(
            f"**{valittu.lyhyt}.** Nouseva käyrä: {valittu.nousu}. "
            f"Laskeva käyrä: {valittu.lasku}."
        )

    v = vertailuluvut(ticker_a, ticker_b)
    if v:
        nyt_taso = taso(v["persentiili"])
        merkitys = {
            "Korkea": valittu.nousu if valittu else "suhde on historiansa yläpäässä",
            "Matala": valittu.lasku if valittu else "suhde on historiansa alapäässä",
            "Normaali": "taso on tavanomainen",
        }[nyt_taso]
        st.info(
            f"**{nyt_taso}: {v['nyt']:.4f}** on korkeampi kuin "
            f"{v['persentiili']:.0f} % kolmen vuoden havainnoista. "
            f"Matala alle {v['matala']:.4f}, mediaani {v['mediaani']:.4f}, "
            f"korkea yli {v['korkea']:.4f}. "
            f"{merkitys[0].upper() + merkitys[1:]}."
        )

    if valittu and valittu.vakiintuneet:
        st.warning(valittu.vakiintuneet)

    kuvaus_a, kuvaus_b = kuvaus(ticker_a), kuvaus(ticker_b)
    if kuvaus_a or kuvaus_b:
        with st.expander("Mistä pari koostuu"):
            if kuvaus_a:
                st.markdown(f"**{ticker_a}** (osoittaja). {kuvaus_a}")
            if kuvaus_b:
                st.markdown(f"**{ticker_b}** (nimittäjä). {kuvaus_b}")
            if valittu:
                st.markdown(
                    f"**Pari.** {valittu.lyhyt}: suhde nousee kun {ticker_a} pärjää "
                    f"{ticker_b}:tä paremmin, jolloin {valittu.nousu}."
                )

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

    with st.expander("Data taulukkona"):
        st.dataframe(ratio.tail(300).iloc[::-1], width="stretch")

with tab_screen:
    st.subheader("Kaikki valmiit parit")
    st.caption(
        "Päivädataa kahden vuoden ajalta. Tila perustuu 3 kk muutokseen ja 50 päivän "
        "keskiarvoon. Sijainti 52vk kertoo missä kohtaa vuoden vaihteluväliä suhde on: "
        "0 % = pohjalla, 100 % = huipulla."
    )
    if st.button("Laske yleiskatsaus"):
        with st.spinner("Haetaan noin 40 tickerin data, ensimmäinen kerta kestää hetken…"):
            df = screen()
        if df.empty:
            st.warning("Dataa ei saatu haettua.")
        else:
            yhteenveto = digest.build(df)
            st.markdown(f"### Kokonaiskuva\n{yhteenveto['kappale']}")

            if yhteenveto["ristiriidat"]:
                for rivi in yhteenveto["ristiriidat"]:
                    st.warning(rivi)

            if yhteenveto["poikkeamat"]:
                st.markdown("**Poikkeavat liikkeet**")
                for rivi in yhteenveto["poikkeamat"]:
                    st.markdown(f"- {rivi}")

            st.divider()
            st.dataframe(
                df.sort_values("3 kk %", ascending=False),
                width="stretch",
                hide_index=True,
                column_config={
                    c: st.column_config.NumberColumn(c, format="%.1f")
                    for c in ["1 kk %", "3 kk %", "12 kk %", "Sijainti 52vk %"]
                },
            )

"""Suhdelukukynttilöiden laskenta (esim. HYG/IEF).

Tässä moduulissa ei ole riippuvuutta Streamlitiin, jotta logiikan voi testata
erikseen ja käyttää myös skriptistä.
"""

from __future__ import annotations

import pandas as pd

OHLC = ["Open", "High", "Low", "Close"]

# Aikavälit, joihin päivädata voidaan tiivistää paikallisesti.
RESAMPLE_RULES: dict[str, str | None] = {
    "Päivä": None,
    "Viikko": "W-FRI",
    "Kuukausi": "ME",
    "Kvartaali": "QE",
}


def load_prices(ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Hae OHLC-data Yahoo Financesta. Palauttaa DataFramen sarakkeilla OHLC."""
    import yfinance as yf  # tuodaan tässä, jotta testit toimivat ilman verkkoa

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    if df is None or df.empty:
        raise ValueError(f"Tickerille '{ticker}' ei löytynyt dataa.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[OHLC].dropna().sort_index()


def ratio_ohlc(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Rakenna suhdeluvun A/B kynttilät kahdesta OHLC-sarjasta.

    Open ja Close ovat suoria jakolaskuja. High ja Low ovat suhteen teoreettiset
    ääriarvot saman kynttilän sisällä (A.High/B.Low ja A.Low/B.High), rajattuna
    niin että High >= max(Open, Close) ja Low <= min(Open, Close).

    Huom: tämä on yläraja-arvio, koska emme tiedä osuivatko A:n huippu ja B:n
    pohja samaan hetkeen. Close-sarja on aina eksakti.
    """
    idx = a.index.intersection(b.index)
    if len(idx) == 0:
        raise ValueError("Sarjoilla ei ole yhtään yhteistä päivämäärää.")
    a, b = a.loc[idx], b.loc[idx]

    r = pd.DataFrame(index=idx)
    r["Open"] = a["Open"] / b["Open"]
    r["Close"] = a["Close"] / b["Close"]
    hi = a["High"] / b["Low"]
    lo = a["Low"] / b["High"]
    r["High"] = pd.concat([hi, r["Open"], r["Close"]], axis=1).max(axis=1)
    r["Low"] = pd.concat([lo, r["Open"], r["Close"]], axis=1).min(axis=1)
    return r[OHLC].dropna()


def resample_ohlc(df: pd.DataFrame, rule: str | None) -> pd.DataFrame:
    """Tiivistä OHLC-data harvempaan aikaväliin (esim. viikko tai kuukausi)."""
    if rule is None:
        return df
    out = df.resample(rule).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    )
    return out.dropna()


def add_sma(df: pd.DataFrame, lengths: list[int]) -> pd.DataFrame:
    """Lisää liukuvat keskiarvot Close-sarjasta."""
    out = df.copy()
    for n in lengths:
        if n and n > 1:
            out[f"SMA{n}"] = out["Close"].rolling(n).mean()
    return out


def summary(df: pd.DataFrame) -> dict[str, float]:
    """Muutamia tunnuslukuja suhdeluvun kehityksestä."""
    close = df["Close"]
    return {
        "viimeisin": float(close.iloc[-1]),
        "muutos_%": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
        "min": float(close.min()),
        "max": float(close.max()),
    }

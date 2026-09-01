"""Suhdelukukynttilöiden laskenta (esim. HYG/IEF).

Tässä moduulissa ei ole riippuvuutta Streamlitiin, jotta logiikan voi testata
erikseen ja käyttää myös skriptistä.
"""

from __future__ import annotations

import pandas as pd

OHLC = ["Open", "High", "Low", "Close"]

# Aikaväli -> (Yahoon interval, paikallinen resample-sääntö tai None).
# Yahoo tarjoaa vain osan aikaväleistä, loput tiivistetään itse.
TIMEFRAMES: dict[str, tuple[str, str | None]] = {
    "1 min": ("1m", None),
    "5 min": ("5m", None),
    "15 min": ("15m", None),
    "30 min": ("30m", None),
    "1 h": ("1h", None),
    "2 h": ("1h", "2h"),
    "4 h": ("1h", "4h"),
    "Päivä": ("1d", None),
    "Viikko": ("1d", "W-FRI"),
    "Kuukausi": ("1d", "ME"),
    "Kvartaali": ("1d", "QE"),
}

# Yahoon historiarajat intraday-datalle. Näistä poikkeaminen palauttaa tyhjän.
PERIODS_BY_INTERVAL: dict[str, list[str]] = {
    "1m": ["1d", "5d"],
    "5m": ["5d", "1mo"],
    "15m": ["5d", "1mo"],
    "30m": ["5d", "1mo"],
    "1h": ["1mo", "3mo", "6mo", "1y", "2y"],
    "1d": ["6mo", "1y", "2y", "5y", "10y", "max"],
}

INTRADAY = {"1m", "5m", "15m", "30m", "1h"}


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
        raise ValueError(f"Tickerille '{ticker}' ei löytynyt dataa jaksolla {period}.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[OHLC].dropna().sort_index()


def ratio_ohlc(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Rakenna suhdeluvun A/B kynttilät kahdesta OHLC-sarjasta.

    Open ja Close ovat suoria jakolaskuja. High ja Low ovat suhteen teoreettiset
    ääriarvot saman kynttilän sisällä (A.High/B.Low ja A.Low/B.High), rajattuna
    niin että High >= max(Open, Close) ja Low <= min(Open, Close).
    """
    idx = a.index.intersection(b.index)
    if len(idx) == 0:
        raise ValueError("Sarjoilla ei ole yhtään yhteistä aikaleimaa.")
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
    """Tiivistä OHLC-data harvempaan aikaväliin."""
    if rule is None or df.empty:
        return df
    kwargs = {}
    if rule.endswith("h"):
        # Intraday: aloita ryhmittely ensimmäisestä kynttilästä eli pörssin
        # avauksesta, ei keskiyöstä.
        kwargs["origin"] = "start"
    out = df.resample(rule, **kwargs).agg(
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


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Wilderin RSI. Sama laskutapa kuin TradingView'n oletus-RSI:ssä."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """MACD-viiva, signaaliviiva ja histogrammi."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    line = ema_fast - ema_slow
    sig = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"MACD": line, "Signal": sig, "Hist": line - sig})


def summary(df: pd.DataFrame) -> dict[str, float]:
    """Muutamia tunnuslukuja suhdeluvun kehityksestä."""
    close = df["Close"]
    return {
        "viimeisin": float(close.iloc[-1]),
        "muutos_%": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
        "min": float(close.min()),
        "max": float(close.max()),
    }

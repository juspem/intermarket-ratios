"""Ratio candle maths for pairs like HYG/IEF.

No Streamlit imports here, so the logic can be tested on its own or used from
a plain script.
"""

from __future__ import annotations

import pandas as pd

OHLC = ["Open", "High", "Low", "Close"]

# Timeframe -> (Yahoo interval, local resample rule or None).
# Yahoo only serves a few intervals, so the rest are aggregated here.
TIMEFRAMES: dict[str, tuple[str, str | None]] = {
    "1 min": ("1m", None),
    "5 min": ("5m", None),
    "15 min": ("15m", None),
    "30 min": ("30m", None),
    "1 hour": ("1h", None),
    "2 hours": ("1h", "2h"),
    "4 hours": ("1h", "4h"),
    "Daily": ("1d", None),
    "Weekly": ("1d", "W-FRI"),
    "Monthly": ("1d", "ME"),
    "Quarterly": ("1d", "QE"),
}

# How far back Yahoo will go for each interval. Ask for more and you get nothing.
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
    """Fetch OHLC data from Yahoo Finance."""
    import yfinance as yf  # imported here so tests run without a network

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    if df is None or df.empty:
        raise ValueError(f"No data for '{ticker}' over {period}.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[OHLC].dropna().sort_index()


def ratio_ohlc(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Build A/B candles from two OHLC frames.

    Open and Close are plain divisions. High and Low are the widest the ratio
    could have been inside the bar (A.High/B.Low and A.Low/B.High), clamped so
    the candle body still fits inside the wicks.
    """
    idx = a.index.intersection(b.index)
    if len(idx) == 0:
        raise ValueError("The two series share no timestamps.")
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
    """Aggregate candles into a longer timeframe."""
    if rule is None or df.empty:
        return df
    kwargs = {}
    if rule.endswith("h"):
        # Start intraday buckets at the first bar, which is the market open,
        # rather than at midnight.
        kwargs["origin"] = "start"
    out = df.resample(rule, **kwargs).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    )
    return out.dropna()


def add_sma(df: pd.DataFrame, lengths: list[int]) -> pd.DataFrame:
    """Add simple moving averages of the close."""
    out = df.copy()
    for n in lengths:
        if n and n > 1:
            out[f"SMA{n}"] = out["Close"].rolling(n).mean()
    return out


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Wilder's RSI, the same smoothing TradingView uses by default."""
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
    """MACD line, signal line and histogram."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    line = ema_fast - ema_slow
    sig = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"MACD": line, "Signal": sig, "Hist": line - sig})


def percentile_range(close: pd.Series, low: int = 10, high: int = 90) -> dict[str, float]:
    """Where the ratio sits within its own history.

    The absolute number on a ratio chart means nothing on its own, since it
    only reflects the two share prices. So the thresholds come from the series
    itself as percentiles.
    """
    s = close.dropna()
    now = float(s.iloc[-1])
    return {
        "low": float(s.quantile(low / 100)),
        "median": float(s.quantile(0.5)),
        "high": float(s.quantile(high / 100)),
        "now": now,
        "percentile": float((s < now).mean() * 100),
        "observations": int(len(s)),
    }


def level(percentile: float, low: int = 10, high: int = 90) -> str:
    """Turn a percentile into a word."""
    if percentile >= high:
        return "High"
    if percentile <= low:
        return "Low"
    return "Normal"


def summary(df: pd.DataFrame) -> dict[str, float]:
    """A few headline numbers for the visible window."""
    close = df["Close"]
    return {
        "last": float(close.iloc[-1]),
        "change_pct": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
        "min": float(close.min()),
        "max": float(close.max()),
    }

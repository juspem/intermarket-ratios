"""A written summary of the overview table, built without a network call.

Sentences are assembled from fixed pieces, so the language is stiff but it is
free, offline and repeatable. The same numbers could later be handed to a
language model if you want something that reads better.
"""

from __future__ import annotations

import pandas as pd

from presets import Pair, all_pairs

DIRECTION = {"Rising": 1, "Falling": -1, "Flat": 0}

# Thresholds for calling something out separately.
BIG_MOVE = 10.0        # percent over three months
NEAR_HIGH = 95.0       # position in the 52 week range
NEAR_LOW = 5.0


def _pairs() -> dict[str, Pair]:
    return {p.name: p for _, p in all_pairs()}


def _rows(df: pd.DataFrame) -> list[dict]:
    """Join the table rows back to the pair definitions."""
    pairs = _pairs()
    out = []
    for row in df.to_dict("records"):
        p = pairs.get(row["Pair"])
        if p is None:
            continue
        out.append({**row, "pair": p, "direction": DIRECTION.get(row["State"], 0)})
    return out


def _theme_scores(rows: list[dict], minimum: int = 2) -> dict[str, float]:
    """Average risk tone per theme, +1 for risk taking and -1 for caution.

    Themes with only one meaningful signal are skipped, since one pair moving
    says nothing about where a theme is headed.
    """
    scores: dict[str, list[float]] = {}
    for r in rows:
        if r["pair"].risk:
            scores.setdefault(r["Theme"], []).append(r["pair"].risk * r["direction"])
    return {k: sum(v) / len(v) for k, v in scores.items() if len(v) >= minimum}


def paragraph(df: pd.DataFrame) -> str:
    """One paragraph on the overall picture."""
    rows = _rows(df)
    signals = [r for r in rows if r["pair"].risk and r["direction"]]
    if not signals:
        return (
            f"None of the {len(rows)} pairs is showing a clear direction. "
            "There is no single tone to the market right now."
        )

    on = [r for r in signals if r["pair"].risk * r["direction"] > 0]
    off = [r for r in signals if r["pair"].risk * r["direction"] < 0]
    share = len(on) / len(signals)

    if share >= 0.65:
        tone = "Risk taking is the dominant tone"
    elif share <= 0.35:
        tone = "Caution is the dominant tone"
    else:
        tone = "The picture is split"

    parts = [
        f"{tone}: {len(on)} pairs point to risk taking and {len(off)} to caution, "
        f"with the other {len(rows) - len(signals)} going sideways."
    ]

    movers = sorted(signals, key=lambda r: abs(r["3M %"]), reverse=True)[:2]
    if movers:
        names = " and ".join(f"{r['Pair']} ({r['3M %']:+.1f}%)" for r in movers)
        parts.append(f"The biggest movers are {names}.")

    breadth = next((r for r in rows if r["Pair"] == "RSP / SPY"), None)
    if breadth and breadth["direction"]:
        if breadth["direction"] > 0:
            parts.append("Breadth is backing the move.")
        else:
            parts.append("Breadth is narrowing, so few names are doing the work.")

    return " ".join(parts)


def outliers(df: pd.DataFrame, limit: int = 5) -> list[str]:
    """Moves and extremes worth a separate mention."""
    out: list[tuple[float, str]] = []
    for r in _rows(df):
        move, pos = r["3M %"], r["52w position %"]
        notes = []
        if pd.notna(move) and abs(move) >= BIG_MOVE:
            notes.append(f"{move:+.1f}% in three months")
        if pd.notna(pos) and pos >= NEAR_HIGH:
            notes.append("at its yearly high")
        elif pd.notna(pos) and pos <= NEAR_LOW:
            notes.append("at its yearly low")
        if notes:
            text = f"{r['Pair']} ({r['pair'].topic}): {', '.join(notes)}. {r['Reading']}."
            out.append((abs(move) if pd.notna(move) else 0.0, text))
    out.sort(reverse=True)
    return [t for _, t in out[:limit]]


def conflicts(df: pd.DataFrame) -> list[str]:
    """Themes that are telling different stories."""
    scores = _theme_scores(_rows(df))
    positive = [k for k, v in scores.items() if v >= 0.34]
    negative = [k for k, v in scores.items() if v <= -0.34]
    if not positive or not negative:
        return []
    return [
        f"{a} points to risk taking while {b} points to caution."
        for a in positive
        for b in negative
    ][:3]


def build(df: pd.DataFrame) -> dict[str, object]:
    """The whole summary in one structure."""
    return {
        "paragraph": paragraph(df),
        "outliers": outliers(df),
        "conflicts": conflicts(df),
    }

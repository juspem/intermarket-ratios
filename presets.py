"""Preset ratio pairs grouped by theme.

Every pair carries a short topic for the dropdown plus a line on what a rising
and a falling ratio each say. The same text feeds the chart caption and the
overview reading, so it only has to be written once.
"""

from __future__ import annotations

from typing import NamedTuple


class Pair(NamedTuple):
    a: str            # numerator
    b: str            # denominator
    topic: str        # a few words for the dropdown
    rising: str       # what a rising ratio tells you
    falling: str      # what a falling ratio tells you
    risk: int = 0     # +1 rising means risk taking, -1 means caution, 0 neither
    convention: str = ""  # only where investors agree on actual threshold values
    note: str = ""        # a quirk of this specific pair worth knowing before you read it

    @property
    def name(self) -> str:
        return f"{self.a} / {self.b}"

    @property
    def label(self) -> str:
        return f"{self.a} / {self.b} · {self.topic}"


# Why each family of ratios is worth watching at all. One level up from the
# per-pair lines, so the same mechanism does not get explained five times.
THEMES: dict[str, str] = {
    "Credit risk": (
        "Credit is usually where trouble shows up first. Companies have to keep "
        "rolling their debt, so when lenders start demanding more compensation, "
        "the weakest borrowers feel it long before it reaches an equity index. "
        "That is why a falling credit ratio while stocks are still rising is worth "
        "paying attention to. The catch is that credit also throws false alarms, "
        "and a widening spread often just reflects fund flows rather than any real "
        "deterioration in company finances."
    ),
    "Risk appetite in equities": (
        "These pairs ask whether investors are reaching for the volatile end of the "
        "market or backing away from it. The index level itself can stay flat while "
        "the money underneath rotates hard, and that rotation tends to show up here "
        "first. None of these ratios predicts anything on its own, but when several "
        "of them turn together it usually means the crowd has changed its mind about "
        "how much risk it wants to hold."
    ),
    "Sector leadership": (
        "Which sector leads tells you what part of the economy the market believes "
        "in. Semiconductors and transport are early cyclicals, so they tend to turn "
        "before the broad index does. Leadership changes are slow and messy though, "
        "and a sector can lag for a year for reasons that have nothing to do with the "
        "economy, such as one enormous constituent having a bad time."
    ),
    "Style": (
        "Value against growth is mostly a story about interest rates. Growth "
        "companies promise cash a long way into the future, so a higher discount "
        "rate hurts them more than it hurts a company earning money today. These "
        "cycles run for years rather than months, which makes the ratio useless for "
        "timing but useful for understanding why a portfolio is behaving the way it is."
    ),
    "Defensive warning": (
        "Staples and utilities do well when investors want certainty rather than "
        "upside. The interesting case is a defensive ratio rising while the index is "
        "also rising, because that means the money going in is going into the safe "
        "corners. Utilities complicate this: they are also a rate play, so they can "
        "climb simply because yields fell, with no fear involved at all."
    ),
    "Rates and inflation": (
        "These are rough proxies built from bond funds rather than actual yield data. "
        "TIP against IEF approximates what the market expects inflation to be, and the "
        "duration pairs reflect the shape of the curve. They move in the right "
        "direction but the levels are not precise, because the funds differ in duration "
        "and holdings. Use them for direction, not for a number you would quote."
    ),
    "Commodities and gold": (
        "Gold responds mainly to real interest rates and to fear, which is why it is "
        "paired here against both stocks and bonds. Copper against gold is the "
        "classic growth thermometer and tracks the ten year yield reasonably well. "
        "Anything built on futures, which means CPER and DBC, carries roll cost, so "
        "the fund can drift away from the spot price over long periods."
    ),
    "Regions": (
        "Relative country performance is driven by two things that often get "
        "confused. The first is the dollar, since these funds are unhedged and a "
        "falling dollar flatters everything priced outside the US. The second is "
        "index composition: the S&P is full of technology while EAFE is full of banks "
        "and industrials, so EFA against SPY is partly a sector bet wearing a "
        "geography costume."
    ),
}


PRESETS: dict[str, list[Pair]] = {
    "Credit risk": [
        Pair("HYG", "IEF", "Appetite for credit risk",
             "investors are happy to hold credit risk",
             "money is moving into government bonds", 1,
             note="HYG carries around three years of duration and IEF around seven, so part of any move here is a rate move rather than a credit move. HYG/LQD exists to strip that out."),
        Pair("HYG", "LQD", "Demand for credit quality",
             "buyers will take weaker credit quality",
             "quality is preferred over junk", 1),
        Pair("LQD", "IEF", "Corporate spread",
             "the corporate spread is tightening",
             "investors want more compensation for corporate debt", 1),
        Pair("JNK", "TLT", "Junk against long rates",
             "risk taking beats duration",
             "long government bonds are winning", 1),
        Pair("EMB", "IEF", "Emerging market debt",
             "emerging market debt is in demand",
             "the emerging market premium is widening", 1),
    ],
    "Risk appetite in equities": [
        Pair("SPY", "TLT", "Stocks against bonds",
             "stocks are beating bonds",
             "money is rotating into bonds", 1),
        Pair("XLY", "XLP", "Consumer risk appetite",
             "consumers are spending on the optional stuff",
             "spending is falling back to essentials", 1),
        Pair("SPHB", "SPLV", "High beta against low vol",
             "risk taking is clearly picking up",
             "investors are running from volatility", 1),
        Pair("IWM", "SPY", "Small caps against large",
             "risk taking reaches down into small caps",
             "safety is found in the large caps", 1),
        Pair("RSP", "SPY", "Market breadth",
             "a wide group of companies is carrying the rally",
             "a handful of giants is carrying the whole market", 1,
             note="This one is mechanical rather than interpretive. It measures concentration directly, since both funds hold the same companies and only the weights differ."),
        Pair("XLI", "XLU", "Cyclical against defensive",
             "the market believes in growth",
             "money is moving to defensive sectors", 1),
    ],
    "Sector leadership": [
        Pair("SMH", "SPY", "Semiconductor pull",
             "the tech cycle is strengthening",
             "the tech cycle is stalling", 1,
             note="SMH is very concentrated. A handful of names drives most of it, so this says more about a few large chip companies than about the sector as a whole."),
        Pair("XLK", "SPY", "Technology leadership",
             "technology is leading the market",
             "technology is falling behind", 1),
        Pair("XLE", "SPY", "Energy pull",
             "energy and inflation pressure are building",
             "energy is falling behind", 0),
        Pair("XLF", "SPY", "Financials leadership",
             "financials are strengthening",
             "financials are falling behind", 1),
        Pair("KRE", "XLF", "Regional bank stress",
             "pressure on regional banks is easing",
             "regional banks are under stress", 1,
             note="KRE is equally weighted and XLF is cap weighted, so this is really small and mid sized banks against the giants."),
        Pair("XLV", "SPY", "Health care pull",
             "the defensive tilt is strengthening",
             "health care is falling behind", -1),
        Pair("IYT", "SPY", "Transport confirmation",
             "the real economy is pulling its weight",
             "transport is warning of a slowdown", 1),
        Pair("ITB", "SPY", "Homebuilder pull",
             "rate expectations favour housing",
             "rate pressure is weighing on builders", 1),
    ],
    "Style": [
        Pair("IWD", "IWF", "Value against growth",
             "value leads, which usually goes with rising rates",
             "growth leads, which usually goes with falling rates", 0),
        Pair("IVE", "IVW", "Value against growth (S&P)",
             "value leads inside the S&P 500",
             "growth leads inside the S&P 500", 0),
        Pair("MTUM", "SPY", "Momentum pull",
             "existing trends keep working",
             "momentum is unwinding and leadership is changing", 0),
        Pair("QQQ", "SPY", "Growth leadership",
             "the big growth names are leading",
             "leadership is moving away from growth", 0),
        Pair("QQQ", "IWM", "Large against small",
             "money is concentrating in the big names",
             "risk taking is spreading into small caps", -1),
    ],
    "Defensive warning": [
        Pair("XLP", "SPY", "Defensive warning",
             "money is hiding in consumer staples",
             "risk appetite looks normal", -1),
        Pair("XLU", "SPY", "Utilities as shelter",
             "investors are sheltering in utilities",
             "nobody is interested in defensives", -1),
        Pair("IEF", "SPY", "Bonds against stocks",
             "bonds are beating stocks",
             "stocks are beating bonds", -1),
    ],
    "Rates and inflation": [
        Pair("TIP", "IEF", "Inflation expectations",
             "inflation expectations are rising",
             "inflation expectations are falling", 0,
             note="A crude breakeven proxy. The two funds do not have matching duration, so the level drifts from the real breakeven rate even when the direction is right."),
        Pair("SHY", "TLT", "Duration risk",
             "long duration is hurting as rates rise",
             "long rates are coming down", 0,
             note="This is a duration ratio, not the yield curve. It moves with the curve but you cannot read a spread off it."),
        Pair("IEF", "TLT", "The long end",
             "the long end is weakening against the belly",
             "the long end is strengthening", 0),
    ],
    "Commodities and gold": [
        Pair("GLD", "SPY", "Gold against stocks",
             "money is looking for shelter in gold",
             "stocks are beating gold", -1),
        Pair("GLD", "TLT", "Real rates",
             "real rates are falling and gold beats bonds",
             "bonds are beating gold", 0),
        Pair("GLD", "SLV", "Gold to silver",
             "macro fear is building",
             "confidence in the cycle is coming back", -1,
             "This is the one pair with thresholds investors actually agree on. "
             "A gold to silver ratio above 80 counts as high and below 50 as low. "
             "The number on this chart is about a tenth of that, because GLD holds "
             "roughly 0.09 ounces of gold per share and SLV roughly 0.9 ounces of "
             "silver. Multiply what you see by about ten to compare it."),
        Pair("GDX", "GLD", "Miner leverage",
             "miners are geared into gold's rise",
             "miners are lagging gold", 0,
             note="Miners are equities as well as a gold play, so they can fall with the stock market even when gold itself is fine."),
        Pair("CPER", "GLD", "Copper to gold",
             "growth expectations are firming",
             "growth expectations are fading", 1,
             note="CPER holds copper futures and trades thinly. Roll cost pulls it away from the spot copper price over long horizons."),
        Pair("DBC", "SPY", "Commodities against stocks",
             "commodity pressure is building",
             "commodities are lagging equities", 0),
    ],
    "Regions": [
        Pair("EFA", "SPY", "Developed ex-US against US",
             "Europe and Japan are leading",
             "the United States is leading", 0,
             note="Unhedged, so a large part of this is simply the dollar."),
        Pair("EEM", "SPY", "Emerging against US",
             "emerging markets are pulling, often on a soft dollar",
             "the United States is beating emerging markets", 1,
             note="Unhedged and heavily weighted toward China and Taiwan, so it is as much a China call as an emerging markets one."),
        Pair("EEM", "EFA", "Emerging against developed",
             "emerging markets lead the rest of the world ex-US",
             "developed ex-US markets are leading", 1),
        Pair("FXI", "EEM", "China's share",
             "China is pulling the emerging market complex",
             "China is lagging the rest of emerging markets", 0),
        Pair("EWJ", "SPY", "Japan against US",
             "Japan is leading",
             "the United States is leading", 0),
    ],
}


def flat() -> dict[str, Pair]:
    """Pairs keyed by their dropdown label."""
    return {p.label: p for items in PRESETS.values() for p in items}


def all_pairs() -> list[tuple[str, Pair]]:
    """Every pair together with its theme."""
    return [(theme, p) for theme, items in PRESETS.items() for p in items]


def all_tickers() -> list[str]:
    seen: list[str] = []
    for _, p in all_pairs():
        for t in (p.a, p.b):
            if t not in seen:
                seen.append(t)
    return seen

"""What each ETF in the preset pairs actually holds.

Short descriptions only: what is inside the fund and what job it does in a pair.
"""

from __future__ import annotations

TICKERS: dict[str, str] = {
    # Rates and credit
    "HYG": "iShares iBoxx High Yield. US junk bonds, meaning corporate debt rated below investment grade.",
    "JNK": "SPDR Bloomberg High Yield. Same asset class as HYG, slightly different index and holdings.",
    "LQD": "iShares iBoxx Investment Grade. Higher quality corporate debt, duration around eight years.",
    "IEF": "iShares 7-10 Year Treasury. US government bonds from the middle of the curve.",
    "TLT": "iShares 20+ Year Treasury. Government bonds past 20 years, very sensitive to rates.",
    "SHY": "iShares 1-3 Year Treasury. Short government bonds with almost no duration risk.",
    "TIP": "iShares TIPS Bond. Inflation-protected government bonds.",
    "EMB": "iShares J.P. Morgan USD Emerging Markets Bond. Emerging market debt issued in dollars.",
    # Broad equity
    "SPY": "SPDR S&P 500. The 500 largest US companies weighted by market cap.",
    "QQQ": "Invesco QQQ. The Nasdaq 100, so the biggest listed names minus financials.",
    "IWM": "iShares Russell 2000. Roughly 2000 US small caps.",
    "RSP": "Invesco S&P 500 Equal Weight. Same companies as SPY, but every one gets the same weight.",
    # Factors and style
    "SPHB": "Invesco S&P 500 High Beta. The hundred S&P names that move most with the market.",
    "SPLV": "Invesco S&P 500 Low Volatility. The hundred steadiest S&P names.",
    "IWD": "iShares Russell 1000 Value. Value names from large and mid caps.",
    "IWF": "iShares Russell 1000 Growth. Growth names from the same universe.",
    "IVE": "iShares S&P 500 Value. The value half of the S&P 500.",
    "IVW": "iShares S&P 500 Growth. The growth half of the S&P 500.",
    "MTUM": "iShares MSCI USA Momentum Factor. Companies that have risen most over recent months.",
    # Sectors
    "XLY": "Consumer Discretionary SPDR. Things people buy when they feel comfortable, like Amazon and Home Depot.",
    "XLP": "Consumer Staples SPDR. Everyday goods, like Procter & Gamble and Walmart.",
    "XLI": "Industrial SPDR. Machinery, aerospace and industrial conglomerates.",
    "XLU": "Utilities SPDR. Power and water companies, defensive but also rate sensitive.",
    "XLK": "Technology SPDR. Software, hardware and semiconductors.",
    "XLE": "Energy SPDR. Oil and gas producers and refiners.",
    "XLF": "Financial SPDR. Banks, insurers and asset managers.",
    "XLV": "Health Care SPDR. Pharma, devices and health insurers.",
    "SMH": "VanEck Semiconductor. Chip makers, concentrated in the biggest names.",
    "KRE": "SPDR S&P Regional Banking. US regional banks, equally weighted.",
    "IYT": "iShares U.S. Transportation. Railroads, freight and airlines.",
    "ITB": "iShares U.S. Home Construction. Homebuilders and building product suppliers.",
    # Commodities
    "GLD": "SPDR Gold Shares. Physical gold, roughly 0.09 ounces per share.",
    "SLV": "iShares Silver Trust. Physical silver, roughly 0.9 ounces per share.",
    "GDX": "VanEck Gold Miners. Gold mining companies, which move further than gold itself.",
    "CPER": "United States Copper Index Fund. Copper futures. Thin volume and roll drag, so treat it with care.",
    "DBC": "Invesco DB Commodity Index. A broad futures basket that leans heavily on energy.",
    # Regions
    "EFA": "iShares MSCI EAFE. Developed markets outside the United States.",
    "EEM": "iShares MSCI Emerging Markets. Emerging market equities.",
    "FXI": "iShares China Large-Cap. Large Chinese companies listed in Hong Kong.",
    "EWJ": "iShares MSCI Japan. Japanese equities priced in dollars.",
}


def describe(ticker: str) -> str:
    return TICKERS.get(ticker.upper(), "")

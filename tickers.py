"""Mitä kukin pareissa käytetty ETF sisältää.

Lyhyt kuvaus riittää: mitä rahasto omistaa ja mikä sen rooli parissa on.
"""

from __future__ import annotations

TICKERS: dict[str, str] = {
    # Korot ja luotto
    "HYG": "iShares iBoxx High Yield. Yhdysvaltalaisia roskalainoja eli alle investment grade -luokituksen yrityslainoja.",
    "JNK": "SPDR Bloomberg High Yield. Sama omaisuusluokka kuin HYG, hieman eri indeksi ja koostumus.",
    "LQD": "iShares iBoxx Investment Grade. Hyvän luottoluokituksen yrityslainoja, duraatio noin kahdeksan vuotta.",
    "IEF": "iShares 7-10 Year Treasury. Yhdysvaltain valtionlainoja keskipitkästä päästä.",
    "TLT": "iShares 20+ Year Treasury. Yli 20 vuoden valtionlainoja, erittäin korkoherkkä.",
    "SHY": "iShares 1-3 Year Treasury. Lyhyet valtionlainat, lähes koroton riski.",
    "TIP": "iShares TIPS Bond. Inflaatiosuojattuja valtionlainoja.",
    "EMB": "iShares J.P. Morgan USD Emerging Markets Bond. Kehittyvien maiden dollarimääräistä velkaa.",
    # Laajat osakeindeksit
    "SPY": "SPDR S&P 500. Yhdysvaltain 500 suurinta yhtiötä markkina-arvon mukaan painotettuna.",
    "QQQ": "Invesco QQQ. Nasdaq 100 eli pörssin suurimmat yhtiöt ilman rahoitussektoria.",
    "IWM": "iShares Russell 2000. Noin 2000 yhdysvaltalaista pienyhtiötä.",
    "RSP": "Invesco S&P 500 Equal Weight. Samat yhtiöt kuin SPY mutta jokainen samalla painolla.",
    # Faktorit ja tyyli
    "SPHB": "Invesco S&P 500 High Beta. Sata markkinaherkintä S&P-yhtiötä.",
    "SPLV": "Invesco S&P 500 Low Volatility. Sata vähiten heiluvaa S&P-yhtiötä.",
    "IWD": "iShares Russell 1000 Value. Arvoyhtiöitä suurten ja keskisuurten joukosta.",
    "IWF": "iShares Russell 1000 Growth. Kasvuyhtiöitä samasta joukosta.",
    "IVE": "iShares S&P 500 Value. Arvopuoli S&P 500:sta.",
    "IVW": "iShares S&P 500 Growth. Kasvupuoli S&P 500:sta.",
    "MTUM": "iShares MSCI USA Momentum Factor. Yhtiöt joiden kurssi on noussut viime kuukausina eniten.",
    # Sektorit
    "XLY": "Consumer Discretionary SPDR. Harkinnanvarainen kulutus, kuten Amazon ja Home Depot.",
    "XLP": "Consumer Staples SPDR. Päivittäistavara, kuten Procter & Gamble ja Walmart.",
    "XLI": "Industrial SPDR. Teollisuus ja koneenrakennus.",
    "XLU": "Utilities SPDR. Sähkö- ja vesiyhtiöt, defensiivinen ja korkoherkkä.",
    "XLK": "Technology SPDR. Ohjelmistot, laitteet ja puolijohteet.",
    "XLE": "Energy SPDR. Öljy- ja kaasuyhtiöt.",
    "XLF": "Financial SPDR. Pankit, vakuutus ja varainhoito.",
    "XLV": "Health Care SPDR. Lääkeyhtiöt, laitevalmistajat ja vakuuttajat.",
    "SMH": "VanEck Semiconductor. Puolijohdeyhtiöitä, keskittynyt suurimpiin nimiin.",
    "KRE": "SPDR S&P Regional Banking. Yhdysvaltalaisia aluepankkeja tasapainoin.",
    "IYT": "iShares U.S. Transportation. Rautatiet, rahti ja lentoyhtiöt.",
    "ITB": "iShares U.S. Home Construction. Talonrakentajat ja rakennustarvikeyhtiöt.",
    # Raaka-aineet
    "GLD": "SPDR Gold Shares. Fyysistä kultaa, noin 0,09 unssia osaketta kohden.",
    "SLV": "iShares Silver Trust. Fyysistä hopeaa, noin 0,9 unssia osaketta kohden.",
    "GDX": "VanEck Gold Miners. Kultakaivosyhtiöitä, liikkuu kultaa voimakkaammin.",
    "CPER": "United States Copper Index Fund. Kuparifutuureja, ohut vaihto ja rullausvinouma.",
    "DBC": "Invesco DB Commodity Index. Laaja raaka-ainefutuurikori energiapainolla.",
    # Maantiede
    "EFA": "iShares MSCI EAFE. Kehittyneet markkinat Yhdysvaltain ulkopuolelta.",
    "EEM": "iShares MSCI Emerging Markets. Kehittyvien maiden osakkeita.",
    "FXI": "iShares China Large-Cap. Hongkongissa listattuja kiinalaisia suuryhtiöitä.",
    "EWJ": "iShares MSCI Japan. Japanilaisia osakkeita dollareissa.",
}


def kuvaus(ticker: str) -> str:
    return TICKERS.get(ticker.upper(), "")

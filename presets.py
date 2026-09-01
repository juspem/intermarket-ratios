"""Valmiit suhdeparit teemoittain.

Muoto: kategoria -> lista (osoittaja, nimittäjä, selite).
Selite kertoo mitä nouseva suhde tarkoittaa.
"""

from __future__ import annotations

PRESETS: dict[str, list[tuple[str, str, str]]] = {
    "Luottoriski": [
        ("HYG", "IEF", "Roskalainat vs valtionlainat. Nousu = luottoriskiä siedetään."),
        ("HYG", "LQD", "Roskalainat vs investment grade. Puhtaampi luottolaatusignaali, duraatio lähes neutraali."),
        ("LQD", "IEF", "Yrityslainojen riskilisä valtionlainoihin nähden."),
        ("JNK", "TLT", "Sama teema pidemmällä duraatiolla nimittäjässä."),
        ("EMB", "IEF", "Kehittyvien maiden velka vs Yhdysvaltain valtionlainat."),
    ],
    "Riskinotto osakkeissa": [
        ("SPY", "TLT", "Osakkeet vs pitkät valtionlainat. Klassinen risk-on/risk-off."),
        ("XLY", "XLP", "Harkinnanvarainen kulutus vs päivittäistavara. Kuluttajan riskinottohalu."),
        ("SPHB", "SPLV", "Korkea beta vs matala volatiliteetti. Suora riskinottomittari."),
        ("IWM", "SPY", "Pienyhtiöt vs suuryhtiöt. Nousu = laaja-alaista riskinottoa."),
        ("RSP", "SPY", "Tasapaino vs markkina-arvopaino. Markkinan leveys."),
        ("XLI", "XLU", "Teollisuus vs sähköyhtiöt. Syklinen vs defensiivinen."),
    ],
    "Sektorijohtajuus": [
        ("SMH", "SPY", "Puolijohteet vs markkina. Teknologiasyklin kärki."),
        ("XLK", "SPY", "Teknologia vs markkina."),
        ("XLE", "SPY", "Energia vs markkina. Raaka-ainesyklin ja inflaation heijastus."),
        ("XLF", "SPY", "Rahoitus vs markkina."),
        ("KRE", "XLF", "Aluepankit vs koko rahoitussektori. Pankkisektorin stressimittari."),
        ("XLV", "SPY", "Terveydenhuolto vs markkina. Defensiivinen kallistuma."),
        ("IYT", "SPY", "Kuljetus vs markkina. Vanha Dow-teorian vahvistussignaali."),
        ("ITB", "SPY", "Rakentajat vs markkina. Herkkä korkotasolle."),
    ],
    "Tyyli": [
        ("IWD", "IWF", "Arvo vs kasvu (Russell 1000). Pitkä sykli, seuraa korkoja."),
        ("IVE", "IVW", "Arvo vs kasvu (S&P 500)."),
        ("MTUM", "SPY", "Momentum vs markkina."),
        ("QQQ", "SPY", "Nasdaq 100 vs S&P 500. Kasvu- ja tekniikkajohtajuus."),
        ("QQQ", "IWM", "Suuret kasvuyhtiöt vs pienyhtiöt."),
    ],
    "Defensiivinen varoitus": [
        ("XLP", "SPY", "Päivittäistavara vs markkina. Nousu varoittaa riskinoton hiipumisesta."),
        ("XLU", "SPY", "Sähköyhtiöt vs markkina."),
        ("IEF", "SPY", "Valtionlainat vs osakkeet. Käänteinen risk-on-mittari."),
    ],
    "Korot ja inflaatio": [
        ("TIP", "IEF", "Inflaatiosuojatut vs nimelliset. Karkea breakeven-inflaatioproxy."),
        ("SHY", "TLT", "Lyhyt vs pitkä duraatio. Korkoherkkyyden ja käyrän muodon heijastus."),
        ("IEF", "TLT", "Keskipitkä vs pitkä duraatio."),
    ],
    "Raaka-aineet ja kulta": [
        ("GLD", "SPY", "Kulta vs osakkeet."),
        ("GLD", "TLT", "Kulta vs pitkät korot. Reaalikorkojen heijastus."),
        ("GLD", "SLV", "Kulta–hopea-suhde. Perinteinen makropelon mittari."),
        ("GDX", "GLD", "Kultakaivokset vs kulta. Kaivosten vipu."),
        ("CPER", "GLD", "Kupari vs kulta. Kasvuodotusten klassikko."),
        ("DBC", "SPY", "Laaja raaka-ainekori vs osakkeet."),
    ],
    "Maantiede": [
        ("EFA", "SPY", "Kehittyneet markkinat ex-US vs Yhdysvallat."),
        ("EEM", "SPY", "Kehittyvät markkinat vs Yhdysvallat."),
        ("EEM", "EFA", "Kehittyvät vs kehittyneet ex-US."),
        ("FXI", "EEM", "Kiina vs muut kehittyvät."),
        ("EWJ", "SPY", "Japani vs Yhdysvallat."),
    ],
}


def flat() -> dict[str, tuple[str, str, str]]:
    """Palauta parit muodossa 'HYG / IEF' -> (a, b, selite)."""
    out: dict[str, tuple[str, str, str]] = {}
    for items in PRESETS.values():
        for a, b, desc in items:
            out[f"{a} / {b}"] = (a, b, desc)
    return out


def all_tickers() -> list[str]:
    seen: list[str] = []
    for items in PRESETS.values():
        for a, b, _ in items:
            for t in (a, b):
                if t not in seen:
                    seen.append(t)
    return seen

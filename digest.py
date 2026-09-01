"""Yhteenveto yleiskatsauksesta ilman verkkoyhteyttä.

Lauseet kootaan valmiista paloista, joten teksti on jäykkää mutta ilmaista ja
toistettavaa. Sama data voidaan myöhemmin syöttää kielimallille, jos halutaan
sujuvampaa kieltä.
"""

from __future__ import annotations

import pandas as pd

from presets import Pair, all_pairs

SUUNTA = {"Nouseva": 1, "Laskeva": -1, "Sivuttain": 0}

# Rajat joiden yli liike nostetaan erikseen esiin.
ISO_MUUTOS = 10.0     # prosenttia kolmessa kuukaudessa
AARIPAA_YLA = 95.0    # sijainti 52 viikon vaihteluvälillä
AARIPAA_ALA = 5.0


def _pairs() -> dict[str, Pair]:
    return {p.nimi: p for _, p in all_pairs()}


def _rivit(df: pd.DataFrame) -> list[dict]:
    """Yhdistä taulukon rivit pariensa metatietoihin."""
    parit = _pairs()
    out = []
    for row in df.to_dict("records"):
        p = parit.get(row["Pari"])
        if p is None:
            continue
        out.append({**row, "pair": p, "suunta": SUUNTA.get(row["Tila"], 0)})
    return out


def _teemapisteet(rivit: list[dict], vahintaan: int = 2) -> dict[str, float]:
    """Teeman keskimääräinen riskisävy: +1 riskinottoa, -1 varovaisuutta.

    Teemat joissa on vain yksi riskisignaali jätetään pois, koska yhden parin
    heilahdus ei kerro teeman suunnasta mitään.
    """
    pisteet: dict[str, list[float]] = {}
    for r in rivit:
        if r["pair"].riski:
            pisteet.setdefault(r["Teema"], []).append(r["pair"].riski * r["suunta"])
    return {k: sum(v) / len(v) for k, v in pisteet.items() if len(v) >= vahintaan}


def kappale(df: pd.DataFrame) -> str:
    """Yksi kappale kokonaiskuvasta."""
    rivit = _rivit(df)
    signaalit = [r for r in rivit if r["pair"].riski and r["suunta"]]
    if not signaalit:
        return (
            f"{len(rivit)} parista yksikään ei näytä selvää suuntaa. "
            "Markkinalla ei ole tällä hetkellä yhtenäistä sävyä."
        )

    on = [r for r in signaalit if r["pair"].riski * r["suunta"] > 0]
    off = [r for r in signaalit if r["pair"].riski * r["suunta"] < 0]
    osuus = len(on) / len(signaalit)

    if osuus >= 0.65:
        savy = "Riskinotto on vallitseva sävy"
    elif osuus <= 0.35:
        savy = "Varovaisuus on vallitseva sävy"
    else:
        savy = "Kuva on jakautunut"

    osat = [
        f"{savy}: {len(on)} paria puoltaa riskinottoa ja {len(off)} varovaisuutta, "
        f"loput {len(rivit) - len(signaalit)} ovat sivuttain."
    ]

    vahvin = sorted(signaalit, key=lambda r: abs(r["3 kk %"]), reverse=True)[:2]
    if vahvin:
        nimet = " ja ".join(
            f"{r['Pari']} ({r['3 kk %']:+.1f} %)" for r in vahvin
        )
        osat.append(f"Voimakkaimmin liikkuvat {nimet}.")

    leveys = next((r for r in rivit if r["Pari"] == "RSP / SPY"), None)
    if leveys and leveys["suunta"]:
        if leveys["suunta"] > 0:
            osat.append("Markkinan leveys tukee nousua.")
        else:
            osat.append("Markkinan leveys kapenee, eli nousua kantaa harva yhtiö.")

    return " ".join(osat)


def poikkeamat(df: pd.DataFrame, maara: int = 5) -> list[str]:
    """Selvästi tavallisesta poikkeavat liikkeet ja ääripäät."""
    out: list[tuple[float, str]] = []
    for r in _rivit(df):
        kk3, sij = r["3 kk %"], r["Sijainti 52vk %"]
        huomiot = []
        if pd.notna(kk3) and abs(kk3) >= ISO_MUUTOS:
            huomiot.append(f"{kk3:+.1f} % kolmessa kuukaudessa")
        if pd.notna(sij) and sij >= AARIPAA_YLA:
            huomiot.append("vuoden huipussa")
        elif pd.notna(sij) and sij <= AARIPAA_ALA:
            huomiot.append("vuoden pohjassa")
        if huomiot:
            teksti = f"{r['Pari']} ({r['pair'].lyhyt}): {', '.join(huomiot)}. {r['Tulkinta']}."
            out.append((abs(kk3) if pd.notna(kk3) else 0.0, teksti))
    out.sort(reverse=True)
    return [t for _, t in out[:maara]]


def ristiriidat(df: pd.DataFrame) -> list[str]:
    """Teemat jotka kertovat eri tarinaa."""
    pisteet = _teemapisteet(_rivit(df))
    myonteiset = [k for k, v in pisteet.items() if v >= 0.34]
    kielteiset = [k for k, v in pisteet.items() if v <= -0.34]
    if not myonteiset or not kielteiset:
        return []
    return [
        f"{a} viestii riskinotosta mutta {b} varovaisuudesta."
        for a in myonteiset
        for b in kielteiset
    ][:3]


def build(df: pd.DataFrame) -> dict[str, object]:
    """Koko yhteenveto yhtenä rakenteena."""
    return {
        "kappale": kappale(df),
        "poikkeamat": poikkeamat(df),
        "ristiriidat": ristiriidat(df),
    }

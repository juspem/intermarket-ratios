"""Valmiit suhdeparit teemoittain.

Jokaisella parilla on lyhyt otsikko valikkoon sekä kuvaus siitä mitä nouseva ja
laskeva suhde tarkoittavat. Samaa tekstiä käytetään kuvaajan selitteessä ja
yleiskatsauksen tulkinnassa.
"""

from __future__ import annotations

from typing import NamedTuple


class Pair(NamedTuple):
    a: str          # osoittaja
    b: str          # nimittäjä
    lyhyt: str      # muutama sana valikkoon
    nousu: str      # mitä nouseva suhde kertoo
    lasku: str      # mitä laskeva suhde kertoo
    riski: int = 0  # +1 = nousu on riskinottoa, -1 = varovaisuutta, 0 = ei kumpaakaan
    vakiintuneet: str = ""  # vain jos parille on sijoittajapiireissä tunnetut raja-arvot

    @property
    def nimi(self) -> str:
        return f"{self.a} / {self.b}"

    @property
    def label(self) -> str:
        return f"{self.a} / {self.b} · {self.lyhyt}"


PRESETS: dict[str, list[Pair]] = {
    "Luottoriski": [
        Pair("HYG", "IEF", "Luottoriskin sietokyky",
             "sijoittajat sietävät luottoriskiä",
             "turvaan siirrytään valtionlainoihin", 1),
        Pair("HYG", "LQD", "Luottolaadun kysyntä",
             "heikompaa luottolaatua uskalletaan ostaa",
             "laatua suositaan roskalainojen sijaan", 1),
        Pair("LQD", "IEF", "Yrityslainojen riskilisä",
             "yrityslainojen riskilisä kapenee",
             "yrityslainoista vaaditaan enemmän korvausta", 1),
        Pair("JNK", "TLT", "Roskalainat vs pitkät korot",
             "riskinotto voittaa duraation",
             "pitkät valtionlainat vetävät paremmin", 1),
        Pair("EMB", "IEF", "Kehittyvien velka",
             "kehittyvien velkaan uskalletaan",
             "kehittyvien riskilisä kasvaa", 1),
    ],
    "Riskinotto osakkeissa": [
        Pair("SPY", "TLT", "Osakkeet vs korot",
             "osakkeet vetävät korkoja paremmin",
             "raha siirtyy korkomarkkinalle", 1),
        Pair("XLY", "XLP", "Kuluttajan riskinotto",
             "kuluttaja uskaltaa kuluttaa harkinnanvaraisesti",
             "kuluttaja siirtyy perustarpeisiin", 1),
        Pair("SPHB", "SPLV", "Korkea beta vs matala vola",
             "riskinotto lisääntyy selvästi",
             "volatiliteettia paetaan", 1),
        Pair("IWM", "SPY", "Pienyhtiöt vs suuret",
             "riskinotto ulottuu pienyhtiöihin",
             "turva haetaan suuryhtiöistä", 1),
        Pair("RSP", "SPY", "Markkinan leveys",
             "nousua kantaa laaja joukko yhtiöitä",
             "muutama suuryhtiö kantaa koko markkinaa", 1),
        Pair("XLI", "XLU", "Syklinen vs defensiivinen",
             "talouskasvuun luotetaan",
             "defensiivisiin sektoreihin siirrytään", 1),
    ],
    "Sektorijohtajuus": [
        Pair("SMH", "SPY", "Puolijohteiden veto",
             "teknologiasykli vahvistuu",
             "teknologiasykli hyytyy", 1),
        Pair("XLK", "SPY", "Teknologian johtajuus",
             "teknologia vetää markkinaa",
             "teknologia jää markkinasta jälkeen", 1),
        Pair("XLE", "SPY", "Energian veto",
             "energia ja inflaatiopaine vahvistuvat",
             "energia jää markkinasta jälkeen", 0),
        Pair("XLF", "SPY", "Rahoituksen johtajuus",
             "rahoitussektori vahvistuu",
             "rahoitus jää markkinasta jälkeen", 1),
        Pair("KRE", "XLF", "Aluepankkien stressi",
             "aluepankkien paine helpottaa",
             "aluepankeissa on stressiä", 1),
        Pair("XLV", "SPY", "Terveydenhuollon veto",
             "defensiivinen kallistuma vahvistuu",
             "terveydenhuolto jää jälkeen", -1),
        Pair("IYT", "SPY", "Kuljetuksen vahvistus",
             "reaalitalous vetää",
             "kuljetus varoittaa hidastumisesta", 1),
        Pair("ITB", "SPY", "Rakentajien veto",
             "korko-odotukset suosivat asuntomarkkinaa",
             "korkopaine painaa rakentajia", 1),
    ],
    "Tyyli": [
        Pair("IWD", "IWF", "Arvo vs kasvu",
             "arvo johtaa, tyypillistä korkojen noustessa",
             "kasvu johtaa, tyypillistä korkojen laskiessa", 0),
        Pair("IVE", "IVW", "Arvo vs kasvu (S&P)",
             "arvo johtaa S&P 500:n sisällä",
             "kasvu johtaa S&P 500:n sisällä", 0),
        Pair("MTUM", "SPY", "Momentumin veto",
             "trendit jatkuvat vahvoina",
             "momentum purkautuu ja johtajuus vaihtuu", 0),
        Pair("QQQ", "SPY", "Kasvujohtajuus",
             "suuret kasvuyhtiöt vetävät",
             "johtajuus siirtyy pois kasvusta", 0),
        Pair("QQQ", "IWM", "Suuret vs pienet",
             "raha keskittyy suuriin kasvuyhtiöihin",
             "riskinotto leviää pienyhtiöihin", -1),
    ],
    "Defensiivinen varoitus": [
        Pair("XLP", "SPY", "Defensiivinen varoitus",
             "raha pakenee päivittäistavaraan",
             "riskinotto on normaalilla tasolla", -1),
        Pair("XLU", "SPY", "Sähköyhtiöiden turva",
             "turvaa haetaan sähköyhtiöistä",
             "defensiivisyys ei kiinnosta", -1),
        Pair("IEF", "SPY", "Korot vs osakkeet",
             "korkomarkkina voittaa osakkeet",
             "osakkeet vetävät korkoja paremmin", -1),
    ],
    "Korot ja inflaatio": [
        Pair("TIP", "IEF", "Inflaatio-odotukset",
             "inflaatio-odotukset nousevat",
             "inflaatio-odotukset laskevat", 0),
        Pair("SHY", "TLT", "Duraatioriski",
             "pitkä duraatio kärsii, korot nousevat",
             "pitkät korot laskevat", 0),
        Pair("IEF", "TLT", "Käyrän pitkä pää",
             "pitkä pää heikkenee suhteessa keskipitkään",
             "pitkä pää vahvistuu", 0),
    ],
    "Raaka-aineet ja kulta": [
        Pair("GLD", "SPY", "Kulta vs osakkeet",
             "kultaan haetaan turvaa",
             "osakkeet vetävät kultaa paremmin", -1),
        Pair("GLD", "TLT", "Reaalikorot",
             "reaalikorot painuvat, kulta voittaa korot",
             "korot voittavat kullan", 0),
        Pair("GLD", "SLV", "Kulta-hopea",
             "makropelko kasvaa",
             "syklinen usko palaa", -1,
             "Ainoa pari jolle on vakiintuneet rajat: kulta-hopea-suhdetta yli 80 "
             "pidetään korkeana ja alle 50 matalana. Kuvaajan luku on kuitenkin noin "
             "kymmenesosa tästä, koska GLD:ssä on noin 0,09 unssia kultaa ja SLV:ssä "
             "noin 0,9 unssia hopeaa osaketta kohden. Kerro näytöllä näkyvä luku "
             "noin kymmenellä saadaksesi vertailukelpoisen suhdeluvun."),
        Pair("GDX", "GLD", "Kaivosten vipu",
             "kaivokset ottavat vipua kullan noususta",
             "kaivokset jäävät kullasta jälkeen", 0),
        Pair("CPER", "GLD", "Kupari-kulta",
             "kasvuodotukset vahvistuvat",
             "kasvuodotukset heikkenevät", 1),
        Pair("DBC", "SPY", "Raaka-aineet vs osakkeet",
             "raaka-ainepaine kasvaa",
             "raaka-aineet jäävät osakkeista jälkeen", 0),
    ],
    "Maantiede": [
        Pair("EFA", "SPY", "Kehittyneet ex-US vs USA",
             "Eurooppa ja Japani johtavat",
             "Yhdysvallat johtaa", 0),
        Pair("EEM", "SPY", "Kehittyvät vs USA",
             "kehittyvät vetävät, usein heikon dollarin aikaan",
             "Yhdysvallat vetää kehittyviä paremmin", 1),
        Pair("EEM", "EFA", "Kehittyvät vs kehittyneet",
             "kehittyvät johtavat muita ex-US-markkinoita",
             "kehittyneet ex-US johtavat", 1),
        Pair("FXI", "EEM", "Kiinan osuus",
             "Kiina vetää kehittyviä markkinoita",
             "Kiina jää muista kehittyvistä jälkeen", 0),
        Pair("EWJ", "SPY", "Japani vs USA",
             "Japani johtaa",
             "Yhdysvallat johtaa", 0),
    ],
}


def flat() -> dict[str, Pair]:
    """Parit valikkotekstin mukaan: 'HYG / IEF · Luottoriskin sietokyky' -> Pair."""
    return {p.label: p for items in PRESETS.values() for p in items}


def all_pairs() -> list[tuple[str, Pair]]:
    """Kaikki parit teeman kanssa."""
    return [(cat, p) for cat, items in PRESETS.items() for p in items]


def all_tickers() -> list[str]:
    seen: list[str] = []
    for _, p in all_pairs():
        for t in (p.a, p.b):
            if t not in seen:
                seen.append(t)
    return seen

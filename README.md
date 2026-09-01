# Chart-Ratios

Streamlit-työkalu kahden instrumentin suhdeluvun tarkasteluun kynttilägraafina, esimerkiksi HYG/IEF. Suhdeparit kertovat markkinan sisäisestä liikkeestä enemmän kuin yksittäisen instrumentin kurssi.

## Käyttö

Valitse sivupalkista osoittaja ja nimittäjä, historian pituus ja kynttilän aikaväli. Voit joko kirjoittaa tickerit itse tai valita valmiin parin.

Yleiskatsaus-välilehti laskee kaikkien valmiiden parien 1 kk, 3 kk ja 12 kk muutokset sekä sijainnin 52 viikon vaihteluvälillä. Jokaiselle parille tulee lisäksi tila (nouseva, laskeva, sivuttain) ja lause siitä mitä suunta juuri sille parille tarkoittaa. Taulukon yläpuolella on kappale kokonaiskuvasta, erikseen nostetut poikkeavat liikkeet ja huomautus jos teemat kertovat eri tarinaa.

## Kuvaaja

Rulla zoomaa, veto panoroi, tuplaklikkaus palauttaa näkymän. Ristikkokursori seuraa hiirtä paneelien läpi ja näyttää arvot yhdessä laatikossa.

RSI ja MACD saa omiin paneeleihinsa sivupalkista. RSI käyttää Wilderin silotusta eli samaa laskutapaa kuin TradingView'n oletus.

Piirtotyökalut ovat oikean yläkulman työkalupalkissa. Piirretyt viivat katoavat kun sivu piirretään uudelleen, eli aina kun asetuksia vaihdetaan.

## Aikavälit

1 min - kvartaali. Yahoo rajoittaa intraday-historiaa: 1 min noin 7 päivää, 5-30 min noin 60 päivää, 1 h noin 730 päivää. Historiavalikko rajautuu automaattisesti valitun kynttiläkoon mukaan.

2 h ja 4 h lasketaan tuntidatasta, viikko ja sitä pidemmät päivädatasta. Aikavälin vaihto ei siis aina vaadi uutta hakua.

## Parin oma mittatikku

Suhdeparin absoluuttinen luku ei kerro mitään, koska se riippuu vain ETF:ien osakekursseista. HYG/IEF on noin 0,82 pelkästään siksi että HYG maksaa vähemmän kuin IEF.

Siksi kuvaajan yläpuolella näytetään parin oma vaihteluväli kolmen vuoden päivädatasta: mikä luku on matala (alin kymmenys), mikä mediaani ja mikä korkea (ylin kymmenys), sekä missä kohtaa suhde nyt on. Yleiskatsauksessa sama tieto on Taso-sarakkeena.

Vakiintuneita raja-arvoja ei merkitä, koska niitä ei suurimmalle osalle pareista ole olemassa. Ainoa poikkeus on GLD/SLV: kulta-hopea-suhdetta yli 80 pidetään korkeana ja alle 50 matalana. Näytöllä oleva luku on noin kymmenesosa siitä, koska GLD:ssä on noin 0,09 unssia kultaa ja SLV:ssä noin 0,9 unssia hopeaa osaketta kohden.

Kuvaajan alta löytyy myös Mistä pari koostuu, joka kertoo mitä kumpikin ETF sisältää. Kuvaukset ovat tickers.py-tiedostossa.

## Suhdekynttilöiden laskenta

Open ja Close ovat eksakteja: A.Open / B.Open ja A.Close / B.Close.

High ja Low ovat teoreettisia ääriarvoja: A.High / B.Low ja A.Low / B.High. Nämä ovat hieman todellista leveämpiä, koska datasta ei näe osuivatko A:n huippu ja B:n pohja samaan hetkeen.

## Valmiit parit

presets.py sisältää noin 40 vakiintunutta suhdeparia kahdeksassa teemassa: luottoriski, riskinotto osakkeissa, sektorijohtajuus, tyyli, defensiivinen varoitus, korot ja inflaatio, raaka-aineet ja maantiede.

Jokainen pari on Pair-tietue: osoittaja, nimittäjä, lyhyt otsikko valikkoon sekä kuvaus siitä mitä nousu ja lasku tarkoittavat. Samasta tekstistä syntyy kuvaajan selite ja yleiskatsauksen tulkinta. Omat parit lisätään suoraan presets.py-tiedostoon.

## Rakenne

core.py: datan haku, suhdekynttilöiden laskenta, indikaattorit

chart.py: Plotly-kuvaaja, ristikkokursori, piirtotyökalut, indikaattoripaneelit

digest.py: yhteenveto yleiskatsauksesta

tickers.py: mitä kukin ETF sisältää

app.py: Streamlit-käyttöliittymä

presets.py: valmiit suhdeparit teemoittain

## Asennus

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Kehityskohteita

- piirrettyjen viivojen säilytys asetusten vaihdon yli
- omien parien tallennus tiedostoon
- yhteenvedon kieli kielimallilla, jos oma API-avain annetaan
- datan välimuisti levylle
- useampi suhdepari samassa näkymässä

# Chart-Ratios

Streamlit-työkalu kahden instrumentin suhdeluvun tarkasteluun kynttilägraafina, esimerkiksi HYG/IEF. Suhdeparit kertovat markkinan sisäisestä liikkeestä enemmän kuin yksittäisen instrumentin kurssi.

## Käyttö

Valitse sivupalkista osoittaja ja nimittäjä, historian pituus ja kynttilän aikaväli. Voit joko kirjoittaa tickerit itse tai valita valmiin parin.

Yleiskatsaus-välilehti laskee kaikkien valmiiden parien 1 kk, 3 kk ja 12 kk muutokset sekä sijainnin 52 viikon vaihteluvälillä, eli mitkä suhteet ovat liikkeessä juuri nyt.

## Suhdekynttilöiden laskenta

Open ja Close ovat eksakteja: A.Open / B.Open ja A.Close / B.Close.

High ja Low ovat teoreettisia ääriarvoja: A.High / B.Low ja A.Low / B.High. Nämä ovat hieman todellista leveämpiä, koska päivädatasta ei näe osuivatko A:n huippu ja B:n pohja samaan hetkeen.

Viikko- ja kuukausikynttilät lasketaan päivädatasta paikallisesti, joten aikavälin vaihto ei vaadi uutta hakua.

## Valmiit parit

presets.py sisältää noin 40 vakiintunutta suhdeparia kahdeksassa teemassa: luottoriski, riskinotto osakkeissa, sektorijohtajuus, tyyli, defensiivinen varoitus, korot ja inflaatio, raaka-aineet ja maantiede.

Omat parit lisätään suoraan presets.py-tiedostoon: kategoria -> lista (osoittaja, nimittäjä, selite).

## Rakenne

core.py: datan haku, suhdekynttilöiden laskenta, aikavälin tiivistys

app.py: Streamlit-käyttöliittymä ja Plotly-kuvaaja

presets.py: valmiit suhdeparit teemoittain

## Asennus

python -m venv .venv

pip install -r requirements.txt

streamlit run app.py

## Kehityskohteita

- RSI tai muu indikaattori suhdesarjasta
- Intrapäivädata (Yahoolla noin 730 päivän historia)
- Datan välimuisti levylle

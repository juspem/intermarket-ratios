# ratio-charts

Kevyt työkalu kahden instrumentin suhdeluvun (esim. `HYG/IEF`) tarkasteluun
kynttilägraafina eri aikaväleillä.

## Asennus (Windows + VS Code)

Avaa VS Codessa terminaali (`Ctrl+ö` tai Terminal → New Terminal) ja aja:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Valitse VS Codessa tulkki: `Ctrl+Shift+P` → *Python: Select Interpreter* → `.venv`.

## Käyttö

```powershell
streamlit run app.py
```

Selain avautuu osoitteeseen `http://localhost:8501`. Vaihda sivupalkista
osoittaja ja nimittäjä, historian pituus ja kynttilän aikaväli.

## Rakenne

| Tiedosto | Sisältö |
|---|---|
| `core.py` | Datan haku, suhdekynttilöiden laskenta, aikavälin tiivistys |
| `app.py` | Streamlit-käyttöliittymä ja Plotly-kuvaaja |
| `presets.py` | Valmiit suhdeparit teemoittain |

## Suhdekynttilöiden laskenta

- `Open = A.Open / B.Open`, `Close = A.Close / B.Close` — eksakteja.
- `High = A.High / B.Low`, `Low = A.Low / B.High` — teoreettiset ääriarvot
  kynttilän sisällä. Nämä ovat hieman todellista leveämpiä, koska päivädatasta
  ei näe osuivatko A:n huippu ja B:n pohja samaan hetkeen.
- Viikko- ja kuukausikynttilät lasketaan päivädatasta paikallisesti
  (`first / max / min / last`), joten aikavälin vaihto ei vaadi uutta hakua.

## Valmiit parit

`presets.py` sisältää noin 40 vakiintunutta suhdeparia kahdeksassa teemassa:
luottoriski, riskinotto osakkeissa, sektorijohtajuus, tyyli, defensiivinen
varoitus, korot ja inflaatio, raaka-aineet, maantiede. Valitse teema ja pari
sivupalkista, tai kirjoita omat tickerit kenttiin.

Lisää omat parisi suoraan `presets.py`-tiedostoon: kategoria -> lista
`(osoittaja, nimittäjä, selite)`.

Välilehti **Yleiskatsaus** laskee kaikkien parien 1 kk / 3 kk / 12 kk muutokset
ja sijainnin 52 viikon vaihteluvälillä, eli mitkä suhteet ovat liikkeessä juuri nyt.

## Git ja GitHub

```powershell
git init
git add .
git commit -m "Ensimmäinen versio: HYG/IEF-suhdegraafi"
git branch -M main
git remote add origin https://github.com/KAYTTAJA/ratio-charts.git
git push -u origin main
```

## Ideoita jatkoon

- RSI tai muu indikaattori suhdesarjasta
- Intrapäivädata (`interval="1h"`, Yahoolla n. 730 päivän historia)
- Valmiiden pariparien tallennus JSON-tiedostoon
- Datan välimuisti levylle, jottei Yahoota tarvitse kysellä joka käynnistyksellä

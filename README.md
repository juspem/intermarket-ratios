# Chart-Ratios

A Streamlit tool for looking at the ratio between two instruments as a candle chart, for example HYG/IEF. Ratio pairs say more about what is going on inside the market than any single price does.

## Use

Pick a numerator and a denominator in the sidebar, along with the history length and the candle size. You can type tickers yourself or choose one of the presets.

The Overview tab works out the 1M, 3M and 12M change for every preset pair plus where each one sits in its 52 week range. Each pair gets a state (rising, falling, flat) and a line on what that direction means for that particular pair. Above the table there is a paragraph on the overall picture, a separate list of unusual moves, and a note if the themes are telling different stories.

## The chart

The wheel zooms, dragging pans, double click resets. A crosshair follows the cursor through every panel and shows the values in one box. Drag the bottom edge of the chart to make it taller.

RSI and MACD get their own panels from the sidebar. RSI uses Wilder's smoothing, the same as TradingView's default.

The drawing tools live in the toolbar at the top right. Anything you draw disappears when the page reruns, which happens every time you change a setting.

## Timeframes

1 min through quarterly. Yahoo limits intraday history: roughly 7 days at 1 min, 60 days at 5 to 30 min, and 730 days at 1 hour. The history dropdown narrows itself to whatever the chosen candle size allows.

2 hour and 4 hour candles are built from hourly data, weekly and longer from daily. So changing the timeframe often costs no new download.

## Reading the level

The absolute number on a ratio chart means nothing on its own. HYG/IEF sits around 0.82 purely because HYG costs less than IEF. Split the denominator two for one and the ratio doubles without anything happening in the market.

So the chart shows the pair's own range instead, taken from three years of daily data: what counts as low (bottom tenth), what the median is, what counts as high (top tenth), and where the ratio sits today. The Overview tab carries the same thing as a Level column.

No fixed thresholds are drawn, because for almost every pair none exist. The one exception is GLD/SLV, where a gold to silver ratio above 80 is widely treated as high and below 50 as low. The number on the chart is about a tenth of that, since GLD holds roughly 0.09 ounces of gold per share and SLV roughly 0.9 ounces of silver.

Above every chart you get what each leg holds, what the pair reads, anything odd about that particular pair, a paragraph on why the theme is worth watching at all, and where the ratio currently stands against its own three year history. ETF descriptions live in tickers.py, theme background and pair notes in presets.py.

The headline numbers sit on the same line as the pair name. Only the raw data table is below the chart.

## How ratio candles are built

Open and Close are exact: A.Open / B.Open and A.Close / B.Close.

High and Low are the widest the ratio could have been inside the bar: A.High / B.Low and A.Low / B.High. They come out slightly wider than reality, because the data does not say whether A's high and B's low happened at the same moment.

## Preset pairs

presets.py holds around 40 well established pairs across eight themes: credit risk, risk appetite in equities, sector leadership, style, defensive warning, rates and inflation, commodities, and regions.

Each one is a Pair record: numerator, denominator, a short topic for the dropdown, and a line each on what rising and falling mean. That same text feeds the chart caption and the overview reading. Ten pairs also carry a note about something that would otherwise mislead you, such as HYG and IEF having very different duration. Themes carry a longer background paragraph in THEMES. Add your own straight into presets.py.

## Layout

core.py: data fetching, ratio candles, indicators, percentile ranges

chart.py: the Plotly figure, crosshair, drawing tools, indicator panels

digest.py: the written summary of the overview

presets.py: preset pairs by theme

tickers.py: what each ETF holds

app.py: the Streamlit interface

## Install

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Todo

- keep drawings alive across reruns
- save custom pairs to a file
- cache data to disk
- more than one ratio in the same view
- let a language model write the summary if an API key is supplied

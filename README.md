# Lookkha

Tourism BI for Phuket businesses: who the customers are, when they come, and how to prepare stock, staff and languages this month. Built on real Phuket open data.

## What's on the site

`index.html` is a single static page:

1. **Advice for your shop**: pick your zone and get six answers. These are this month's stock change, next month's outlook, languages for signs and menus, the fastest-growing market, peak months, and the quietest months.
2. **Overview**: KPIs, a visitor map, and what to prepare this month (with rain and source-market holidays).
3. **Who is coming**: visitors by nationality, seasonality by nationality, and yearly tourism revenue.
4. **When they come**: monthly visitors with a 3-month forecast and error band, a 14-day rain forecast, and a 60-day holiday calendar.

## Data

`etl/build_data.py` downloads the datasets below from [phuket.gdcatalog.go.th](https://phuket.gdcatalog.go.th/) (data.go.th, licence: Open Data Common) and writes `data/phuket-data.js`.

| Dataset | Content | Granularity | Publisher |
|---|---|---|---|
| dataset_10_36 | Foreign international departures by nationality | Monthly | Phuket Airport Immigration |
| dataset_10_02 | Phuket airport passengers, domestic / international | Monthly | AOT, Phuket Airport |
| dataset_10_34 | Visitors, Thai / foreign | Yearly | Phuket Tourism and Sports Office |
| dataset_10_09 | Average spend per person per day | Yearly | Phuket Tourism and Sports Office |
| dataset_10_08 | Tourism revenue, Thai / foreign | Yearly | Phuket Tourism and Sports Office |

These APIs are called live in the browser:
- Open-Meteo for the 14-day rain forecast
- Nager.Date for source-market public holidays
- Esri World Imagery for the satellite map

`.github/workflows/refresh-data.yml` runs the ETL on the 5th of every month and commits `data/phuket-data.js` if it changed. For this to work, set **Settings → Actions → General → Workflow permissions** to **Read and write**.

## Method

- **Monthly visitors** = monthly airport passengers × a calibration ratio, so that the latest full year adds up to the official yearly visitor total.
  - Foreign visitors use international departures by nationality.
  - Thai visitors use domestic arrivals.
- **Revenue** = visitors × revenue per visitor (latest official revenue ÷ visitors in the same year).
- **Spend per person per day** comes from the latest yearly statistics, weighted by the Thai / foreign mix.
- **Forecast** = same month last year × growth over the latest 3 months, calculated separately for Thai and foreign visitors.
- **Accuracy**: a 1-month-ahead backtest of the same method on real history (MAPE). The forecast band is ± MAPE × √(months ahead).
- **Benchmark**: each nationality's growth (latest 3 months vs a year earlier) compared with the whole market.
- **YoY** compares the same months of the previous year.
- **Rainy day** = rain ≥ 5 mm.

### Advice page

Every answer follows the selected zone.

- **Stock this month**: this month's forecast, daily average, vs the latest month of real data. Changes within ±3% count as unchanged.
- **Next month**: next month's forecast daily average vs this month.
- **Sign / menu languages**: visitor share by each nationality's main language.
- **Fastest-growing market**: highest growth over the latest 3 months vs a year earlier, excluding "Other foreign".
- **Months to add staff / renovate**: the 3 busiest and 2 quietest calendar months, averaged over all real monthly data.

## Limitations

- **Zones:** the visitor split by zone is an assumption, because no area-level data is published. It is labelled as an estimate on the site.
- **Spend:** there is no spend data by nationality, so every foreign market uses the foreign average.
- **Granularity:** the data is monthly, so the site gives no weekly advice.
- **Airport data:** it doesn't count visitors arriving by road or sea. The yearly calibration ratio corrects for this.

## Run locally

```bash
python -m http.server 8000
```

Then open http://localhost:8000/. To refresh the data by hand:

```bash
python etl/build_data.py
```

The raw 33 MB hero video source (`Photo/videoplayback.mp4`) is not published; see `.gitignore`.

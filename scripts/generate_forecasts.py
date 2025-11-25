"""Generate forecasts for `co2_per_capita` per country and save outputs.

Produces:
- `data/forecasts_co2_per_capita.csv` with observed + forecast + 95% CI
- `data/forecasts_plots/{country}.html` per-country interactive Plotly plot

Run from project root:
    python scripts/generate_forecasts.py
"""
import os
import sys
import logging
from pathlib import Path

import pandas as pd

# Ensure project src is importable when script is run from project root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_data
from src.forecast import forecast_series
from src.viz_timeseries import country_forecast_plot


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name).strip()


def generate_forecasts(metric: str = "co2", steps: int = 5, min_points: int = 6):
    df = load_data()

    out_rows = []
    plots_dir = ROOT / "data" / "forecasts_plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    countries = sorted(df["country"].dropna().unique())
    logging.info(f"Found {len(countries)} countries; computing forecasts for metric '{metric}'")

    for country in countries:
        cdf = df[df["country"] == country].sort_values("year")
        years = cdf["year"].astype(int)
        values = cdf.get(metric)
        non_null = values.dropna()
        if non_null.shape[0] < min_points:
            logging.info(f"Skipping {country}: only {non_null.shape[0]} non-missing points")
            continue

        try:
            fdf = forecast_series(years, values, steps=steps)
        except Exception as e:
            logging.warning(f"Forecast failed for {country}: {e}")
            continue

        # Attach identifiers
        iso = cdf["iso_code"].dropna().unique()
        iso_val = iso[0] if len(iso) > 0 else ""
        fdf["country"] = country
        fdf["iso_code"] = iso_val
        fdf["metric"] = metric

        out_rows.append(fdf)

        # Save per-country interactive plot
        try:
            fig = country_forecast_plot(df, country, metric=metric, steps=steps)
            fname = plots_dir / f"{_safe_filename(country)}.html"
            fig.write_html(str(fname), include_plotlyjs="cdn")
        except Exception as e:
            logging.warning(f"Failed to create plot for {country}: {e}")

    if not out_rows:
        logging.error("No forecasts were generated; exiting")
        return

    combined = pd.concat(out_rows, ignore_index=True)
    out_csv = ROOT / "data" / f"forecasts_{metric}.csv"
    combined.to_csv(out_csv, index=False)
    logging.info(f"Wrote forecasts CSV to {out_csv}")
    logging.info(f"Wrote per-country plots to {plots_dir}")


if __name__ == "__main__":
    generate_forecasts()

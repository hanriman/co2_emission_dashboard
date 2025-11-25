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
from src.pages.timeseries.forecast import forecast_series
from src.pages.timeseries.viz_timeseries import country_forecast_plot
import plotly.graph_objects as go


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name).strip()


def generate_forecasts(metrics: list | None = None, steps: int = 5, min_points: int = 6):
    """Generate per-country forecasts for the requested metrics and a global CO2 total forecast.

    By default this generates forecasts for `co2` and `gdp` for every country (when available),
    and additionally generates a single global CO2 total forecast (aggregate across countries by year).

    Results:
    - `data/forecasts_{metric}.csv` per-metric per-country forecasts
    - `data/forecasts_plots/{country}.html` per-country plots
    - `data/forecasts_global_co2.csv` and `data/forecasts_plots/global_co2.html` for global CO2
    """
    if metrics is None:
        metrics = ["co2", "gdp"]

    df = load_data()

    plots_dir = ROOT / "data" / "forecasts_plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    countries = sorted(df["country"].dropna().unique())

    for metric in metrics:
        out_rows = []
        logging.info(f"Found {len(countries)} countries; computing forecasts for metric '{metric}'")

        for country in countries:
            cdf = df[df["country"] == country].sort_values("year")
            years = cdf["year"].astype(int)
            values = cdf.get(metric)
            if values is None:
                # Metric not present for this dataset
                logging.debug(f"Metric '{metric}' not found for country {country}; skipping")
                continue
            non_null = values.dropna()
            if non_null.shape[0] < min_points:
                logging.info(f"Skipping {country}: only {non_null.shape[0]} non-missing points for metric '{metric}'")
                continue

            try:
                fdf = forecast_series(years, values, steps=steps)
            except Exception as e:
                logging.warning(f"Forecast failed for {country} ({metric}): {e}")
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
                fname = plots_dir / f"{_safe_filename(country)}_{metric}.html"
                fig.write_html(str(fname), include_plotlyjs="cdn")
            except Exception as e:
                logging.warning(f"Failed to create plot for {country} ({metric}): {e}")

        if not out_rows:
            logging.warning(f"No forecasts were generated for metric '{metric}'")
            continue

        combined = pd.concat(out_rows, ignore_index=True)
        out_csv = ROOT / "data" / f"forecasts_{metric}.csv"
        combined.to_csv(out_csv, index=False)
        logging.info(f"Wrote forecasts CSV to {out_csv}")
        logging.info(f"Wrote per-country plots for metric '{metric}' to {plots_dir}")

    # Additionally: create a global total CO2 forecast (aggregate across countries)
    try:
        logging.info("Computing global total CO2 time series and forecast")
        # Sum CO2 across countries by year; ensure numeric and drop NaNs
        gdf = df.groupby("year", as_index=False)["co2"].sum()
        gdf = gdf.sort_values("year")
        years = gdf["year"].astype(int)
        values = gdf["co2"].astype(float)

        if values.dropna().shape[0] >= min_points:
            gf = forecast_series(years, values, steps=steps)
            gf["metric"] = "co2_global"
            out_csv = ROOT / "data" / "forecasts_global_co2.csv"
            gf.to_csv(out_csv, index=False)
            logging.info(f"Wrote global CO2 forecasts to {out_csv}")

            # Build a simple plot similar to country_forecast_plot for the global series
            hist_x = gf[gf["y"].notna()]["year"]
            hist_y = gf[gf["y"].notna()]["y"]
            fcast = gf[gf["y_pred"].notna()]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist_x, y=hist_y, mode="lines+markers", name="Observed", line=dict(color="#1f77b4")))
            fig.add_trace(go.Scatter(x=fcast["year"], y=fcast["y_pred"], mode="lines+markers", name="Forecast", line=dict(color="#ff7f0e")))
            fig.add_trace(go.Scatter(x=fcast["year"], y=fcast["y_lower"], mode="lines", line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=fcast["year"], y=fcast["y_upper"], mode="lines", line=dict(width=0), fill="tonexty", fillcolor="rgba(255,127,14,0.2)", name="95% CI"))
            fig.update_layout(title="Global total CO2 (observed + forecast)", xaxis_title="Year", yaxis_title="CO2 (total)")
            fname = plots_dir / "global_co2.html"
            fig.write_html(str(fname), include_plotlyjs="cdn")
            logging.info(f"Wrote global CO2 forecast plot to {fname}")
        else:
            logging.warning("Not enough non-missing global CO2 points to forecast")
    except Exception as e:
        logging.warning(f"Failed to compute global CO2 forecast: {e}")


if __name__ == "__main__":
    generate_forecasts()

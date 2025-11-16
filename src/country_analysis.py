import pandas as pd
import plotly.express as px
from typing import Tuple, Optional, List


def country_summary(df: pd.DataFrame, country: str) -> Tuple[Optional[dict], pd.DataFrame]:
    """Return a small summary dictionary and the country's time-series DataFrame.

    Summary contains GDP growth % and CO2 per-capita change % between earliest and latest available years.
    """
    cdf = df[df["country"] == country].sort_values("year")
    if cdf.empty:
        return None, cdf

    # pick first/last available
    gdp_start = cdf["gdp"].iloc[0] if "gdp" in cdf.columns else None
    gdp_end = cdf["gdp"].iloc[-1] if "gdp" in cdf.columns else None
    co2_start = cdf["co2_per_capita"].iloc[0] if "co2_per_capita" in cdf.columns else None
    co2_end = cdf["co2_per_capita"].iloc[-1] if "co2_per_capita" in cdf.columns else None

    summary = {
        "country": country,
        "years": (int(cdf["year"].min()), int(cdf["year"].max())),
        "gdp_growth_pct": None,
        "co2_per_capita_change_pct": None,
        "green_growth": None,
    }

    if gdp_start and gdp_end and gdp_start != 0:
        summary["gdp_growth_pct"] = (gdp_end - gdp_start) / gdp_start * 100

    if co2_start is not None and co2_end is not None and co2_start != 0:
        summary["co2_per_capita_change_pct"] = (co2_end - co2_start) / co2_start * 100

    if summary["gdp_growth_pct"] is not None and summary["co2_per_capita_change_pct"] is not None:
        summary["green_growth"] = (summary["gdp_growth_pct"] > 0 and summary["co2_per_capita_change_pct"] < 0)

    return summary, cdf


def plot_country_trends(cdf: pd.DataFrame) -> List[px.Figure]:
    figs = []
    if cdf.empty:
        return figs

    if "gdp" in cdf.columns:
        figs.append(px.line(cdf, x="year", y="gdp", title="GDP over time", markers=True))

    if "co2_per_capita" in cdf.columns:
        figs.append(px.line(cdf, x="year", y="co2_per_capita", title="CO2 per capita over time", markers=True))

    if "gdp" in cdf.columns and "co2_per_capita" in cdf.columns:
        size_col = "population" if "population" in cdf.columns else None
        figs.append(px.scatter(cdf, x="gdp", y="co2_per_capita", size=size_col, hover_name="year", title="GDP vs CO2 per capita"))

    return figs


def find_green_growth_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame listing countries that show 'green growth'.

    Green growth is defined here as GDP growth > 0 between the country's
    first and last available years while CO2 per capita decreases (percentage change < 0).

    Returns a DataFrame with columns: country, years (tuple), gdp_growth_pct, co2_per_capita_change_pct, green_growth
    """
    out_rows = []
    # work on a copy sorted by country and year
    df_sorted = df.sort_values(["country", "year"]).copy()
    for country, group in df_sorted.groupby("country", sort=True):
        if group.empty:
            continue
        gdp = pd.to_numeric(group.get("gdp"), errors="coerce")
        co2pc = pd.to_numeric(group.get("co2_per_capita"), errors="coerce")

        # pick first/last available non-null
        try:
            gdp_start = gdp.dropna().iloc[0]
            gdp_end = gdp.dropna().iloc[-1]
        except Exception:
            gdp_start = None
            gdp_end = None

        try:
            co2_start = co2pc.dropna().iloc[0]
            co2_end = co2pc.dropna().iloc[-1]
        except Exception:
            co2_start = None
            co2_end = None

        gdp_growth_pct = None
        co2_change_pct = None
        if gdp_start is not None and gdp_end is not None and gdp_start != 0:
            gdp_growth_pct = (gdp_end - gdp_start) / gdp_start * 100

        if co2_start is not None and co2_end is not None and co2_start != 0:
            co2_change_pct = (co2_end - co2_start) / co2_start * 100

        green = (gdp_growth_pct is not None and co2_change_pct is not None and gdp_growth_pct > 0 and co2_change_pct < 0)

        out_rows.append({
            "country": country,
            "years": (int(group["year"].min()), int(group["year"].max())),
            "gdp_growth_pct": gdp_growth_pct,
            "co2_per_capita_change_pct": co2_change_pct,
            "green_growth": green,
        })

    return pd.DataFrame(out_rows)

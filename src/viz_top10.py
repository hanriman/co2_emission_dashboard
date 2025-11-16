import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List


def top10_countries_by_metric(df: pd.DataFrame, year: int, metric: str = "co2", continent_filter: Optional[List[str]] = None):
    """Return a Plotly bar figure with top 10 countries by `metric` for `year`.

    If `continent_filter` is provided, filter to those continents first.
    """
    df_year = df[df["year"] == year]
    if continent_filter:
        df_year = df_year[df_year["continent_name"].isin(continent_filter)]

    if metric not in df_year.columns:
        return None

    df_year = df_year.dropna(subset=[metric])
    top = df_year.sort_values(metric, ascending=False).head(10)
    if top.empty:
        return None

    fig = px.bar(top, x="country", y=metric, title=f"Top 10 countries by {metric} — {year}")
    return fig


def top10_co2_with_gdp(df: pd.DataFrame, year: int, continent_filter: Optional[List[str]] = None):
    """Return a dual-axis Plotly figure showing Top 10 countries by CO2 (bars) with GDP as a line (secondary y-axis).

    GDP is expected to be present in the `gdp` column for the given year.
    """
    df_year = df[df["year"] == year]
    if continent_filter:
        df_year = df_year[df_year["continent_name"].isin(continent_filter)]

    # ensure numeric
    df_year["co2"] = pd.to_numeric(df_year.get("co2"), errors="coerce")
    df_year["gdp"] = pd.to_numeric(df_year.get("gdp"), errors="coerce")

    df_year = df_year.dropna(subset=["co2"])
    if df_year.empty:
        return None

    top = df_year.sort_values("co2", ascending=False).head(10)
    if top.empty:
        return None

    countries = top["country"].tolist()
    co2_vals = top["co2"].tolist()
    gdp_vals = top["gdp"].fillna(0).tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=countries, y=co2_vals, name="CO2 (metric tons)"))
    fig.add_trace(go.Scatter(x=countries, y=gdp_vals, name="GDP (USD)", yaxis="y2", mode="lines+markers"))

    fig.update_layout(
        title=f"Top 10 countries by CO2 with GDP — {year}",
        xaxis=dict(title="Country"),
        yaxis=dict(title="CO2 (metric tons)"),
        yaxis2=dict(title="GDP (USD)", overlaying="y", side="right"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


def top10_by_co2_metric(df: pd.DataFrame, year: int, metric: str = "co2", continent_filter: Optional[List[str]] = None, add_gdp_line: bool = True):
    """Return a Plotly figure for Top 10 countries (ranked by CO2) showing `metric` as bars.

    If add_gdp_line is True, overlay GDP as a secondary y-axis line.
    The Top 10 selection is always based on the highest CO2 values for the year (per-country).
    """
    df_year = df[df["year"] == year]
    if continent_filter:
        df_year = df_year[df_year["continent_name"].isin(continent_filter)]

    # Ensure numeric columns
    df_year["co2"] = pd.to_numeric(df_year.get("co2"), errors="coerce")
    df_year[metric] = pd.to_numeric(df_year.get(metric), errors="coerce")
    df_year["gdp"] = pd.to_numeric(df_year.get("gdp"), errors="coerce")

    # Select top 10 by CO2
    df_year = df_year.dropna(subset=["co2"])
    if df_year.empty:
        return None

    top = df_year.sort_values("co2", ascending=False).head(10)
    if top.empty:
        return None

    countries = top["country"].tolist()
    metric_vals = top[metric].fillna(0).tolist() if metric in top.columns else [0] * len(countries)
    gdp_vals = top["gdp"].fillna(0).tolist()

    # Build figure: bars for the metric, optional GDP line on secondary y-axis
    fig = go.Figure()
    fig.add_trace(go.Bar(x=countries, y=metric_vals, name=f"{metric}"))

    if add_gdp_line:
        fig.add_trace(go.Scatter(x=countries, y=gdp_vals, name="GDP (USD)", yaxis="y2", mode="lines+markers"))

    # Titles and axis labels
    y_title = metric
    if metric == "co2":
        y_title = "CO2 (metric tons)"
    elif metric == "co2_per_capita":
        y_title = "CO2 per capita"
    elif metric == "population":
        y_title = "Population"

    layout = dict(
        title=f"Top 10 countries by CO2 (showing {metric}) — {year}",
        xaxis=dict(title="Country"),
        yaxis=dict(title=y_title),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    if add_gdp_line:
        layout["yaxis2"] = dict(title="GDP (USD)", overlaying="y", side="right")

    fig.update_layout(**layout)
    return fig

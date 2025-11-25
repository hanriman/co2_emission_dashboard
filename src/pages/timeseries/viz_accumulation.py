"""Analysis of cumulative CO2 emissions and historical responsibility.

Provides helpers to extract cumulative series and plot cumulative CO2
for multiple countries.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List


def get_cumulative_emissions(df: pd.DataFrame, country: Optional[str] = None) -> pd.DataFrame:
    """Get cumulative CO2 emissions data.

    If `country` is provided, the result is filtered to that country.
    Otherwise returns the full DataFrame (with cumulative cols coerced to numeric).
    """
    data = df.copy()

    if country:
        data = data[data["country"] == country]

    # Common cumulative column names used in some datasets; coerce if present
    cumulative_cols = [
        "cumulative_co2",
        "cumulative_co2_including_luc",
        "cumulative_coal_co2",
        "cumulative_oil_co2",
        "cumulative_gas_co2",
    ]

    for col in cumulative_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    return data


def plot_cumulative_trends(df: pd.DataFrame, countries: List[str]) -> Optional[go.Figure]:
    """Plot cumulative CO2 emissions over time for selected countries.

    Expects a column `cumulative_co2` (million tonnes). If not present,
    tries to fall back to computing cumulative sums of `co2` per country.
    """
    if df is None or len(countries) == 0:
        return None

    data = df.copy()
    data = data.dropna(subset=["country", "year"])  # minimal requirements

    # If dataset already contains cumulative columns, use them.
    if "cumulative_co2" in data.columns:
        data_filtered = data[data["country"].isin(countries)].copy()
        data_filtered = data_filtered.dropna(subset=["cumulative_co2", "year"]).copy()
        if data_filtered.empty:
            return None

        # Use a stacked-area (sandwich) chart to show cumulative responsibility
        fig = px.area(
            data_filtered,
            x="year",
            y="cumulative_co2",
            color="country",
            title="Cumulative CO2 Emissions Over Time",
            labels={"cumulative_co2": "Cumulative CO2 (Mt)"},
        )
        # stack traces so areas form a "sandwich" showing contributions
        fig.update_traces(stackgroup="one", mode="none", hoverinfo="x+y+name")
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Cumulative CO2 Emissions (million tonnes)",
            hovermode="x unified",
            legend_title_text="Country",
        )
        return fig

    # Otherwise compute cumulative sums from annual `co2` values
    if "co2" not in data.columns:
        return None

    data = data[data["country"].isin(countries)].copy()
    data["co2"] = pd.to_numeric(data["co2"], errors="coerce").fillna(0)
    # compute cumulative per country
    data = data.sort_values(["country", "year"]).copy()
    data["cum_co2"] = data.groupby("country")["co2"].cumsum()

    data_filtered = data.dropna(subset=["cum_co2", "year"]).copy()
    if data_filtered.empty:
        return None

    fig = px.area(
        data_filtered,
        x="year",
        y="cum_co2",
        color="country",
        title="Cumulative CO2 Emissions Over Time (computed)",
        labels={"cum_co2": "Cumulative CO2 (Mt)"},
    )
    fig.update_traces(stackgroup="one", mode="none", hoverinfo="x+y+name")
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative CO2 Emissions (million tonnes)",
        hovermode="x unified",
        legend_title_text="Country",
    )

    return fig

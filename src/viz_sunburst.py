import plotly.express as px
import pandas as pd
from typing import Optional, List


def sunburst_co2(df: pd.DataFrame, year: int, continents: Optional[List[str]] = None):
    """Create a sunburst (continent -> gdp_category -> country) sized by total CO2 for the given year.

    Expects a `gdp_category` column present in df. Returns a Plotly figure or None.
    """
    df_year = df[df["year"] == year]
    if continents:
        df_year = df_year[df_year["continent_name"].isin(continents)]

    if df_year.empty:
        return None

    # Ensure co2 numeric
    df_year["co2"] = pd.to_numeric(df_year.get("co2"), errors="coerce")
    df_year = df_year.dropna(subset=["co2"])
    if df_year.empty:
        return None

    # Use sunburst with path and co2 as values
    fig = px.sunburst(df_year, path=["continent_name", "gdp_category", "country"], values="co2",
                      title=f"CO2 sunburst — {year}")
    fig.update_layout(margin=dict(t=35, l=0, r=0, b=0))
    return fig


def sunburst_population(df: pd.DataFrame, year: int, continents: Optional[List[str]] = None):
    """Create a sunburst (continent -> gdp_category -> country) sized by population for the given year.

    Expects a `gdp_category` column present in df. Returns a Plotly figure or None.
    """
    df_year = df[df["year"] == year]
    if continents:
        df_year = df_year[df_year["continent_name"].isin(continents)]

    if df_year.empty:
        return None

    # Ensure population numeric
    df_year["population"] = pd.to_numeric(df_year.get("population"), errors="coerce")
    df_year = df_year.dropna(subset=["population"])
    if df_year.empty:
        return None

    fig = px.sunburst(df_year, path=["continent_name", "gdp_category", "country"], values="population",
                      title=f"Population sunburst — {year}")
    fig.update_layout(margin=dict(t=35, l=0, r=0, b=0))
    return fig

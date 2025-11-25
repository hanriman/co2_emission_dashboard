import plotly.express as px
import pandas as pd
from typing import Optional, Iterable, List, Sequence


# Default green->red diverging scale (low=green, high=red)
DEFAULT_GREEN_RED = px.colors.diverging.RdYlGn[::-1]


def _select_years(df: pd.DataFrame, years: Optional[Iterable[int]]):
    if years is None:
        return df.copy()
    if isinstance(years, int):
        return df[df["year"] == years].copy()
    return df[df["year"].isin(years)].copy()


def sunburst_co2(df: pd.DataFrame, years: Optional[Iterable[int]] = None, continents: Optional[List[str]] = None, color_scale: Optional[Sequence[str]] = None):
    """Create a sunburst (continent -> gdp_category -> country) sized by total CO2 for the given year(s).

    Aggregates total CO2 per country across selected years before plotting.
    `years` can be None, an int, or an iterable of years.
    """
    df_year = _select_years(df, years)
    if continents:
        df_year = df_year[df_year["continent_name"].isin(continents)]

    if df_year.empty:
        return None

    # Aggregate total CO2 per country so duplicates collapse correctly for multi-year
    df_year["co2"] = pd.to_numeric(df_year.get("co2"), errors="coerce")
    agg = df_year.groupby(["continent_name", "gdp_category", "country"], as_index=False).agg({"co2": "sum"})
    agg = agg.dropna(subset=["co2"]) if not agg.empty else agg
    if agg.empty:
        return None

    title = "CO2 sunburst"
    if years is not None:
        if isinstance(years, int):
            title = f"{title} — {years}"
        else:
            title = f"{title} — {','.join(str(int(y)) for y in sorted(set(years)))}"

    scale = color_scale or DEFAULT_GREEN_RED
    fig = px.sunburst(agg, path=["continent_name", "gdp_category", "country"], values="co2",
                      color="co2", color_continuous_scale=scale,
                      title=title)
    fig.update_layout(margin=dict(t=35, l=0, r=0, b=0))
    return fig


def sunburst_co2_percapita(df: pd.DataFrame, years: Optional[Iterable[int]] = None, continents: Optional[List[str]] = None, color_scale: Optional[Sequence[str]] = None):
    """Create a sunburst (continent -> gdp_category -> country) sized by CO2 per capita.

    Computes aggregated CO2 and population per country across selected years, then computes
    CO2 per capita as total_co2 / total_population and uses that as the sunburst value.
    """
    df_year = _select_years(df, years)
    if continents:
        df_year = df_year[df_year["continent_name"].isin(continents)]

    if df_year.empty:
        return None

    df_year["co2"] = pd.to_numeric(df_year.get("co2"), errors="coerce")
    df_year["population"] = pd.to_numeric(df_year.get("population"), errors="coerce")

    agg = df_year.groupby(["continent_name", "gdp_category", "country"], as_index=False).agg({
        "co2": "sum",
        "population": "sum",
    })
    if agg.empty:
        return None

    agg["co2_per_capita"] = agg.apply(lambda r: (r["co2"] / r["population"]) if r["population"] and not pd.isna(r["population"]) else pd.NA, axis=1)
    agg = agg.dropna(subset=["co2_per_capita"]) if not agg.empty else agg
    if agg.empty:
        return None

    title = "CO2 per capita sunburst"
    if years is not None:
        if isinstance(years, int):
            title = f"{title} — {years}"
        else:
            title = f"{title} — {','.join(str(int(y)) for y in sorted(set(years)))}"

    scale = color_scale or DEFAULT_GREEN_RED
    fig = px.sunburst(agg, path=["continent_name", "gdp_category", "country"], values="co2_per_capita",
                      color="co2_per_capita", color_continuous_scale=scale,
                      title=title)
    fig.update_layout(margin=dict(t=35, l=0, r=0, b=0))
    return fig

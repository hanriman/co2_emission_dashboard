import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List, Iterable, Union


def _normalize_years(years: Union[int, Iterable[int], None]) -> Optional[List[int]]:
    if years is None:
        return None
    if isinstance(years, int):
        return [years]
    try:
        return list(years)
    except Exception:
        return None


def _years_title(years_list: Optional[List[int]]) -> str:
    if not years_list:
        return "all years"
    years_sorted = sorted(years_list)
    if len(years_sorted) == 1:
        return str(years_sorted[0])
    if years_sorted[-1] - years_sorted[0] == len(years_sorted) - 1:
        return f"{years_sorted[0]}–{years_sorted[-1]}"
    return ",".join(map(str, years_sorted))


def top10_countries_by_metric(df: pd.DataFrame, years: Union[int, Iterable[int], None], metric: str = "co2", continent_filter: Optional[List[str]] = None):
    """Return a Plotly bar figure with top 10 countries by `metric` for `years`.

    `years` may be an int, an iterable of ints, or None (meaning all years).
    If `continent_filter` is provided, filter to those continents first.
    Aggregation: sums numeric columns across selected years; recomputes per-capita metrics.
    """
    years_list = _normalize_years(years)

    if years_list is None:
        df_sel = df.copy()
    else:
        df_sel = df[df["year"].isin(years_list)].copy()

    if continent_filter:
        df_sel = df_sel[df_sel["continent_name"].isin(continent_filter)].copy()

    if df_sel.empty:
        return None

    # Aggregate numeric columns per country across selected years
    agg = df_sel.groupby("country", as_index=False).agg({
        "co2": "sum",
        "gdp": "sum",
        "population": "sum",
    })

    # Recompute per-capita metrics where needed
    agg["co2_per_capita"] = agg.apply(lambda r: (r["co2"] / r["population"]) if r["population"] and not pd.isna(r["population"]) else pd.NA, axis=1)

    if metric not in agg.columns:
        return None

    agg = agg.dropna(subset=[metric])
    top = agg.sort_values(metric, ascending=False).head(10)
    if top.empty:
        return None

    title_years = _years_title(years_list)
    fig = px.bar(top, x="country", y=metric, title=f"Top 10 countries by {metric} — {title_years}")
    return fig


def top10_co2_with_gdp(df: pd.DataFrame, years: Union[int, Iterable[int], None], continent_filter: Optional[List[str]] = None):
    """Return a dual-axis Plotly figure showing Top 10 countries by CO2 (bars) with GDP as a line (secondary y-axis).

    Aggregates across `years` if provided.
    """
    years_list = _normalize_years(years)
    if years_list is None:
        df_sel = df.copy()
    else:
        df_sel = df[df["year"].isin(years_list)].copy()

    if continent_filter:
        df_sel = df_sel[df_sel["continent_name"].isin(continent_filter)].copy()

    if df_sel.empty:
        return None

    # Aggregate per country
    agg = df_sel.groupby("country", as_index=False).agg({
        "co2": "sum",
        "gdp": "sum",
    })

    agg["co2"] = pd.to_numeric(agg["co2"], errors="coerce")
    agg["gdp"] = pd.to_numeric(agg["gdp"], errors="coerce")

    agg = agg.dropna(subset=["co2"]) if not agg.empty else agg
    if agg.empty:
        return None

    top = agg.sort_values("co2", ascending=False).head(10)
    if top.empty:
        return None

    countries = top["country"].tolist()
    co2_vals = top["co2"].tolist()
    gdp_vals = top["gdp"].fillna(0).tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=countries, y=co2_vals, name="CO2 (metric tons)"))
    fig.add_trace(go.Scatter(x=countries, y=gdp_vals, name="GDP (USD)", yaxis="y2", mode="lines+markers"))

    title_years = _years_title(years_list)
    fig.update_layout(
        title=f"Top 10 countries by CO2 with GDP — {title_years}",
        xaxis=dict(title="Country"),
        yaxis=dict(title="CO2 (metric tons)"),
        yaxis2=dict(title="GDP (USD)", overlaying="y", side="right"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


def top10_by_co2_metric(df: pd.DataFrame, years: Union[int, Iterable[int], None], metric: str = "co2", continent_filter: Optional[List[str]] = None, add_gdp_line: bool = True):
    """Return a Plotly figure for Top 10 countries (ranked by CO2) showing `metric` as bars.

    If add_gdp_line is True, overlay GDP as a secondary y-axis line.
    The Top 10 selection is always based on the highest aggregated CO2 values for the selected years.
    """
    years_list = _normalize_years(years)
    if years_list is None:
        df_sel = df.copy()
    else:
        df_sel = df[df["year"].isin(years_list)].copy()

    if continent_filter:
        df_sel = df_sel[df_sel["continent_name"].isin(continent_filter)].copy()

    if df_sel.empty:
        return None

    # Aggregate per country
    agg = df_sel.groupby("country", as_index=False).agg({
        "co2": "sum",
        "gdp": "sum",
        "population": "sum",
    })

    agg["co2"] = pd.to_numeric(agg["co2"], errors="coerce")
    agg["gdp"] = pd.to_numeric(agg["gdp"], errors="coerce")
    agg["population"] = pd.to_numeric(agg["population"], errors="coerce")

    # Recompute per-capita metric
    agg["co2_per_capita"] = agg.apply(lambda r: (r["co2"] / r["population"]) if r["population"] and not pd.isna(r["population"]) else pd.NA, axis=1)

    # Select top 10 by the requested metric (fall back to CO2 if metric not present)
    select_col = metric if metric in agg.columns else "co2"
    agg = agg.dropna(subset=[select_col]) if not agg.empty else agg
    if agg.empty:
        return None

    top = agg.sort_values(select_col, ascending=False).head(10)
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

    title_years = _years_title(years_list)
    layout = dict(
        title=f"Top 10 countries by {select_col} (showing {metric}) — {title_years}",
        xaxis=dict(title="Country"),
        yaxis=dict(title=y_title),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    if add_gdp_line:
        layout["yaxis2"] = dict(title="GDP (USD)", overlaying="y", side="right")

    fig.update_layout(**layout)
    return fig

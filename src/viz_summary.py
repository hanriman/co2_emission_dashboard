import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Iterable, List, Union


def _normalize_years(years: Union[int, Iterable[int], None]):
    if years is None:
        return None
    if isinstance(years, int):
        return [years]
    try:
        return list(years)
    except Exception:
        return None


def summary_matrix(df: pd.DataFrame, years: Union[int, Iterable[int], None] = None, continents: Optional[List[str]] = None):
    """Return a Plotly table/metric matrix with three summary numbers:
    - Total CO2 (sum of `co2`)
    - CO2 per capita (total_co2 / total_population)
    - Avg global CO2 per capita (mean of per-country co2_per_capita)

    The function aggregates across selected years and optional continent filters.
    """
    years_list = _normalize_years(years)
    if years_list is None:
        df_sel = df.copy()
    else:
        df_sel = df[df["year"].isin(years_list)].copy()

    if continents:
        df_sel = df_sel[df_sel["continent_name"].isin(continents)].copy()

    # Ensure numeric
    df_sel["co2"] = pd.to_numeric(df_sel.get("co2"), errors="coerce")
    df_sel["population"] = pd.to_numeric(df_sel.get("population"), errors="coerce")
    df_sel["co2_per_capita"] = pd.to_numeric(df_sel.get("co2_per_capita"), errors="coerce")

    # Aggregate totals
    total_co2 = df_sel["co2"].sum(min_count=1)
    total_pop = df_sel["population"].sum(min_count=1)
    co2_per_capita = (total_co2 / total_pop) if total_pop and not pd.isna(total_pop) else None

    # Average global co2 per capita: mean of per-country co2_per_capita (using latest aggregated per-country values)
    per_country = df_sel.groupby("country", as_index=False).agg({"co2": "sum", "population": "sum"})
    per_country["co2_per_capita"] = per_country.apply(lambda r: (r["co2"] / r["population"]) if r["population"] and not pd.isna(r["population"]) else pd.NA, axis=1)
    avg_global_co2pc = per_country["co2_per_capita"].dropna().mean()

    # Format display values
    def fmt(x):
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return "—"
        if abs(x) >= 1e12:
            return f"{x/1e12:.2f}T"
        if abs(x) >= 1e9:
            return f"{x/1e9:.2f}B"
        if abs(x) >= 1e6:
            return f"{x/1e6:.2f}M"
        if isinstance(x, float):
            return f"{x:.2f}"
        return str(x)

    values = [fmt(total_co2), fmt(co2_per_capita), fmt(avg_global_co2pc)]
    labels = ["Total CO2", "CO2 per capita", "Avg global CO2 per capita"]

    fig = go.Figure(data=[go.Table(
        header=dict(values=labels, fill_color="#f2f2f2", align="center"),
        cells=dict(values=[values], align="center", height=80)
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=120)
    return fig

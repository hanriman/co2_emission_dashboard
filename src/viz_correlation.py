import pandas as pd
import numpy as np
import plotly.express as px
from typing import Optional, Iterable, List


def _select_and_aggregate(df: pd.DataFrame, years: Optional[Iterable[int]] = None, continents: Optional[List[str]] = None):
    if years is None:
        df_sel = df.copy()
    elif isinstance(years, int):
        df_sel = df[df["year"] == years].copy()
    else:
        df_sel = df[df["year"].isin(years)].copy()

    if continents:
        df_sel = df_sel[df_sel["continent_name"].isin(continents)].copy()

    # Ensure numeric
    df_sel["co2"] = pd.to_numeric(df_sel.get("co2"), errors="coerce")
    df_sel["gdp"] = pd.to_numeric(df_sel.get("gdp"), errors="coerce")
    df_sel["population"] = pd.to_numeric(df_sel.get("population"), errors="coerce")

    # Aggregate per country
    agg = df_sel.groupby(["country", "iso_code", "continent_name"], as_index=False).agg({
        "co2": "sum",
        "gdp": "sum",
        "population": "sum",
    })

    # Remove rows with no GDP or no CO2
    agg = agg.dropna(subset=["co2", "gdp"]) if not agg.empty else agg
    return agg


def correlation_gdp_co2(df: pd.DataFrame, years: Optional[Iterable[int]] = None, continents: Optional[List[str]] = None,
                        log_x: bool = True, log_y: bool = True, show_trend: bool = True):
    """Create a scatter plot showing correlation between GDP and CO2 per country.

    - Aggregates selected `years` per country (sums).
    - X axis: `gdp` (optionally log).
    - Y axis: `co2` (optionally log).
    - Color: `continent_name`.
    - Size: `population`.
    - `show_trend` fits a simple linear regression on (optionally log-transformed) data and overlays a trend line.
    Returns a Plotly figure or None if insufficient data.
    """
    agg = _select_and_aggregate(df, years=years, continents=continents)
    if agg.empty:
        return None

    # Prepare axis columns
    x = agg["gdp"].replace(0, np.nan)
    y = agg["co2"].replace(0, np.nan)

    if log_x:
        x_plot = np.log10(x)
        x_label = "log10(GDP)"
    else:
        x_plot = x
        x_label = "GDP (USD)"

    if log_y:
        y_plot = np.log10(y)
        y_label = "log10(CO2)"
    else:
        y_plot = y
        y_label = "CO2 (metric tons)"

    plot_df = agg.copy()
    plot_df["_x"] = x_plot
    plot_df["_y"] = y_plot

    # Remove rows with NaNs after transform
    plot_df = plot_df.dropna(subset=["_x", "_y"]) if not plot_df.empty else plot_df
    if plot_df.empty:
        return None

    fig = px.scatter(plot_df, x="_x", y="_y", color="continent_name", size="population",
                     hover_name="country", hover_data={"gdp": True, "co2": True, "population": True},
                     labels={"_x": x_label, "_y": y_label, "continent_name": "Continent"},
                     title="GDP vs CO2 (country-level)")

    if show_trend and len(plot_df) >= 2:
        # Fit linear regression on the plotted coordinates
        xs = plot_df["_x"].to_numpy()
        ys = plot_df["_y"].to_numpy()
        # Simple linear fit
        m, b = np.polyfit(xs, ys, 1)
        x_line = np.linspace(xs.min(), xs.max(), 100)
        y_line = m * x_line + b
        fig.add_traces(px.line(x=x_line, y=y_line, labels={"x": x_label, "y": y_label}).data)

        # Add annotation with slope and r^2
        # Compute R^2
        y_pred = m * xs + b
        ss_res = np.sum((ys - y_pred) ** 2)
        ss_tot = np.sum((ys - ys.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan
        fig.add_annotation(x=0.95, y=0.05, xref="paper", yref="paper",
                           text=f"slope={m:.2f}, $R^2$={r2:.2f}", showarrow=False,
                           bgcolor="rgba(255,255,255,0.8)")

    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig

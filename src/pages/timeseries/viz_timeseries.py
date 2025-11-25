import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List

from .forecast import forecast_series


def country_timeseries(df: pd.DataFrame, countries: List[str], metric: str = "co2_per_capita"):
    ts_df = df[df["country"].isin(countries)].sort_values(["country", "year"])
    if metric not in ts_df.columns:
        return None
    fig = px.line(ts_df, x="year", y=metric, color="country", markers=True,
                  title=f"{metric} over time")
    return fig


def country_forecast_plot(df: pd.DataFrame, country: str, metric: str = "co2", steps: int = 5):
    """Create a Plotly figure showing historical data, forecast, and 95% CI for a single country.

    Args:
        df: Full DataFrame with `country`, `year`, and the metric column.
        country: Country name to filter.
        metric: Metric column to forecast.
        steps: Number of future years to predict.

    Returns:
        plotly.graph_objects.Figure
    """
    ts = df[df["country"] == country].sort_values("year")
    if metric not in ts.columns:
        raise ValueError(f"Metric '{metric}' not found in dataframe")

    years = ts["year"].astype(int)
    values = ts[metric]

    # Build forecast DataFrame
    forecast_df = forecast_series(years, values, steps=steps)

    # Historical portion
    hist_x = forecast_df[forecast_df["y"].notna()]["year"]
    hist_y = forecast_df[forecast_df["y"].notna()]["y"]

    # Forecast portion
    fcast = forecast_df[forecast_df["y_pred"].notna()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_x, y=hist_y, mode="lines+markers", name="Observed", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=fcast["year"], y=fcast["y_pred"], mode="lines+markers", name="Forecast", line=dict(color="#ff7f0e")))

    # Confidence interval as filled area between lower and upper
    fig.add_trace(go.Scatter(
        x=fcast["year"],
        y=fcast["y_lower"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        name="lower"
    ))
    fig.add_trace(go.Scatter(
        x=fcast["year"],
        y=fcast["y_upper"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(255,127,14,0.2)",
        name="95% CI"
    ))

    fig.update_layout(title=f"{metric} forecast for {country}", xaxis_title="Year", yaxis_title=metric)
    return fig

import plotly.express as px
import pandas as pd
from typing import List


def country_timeseries(df: pd.DataFrame, countries: List[str], metric: str = "co2_per_capita"):
    ts_df = df[df["country"].isin(countries)].sort_values(["country", "year"])
    if metric not in ts_df.columns:
        return None
    fig = px.line(ts_df, x="year", y=metric, color="country", markers=True,
                  title=f"{metric} over time")
    return fig

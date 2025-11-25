import plotly.express as px
import pandas as pd
from typing import Iterable, Optional


def total_metric_by_continent(df: pd.DataFrame, years: Optional[Iterable[int]] = None, metric: str = "co2"):
    """Return a horizontal bar chart of total `metric` by continent for the given year(s).

    `years` can be None (use df as-is), an int, or an iterable of years. The function
    aggregates `metric` across the selection and shows a horizontal bar sorted descending.
    """
    if years is None:
        df_year = df.copy()
    elif isinstance(years, int):
        df_year = df[df["year"] == years].copy()
    else:
        df_year = df[df["year"].isin(years)].copy()

    if metric not in df_year.columns:
        # nothing to plot
        return None

    # ensure numeric for chosen metric
    df_year[metric] = pd.to_numeric(df_year.get(metric), errors="coerce")

    cont = df_year.groupby("continent_name")[metric].sum().reset_index()
    cont = cont.sort_values(metric, ascending=True)

    # horizontal bar: x=metric, y=continent_name
    label = metric
    if metric == "co2":
        label = "Total CO2 (metric tons)"
    elif metric == "gdp":
        label = "Total GDP (USD)"

    title = f"{label} by Continent"
    if years is not None:
        if isinstance(years, int):
            title = f"{title} — {years}"
        else:
            title = f"{title} — {','.join(str(int(y)) for y in sorted(set(years))) }"

    fig = px.bar(cont, x=metric, y="continent_name", orientation="h",
                 labels={metric: label, "continent_name": "Continent"},
                 title=title)

    # ensure largest is at top by explicitly setting the category order from the sorted DataFrame
    cont_order = cont["continent_name"].tolist()
    fig.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': cont_order})

    return fig


def total_co2_by_continent(df: pd.DataFrame, years: Optional[Iterable[int]] = None):
    return total_metric_by_continent(df, years=years, metric="co2")

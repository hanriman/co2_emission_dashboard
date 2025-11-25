from typing import Optional, Iterable, Sequence
import plotly.express as px
import pandas as pd


# Default green->red diverging scale (low=green, high=red)
DEFAULT_GREEN_RED = px.colors.diverging.RdYlGn[::-1]


def choropleth_co2(df: pd.DataFrame, years: Optional[Iterable[int]] = None, color_col: Optional[str] = None, color_scale: Optional[Sequence[str]] = None):
    """Create a choropleth for given year(s).

    `years` can be None (use df as-is), an int, or an iterable of years.
    """
    if years is None:
        df_year = df.dropna(subset=["iso_code"]).copy()
    elif isinstance(years, int):
        df_year = df[df["year"] == years].dropna(subset=["iso_code"]).copy()
    else:
        df_year = df[df["year"].isin(years)].dropna(subset=["iso_code"]).copy()

    if color_col and color_col in df_year.columns:
        col = color_col
    else:
        col = "co2 per capita" if "co2_per_capita" in df_year.columns else "co2"

    if df_year.empty:
        return None

    if years is not None:
        if isinstance(years, int):
            title = f"{years}"
        else:
            yrstr = ",".join(str(int(y)) for y in sorted(set(years)))
            title = f"{yrstr}"

    scale = color_scale or DEFAULT_GREEN_RED
    fig = px.choropleth(df_year, locations="iso_code", color=col,
                        hover_name="country", color_continuous_scale=scale,
                        title=title)
    fig.update_layout(margin=dict(l=0, r=0, t=35, b=0))
    return fig
    

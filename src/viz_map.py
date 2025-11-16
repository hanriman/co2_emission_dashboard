from typing import Optional
import plotly.express as px
import pandas as pd


def choropleth_co2(df: pd.DataFrame, year: int, color_col: Optional[str] = None):
    df_year = df[df["year"] == year].dropna(subset=["iso_code"])
    if color_col and color_col in df_year.columns:
        col = color_col
    else:
        col = "co2_per_capita" if "co2_per_capita" in df_year.columns else "co2"

    if df_year.empty:
        return None

    fig = px.choropleth(df_year, locations="iso_code", color=col,
                        hover_name="country", color_continuous_scale="Viridis",
                        title=f"CO2 ({col}) — {year}")
    fig.update_layout(margin=dict(l=0, r=0, t=35, b=0))
    return fig
    

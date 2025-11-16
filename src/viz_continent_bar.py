import plotly.express as px
import pandas as pd


def total_co2_by_continent(df: pd.DataFrame, year: int):
    """Return a horizontal bar chart of total CO2 by continent for the given year.

    The chart is horizontal (CO2 on x-axis, continent on y-axis) and sorted so the
    continent with largest CO2 appears at the top.
    """
    df_year = df[df["year"] == year]
    cont = df_year.groupby("continent_name")["co2"].sum().reset_index()
    cont = cont.sort_values("co2", ascending=True)

    # horizontal bar: x=co2, y=continent_name
    fig = px.bar(cont, x="co2", y="continent_name", orientation="h",
                 labels={"co2": "Total CO2 (metric tons)", "continent_name": ""},
                 title=f"Total CO2 by Continent — {year}")

    # ensure largest is at top by explicitly setting the category order from the sorted DataFrame
    cont_order = cont["continent_name"].tolist()
    fig.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': cont_order})

    return fig

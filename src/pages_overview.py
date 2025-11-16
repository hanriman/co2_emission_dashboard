import streamlit as st
from src.gdp_category import add_gdp_category
from src.viz_map import choropleth_co2
from src.viz_continent_bar import total_co2_by_continent
from src.viz_sunburst import sunburst_co2, sunburst_population
from src.viz_top10 import top10_countries_by_metric, top10_co2_with_gdp, top10_by_co2_metric
import pandas as pd


def render_overview(df: pd.DataFrame, year: int, selected_continents: list):
    """Render the Overview page into the current Streamlit app context.

    Inputs:
      - df: loaded DataFrame (raw from loader)
      - year: single integer year
      - selected_continents: list of continent names to include
    """
    # Ensure GDP categories are present (tertile per year)
    df_with_cat = add_gdp_category(df)

    # filter by the selected year and continents for overview aggregations
    df_overview = df_with_cat[(df_with_cat["year"] == int(year)) & (df_with_cat["continent_name"].isin(selected_continents))]

    # Top row: map + continent bar
    col1, col2 = st.columns((2, 1))

    with col1:
        st.subheader("World choropleth")
        fig_map = choropleth_co2(df_overview, year)
        if fig_map is None:
            st.write("No map data for selected year")
        else:
            st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.subheader("By continent")
        fig_bar = total_co2_by_continent(df_overview, year)
        if fig_bar is None:
            st.write("No continent data for selected year")
        else:
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    st.subheader("Sunburst: continent → GDP category → country (size = total CO2)")
    fig_sun = sunburst_co2(df_overview, year, continents=selected_continents)
    if fig_sun is None:
        st.write("No data for sunburst chart")
    else:
        st.plotly_chart(fig_sun, use_container_width=True)

    st.markdown("---")
    st.subheader("Sunburst: continent → GDP category → country (size = population)")
    fig_pop = sunburst_population(df_overview, year, continents=selected_continents)
    if fig_pop is None:
        st.write("No data for population sunburst")
    else:
        st.plotly_chart(fig_pop, use_container_width=True)

    st.markdown("---")

    st.subheader("Top 10 countries")
    # We rank Top 10 by highest CO2, and for metrics co2_per_capita and population
    # also overlay GDP as a secondary y-axis. The 'gdp' option is removed.
    metric = st.selectbox("Top metric", options=["co2", "co2_per_capita", "population"], index=0)
    if metric == "co2":
        fig_top10 = top10_co2_with_gdp(df_overview, year, continent_filter=selected_continents)
    elif metric in ("co2_per_capita", "population"):
        fig_top10 = top10_by_co2_metric(df_overview, year, metric=metric, continent_filter=selected_continents, add_gdp_line=True)
    else:
        fig_top10 = top10_countries_by_metric(df_overview, year, metric=metric, continent_filter=selected_continents)
    if fig_top10 is None:
        st.write("No data for Top 10 chart")
    else:
        st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("---")
    st.subheader("Filtered data")
    # For the data table, show totals per country for the selected year
    table_df = df_with_cat[(df_with_cat["year"] == int(year)) & (df_with_cat["continent_name"].isin(selected_continents))]

    agg_table = table_df.groupby(["country", "iso_code", "continent_name", "gdp_category"], as_index=False).agg({
        "co2": "sum",
        "population": "sum",
        "gdp": "sum",
    })

    st.dataframe(agg_table.head(500))
    csv = agg_table.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name=f"co2_filtered_{year}.csv")

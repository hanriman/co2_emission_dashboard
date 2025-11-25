import streamlit as st
from src.gdp_category import add_gdp_category
from src.viz_map import choropleth_co2
from src.viz_continent_bar import total_co2_by_continent
from src.viz_sunburst import sunburst_co2, sunburst_co2_percapita
from src.viz_top10 import top10_countries_by_metric, top10_co2_with_gdp, top10_by_co2_metric
import pandas as pd
from typing import Optional, Iterable, Union, List


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
        return "all"
    years_sorted = sorted(years_list)
    if len(years_sorted) == 1:
        return str(years_sorted[0])
    if years_sorted[-1] - years_sorted[0] == len(years_sorted) - 1:
        return f"{years_sorted[0]}–{years_sorted[-1]}"
    return ",".join(map(str, years_sorted))


def _cagr(start: float, end: float, periods: int) -> Optional[float]:
    try:
        if start is None or end is None or start == 0 or periods <= 0:
            return None
        return (end / start) ** (1.0 / periods) - 1.0
    except Exception:
        return None


def render_overview(df: pd.DataFrame, years: Union[int, Iterable[int], None], selected_continents: list):
    """Render the Overview page into the current Streamlit app context.

    Inputs:
      - df: loaded DataFrame (raw from loader)
      - years: int, iterable of ints, or None (all years)
      - selected_continents: list of continent names to include
    """
    # Ensure GDP categories are present (tertile per year)
    df_with_cat = add_gdp_category(df)

    years_list = _normalize_years(years)

    # Build a working selection filtered by years and continents for table / simple aggregations
    if years_list is None:
        df_sel = df_with_cat.copy()
    else:
        df_sel = df_with_cat[df_with_cat["year"].isin(years_list)].copy()

    if selected_continents:
        df_sel = df_sel[df_sel["continent_name"].isin(selected_continents)].copy()

    # (GDP category filter removed per user request)

    # Global summary: total global CO2 and CO2 per capita (sum across selected years)
    st.subheader("Global summary")
    if df_sel.empty:
        st.write("No data for selected filters")
    else:
        # ensure numeric
        for col in ("co2", "population"):
            if col in df_sel.columns:
                df_sel[col] = pd.to_numeric(df_sel[col], errors="coerce")

        total_co2 = df_sel["co2"].sum(min_count=1)
        total_pop = df_sel["population"].sum(min_count=1)

        # Compute per-capita correctly: `co2` is in million tonnes (Mt).
        # Convert to kilograms per person: (Mt * 1e9 kg/Mt) / population
        co2_per_capita_kg = None
        if pd.notna(total_co2) and pd.notna(total_pop) and total_pop > 0:
            co2_per_capita_kg = (total_co2 * 1e9) / total_pop

        c1, c2 = st.columns(2)
        with c1:
            if pd.notna(total_co2):
                # `co2` is in million tonnes according to the codebook
                st.metric("Total CO2 (Mt)", f"{total_co2:,.1f} Mt")
            else:
                st.metric("Total CO2 (Mt)", "n/a")

        with c2:
            if co2_per_capita_kg is not None:
                st.metric("Global CO2 per capita (kg/person)", f"{co2_per_capita_kg:,.1f} kg/person")
            else:
                st.metric("Global CO2 per capita (kg/person)", "n/a")

    # Centered world choropleths (Total CO2 and CO2 per capita stacked), with continent bar below
    # Centered choropleths stacked vertically
    left, mid, right = st.columns([1, 3, 1])
    with mid:
        st.subheader("World choropleth — Total CO2")
        # Prepare df for maps (apply continent + gdp filters)
        df_map = df_with_cat.copy()
        if selected_continents:
            df_map = df_map[df_map["continent_name"].isin(selected_continents)].copy()

        fig_map_total = choropleth_co2(df_map, years_list, color_col="co2")
        if fig_map_total is None:
            st.write("No map data for selected years")
        else:
            st.plotly_chart(fig_map_total, use_container_width=True)

        st.subheader("World choropleth — CO2 per capita")
        fig_map_pc = choropleth_co2(df_map, years_list, color_col="co2_per_capita")
        if fig_map_pc is None:
            st.write("No map data for selected years")
        else:
            st.plotly_chart(fig_map_pc, use_container_width=True)

    # Continent bar appears full-width below the centered maps
    st.subheader("By Continent")
    df_bar = df_with_cat.copy()
    if selected_continents:
        df_bar = df_bar[df_bar["continent_name"].isin(selected_continents)].copy()

    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("Total CO2 by Continent")
        fig_co2 = total_co2_by_continent(df_bar, years_list)
        if fig_co2 is None:
            st.write("No continent CO2 data for selected years")
        else:
            st.plotly_chart(fig_co2, use_container_width=True)

    with col_b:
        st.caption("Total GDP by Continent")
        # use the generic continent function to plot GDP
        try:
            from src.viz_continent_bar import total_metric_by_continent
        except Exception:
            total_metric_by_continent = None

        if total_metric_by_continent is None:
            st.write("GDP chart unavailable")
        else:
            fig_gdp = total_metric_by_continent(df_bar, years_list, metric="gdp")
            if fig_gdp is None:
                st.write("No continent GDP data for selected years")
            else:
                st.plotly_chart(fig_gdp, use_container_width=True)

    st.markdown("---")

    st.markdown("---")
    st.subheader("Sunbursts")
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Total CO2 (continent → GDP category → country)")
        fig_sun = sunburst_co2(df_with_cat, years=years_list, continents=selected_continents)
        if fig_sun is None:
            st.write("No data for sunburst chart")
        else:
            st.plotly_chart(fig_sun, use_container_width=True)

    with col2:
        st.caption("CO2 per capita (continent → GDP category → country)")
        fig_co2pc = sunburst_co2_percapita(df_with_cat, years=years_list, continents=selected_continents)
        if fig_co2pc is None:
            st.write("No data for CO2 per-capita sunburst")
        else:
            st.plotly_chart(fig_co2pc, use_container_width=True)

    st.markdown("---")

    st.subheader("Top 10 countries")
    # We rank Top 10 by highest CO2, and for metrics co2_per_capita and population
    # also overlay GDP as a secondary y-axis. The 'gdp' option is removed.
    metric = st.selectbox("Top metric", options=["co2", "co2_per_capita", "population"], index=0)
    if metric == "co2":
        fig_top10 = top10_co2_with_gdp(df_with_cat, years_list, continent_filter=selected_continents)
    elif metric in ("co2_per_capita", "population"):
        fig_top10 = top10_by_co2_metric(df_with_cat, years_list, metric=metric, continent_filter=selected_continents, add_gdp_line=True)
    else:
        fig_top10 = top10_countries_by_metric(df_with_cat, years_list, metric=metric, continent_filter=selected_continents)
    if fig_top10 is None:
        st.write("No data for Top 10 chart")
    else:
        st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("---")
    st.subheader("GDP vs CO2 correlation")
    try:
        from src.viz_correlation import correlation_gdp_co2
    except Exception:
        correlation_gdp_co2 = None

    if correlation_gdp_co2 is None:
        st.write("Correlation chart not available")
    else:
        # Options: log axes and show trend
        cols = st.columns([1,1,2])
        with cols[0]:
            log_x = st.checkbox("Log GDP (x)", value=True)
        with cols[1]:
            log_y = st.checkbox("Log CO2 (y)", value=True)
        with cols[2]:
            show_trend = st.checkbox("Show trend line", value=True)

        fig_corr = correlation_gdp_co2(df_with_cat, years=years_list, continents=selected_continents, log_x=log_x, log_y=log_y, show_trend=show_trend)
        if fig_corr is None:
            st.write("No data for correlation chart with selected filters")
        else:
            st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")
    st.subheader("Filtered data")
    # For the data table, show totals per country for the selected years and continents
    table_df = df_sel

    agg_table = table_df.groupby(["country", "iso_code", "continent_name", "gdp_category"], as_index=False).agg({
        "co2": "sum",
        "population": "sum",
        "gdp": "sum",
    })

    st.dataframe(agg_table.head(500))
    csv = agg_table.to_csv(index=False)
    years_label = _years_title(years_list)
    st.download_button("Download CSV", data=csv, file_name=f"co2_filtered_{years_label}.csv")

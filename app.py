import streamlit as st

from src.data_loader import load_data
from src.pages.overview.pages_overview import render_overview
from src.pages.timeseries.pages_timeseries import render_country_page


def main():
    st.set_page_config(layout="wide", page_title="CO2 Emissions dashboard")
    st.title("CO2 Emissions Dashboard")

    df = load_data()

    # Controls
    years = sorted(df["year"].dropna().astype(int).unique())
    # allow selecting multiple years; visualizations will aggregate across selected years
    selected_years = st.sidebar.multiselect("Years", options=years, default=[max(years)], key="years")

    continents = sorted(df["continent_name"].dropna().unique())
    selected_continents = st.sidebar.multiselect("Continent", options=continents, default=continents, key="continents")

    st.sidebar.markdown("---")
    st.sidebar.markdown("Data: Our World in Data CO2 dataset")

    # Page navigation
    page = st.sidebar.radio("Page", ["Overview", "Timeseries Analysis"]) 

    if page == "Overview":
        render_overview(df, selected_years, selected_continents)
    else:
        render_country_page(df)


if __name__ == "__main__":
    main()
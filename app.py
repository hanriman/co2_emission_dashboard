import streamlit as st

from src.data_loader import load_data
from src.pages_overview import render_overview
from src.pages_country import render_country_page


def main():
    st.set_page_config(layout="wide", page_title="CO2 Emissions dashboard")
    st.title("CO2 Emissions Dashboard")

    df = load_data()

    # Controls
    years = sorted(df["year"].dropna().astype(int).unique())
    year = st.sidebar.slider("Year", min_value=int(min(years)), max_value=int(max(years)), value=int(max(years)))

    continents = sorted(df["continent_name"].dropna().unique())
    selected_continents = st.sidebar.multiselect("Continent", options=continents, default=continents)

    st.sidebar.markdown("---")
    st.sidebar.markdown("Data: Our World in Data CO2 dataset")

    # Page navigation
    page = st.sidebar.radio("Page", ["Overview", "Country deep dive"]) 

    if page == "Overview":
        render_overview(df, int(year), selected_continents)
    else:
        render_country_page(df)


if __name__ == "__main__":
    main()

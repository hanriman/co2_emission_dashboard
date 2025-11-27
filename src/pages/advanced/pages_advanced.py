"""Streamlit page for advanced CO2 emissions analysis."""
import streamlit as st
import pandas as pd
from src.pages.advanced.analysis import (
    fuel_source_analysis,
    greenhouse_gas_analysis,
    temperature_impact_analysis,
)


def render_advanced_analysis_page(df: pd.DataFrame):
    """Render the Advanced Analysis page into the current Streamlit app context."""
    st.header("Advanced CO2 Emissions Analysis")
    st.markdown("Explore deeper insights into CO2 emissions: fuel sources, greenhouse gases, and temperature impact.")
    
    # Create tabs for different analysis types
    tab1, tab2, tab3 = st.tabs([
        "Fuel Sources",
        "Greenhouse Gases",
        "Temperature Impact"
    ])
    
    # Tab 1: Fuel Sources
    with tab1:
        st.subheader("CO2 Emissions by Fuel Source")
        st.markdown("Analyze emissions breakdown by fuel type: coal, oil, gas, cement, and flaring.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            country_list = sorted(df["country"].dropna().unique())
            selected_country = st.selectbox("Select Country", options=["All Countries"] + country_list, key="fuel_country")
        
        with col2:
            years = sorted(df["year"].dropna().astype(int).unique())
            selected_year = st.selectbox("Select Year", options=years, index=len(years)-1, key="fuel_year")
        
        if selected_country == "All Countries":
            # Show global fuel breakdown over time
            fig = fuel_source_analysis.plot_fuel_breakdown_timeseries(df, country=None)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No fuel source data available.")
        else:
            # Show country-specific analysis
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("**Time Series**")
                fig1 = fuel_source_analysis.plot_fuel_breakdown_timeseries(df, country=selected_country)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.warning("No fuel source data available for this country.")
            
            with col4:
                st.markdown("**Breakdown by Year**")
                fig2 = fuel_source_analysis.plot_fuel_breakdown_pie(df, selected_country, selected_year)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("No fuel source data available for this country/year.")
        
        # Top fuel consumers
        st.markdown("---")
        st.subheader("Top Fuel Consumers")
        fuel_type = st.selectbox(
            "Fuel Type",
            options=["coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2"],
            format_func=lambda x: x.replace("_co2", "").title(),
            key="top_fuel_type"
        )
        
        top_fuel = fuel_source_analysis.get_top_fuel_consumers(df, selected_year, fuel_type, top_n=10)
        if not top_fuel.empty:
            st.dataframe(top_fuel, use_container_width=True)
        else:
            st.warning("No data available for this fuel type.")
    
    # (Consumption, Efficiency, and Cumulative analyses removed per user request.)
    
    # Tab 2: Greenhouse Gases
    with tab2:
        st.subheader("Greenhouse Gas Emissions (Beyond CO2)")
        st.markdown("Analysis of methane, nitrous oxide, and total greenhouse gas emissions.")
        
        country_list = sorted(df["country"].dropna().unique())
        ghg_country = st.selectbox("Select Country", options=country_list, key="ghg_country")
        
        fig_ghg = greenhouse_gas_analysis.plot_ghg_composition(df, ghg_country)
        if fig_ghg:
            st.plotly_chart(fig_ghg, use_container_width=True)
        else:
            st.warning("No GHG data available for this country.")
        
        st.markdown("---")
        st.subheader("GHG Emissions Rankings")
        years = sorted(df["year"].dropna().astype(int).unique())
        ghg_year = st.selectbox("Select Year", options=years, index=len(years)-1, key="ghg_year")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top GHG Emitters per Capita**")
            top_ghg = greenhouse_gas_analysis.get_ghg_per_capita_ranking(df, ghg_year, top_n=15)
            if not top_ghg.empty:
                st.dataframe(top_ghg, use_container_width=True)
            else:
                st.warning("No GHG per capita data available.")
        
        with col2:
            st.markdown("**GHG vs CO2 Comparison**")
            fig_ghg_vs_co2 = greenhouse_gas_analysis.plot_ghg_vs_co2(df, ghg_year)
            if fig_ghg_vs_co2:
                st.plotly_chart(fig_ghg_vs_co2, use_container_width=True)
            else:
                st.warning("No GHG comparison data available.")
    
    # Tab 3: Temperature Impact
    with tab3:
        st.subheader("Temperature Impact from Emissions")
        st.markdown("🌡️ **Unique Analysis**: See how countries' emissions contribute to global temperature change. This shows the direct climate impact of emissions.")
        
        years = sorted(df["year"].dropna().astype(int).unique())
        temp_year = st.selectbox("Select Year", options=years, index=len(years)-1, key="temp_year")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Global Temperature Contribution Map**")
            fig_temp_map = temperature_impact_analysis.plot_temperature_contribution_map(df, temp_year)
            if fig_temp_map:
                st.plotly_chart(fig_temp_map, use_container_width=True)
            else:
                st.warning("No temperature impact data available. This data may not be available for all years.")
        
        with col2:
            st.markdown("**Top Temperature Contributors**")
            top_temp = temperature_impact_analysis.get_top_temperature_contributors(df, temp_year, top_n=15)
            if not top_temp.empty:
                st.dataframe(top_temp, use_container_width=True)
            else:
                st.warning("No temperature contribution data available.")
        
        st.markdown("---")
        st.subheader("Temperature Impact Analysis")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**Emissions vs Temperature Impact**")
            fig_temp_vs_co2 = temperature_impact_analysis.plot_temperature_vs_emissions(df, temp_year)
            if fig_temp_vs_co2:
                st.plotly_chart(fig_temp_vs_co2, use_container_width=True)
            else:
                st.warning("No temperature vs emissions data available.")
        
        with col4:
            st.markdown("**Temperature Breakdown by Gas**")
            country_list = sorted(df["country"].dropna().unique())
            temp_country = st.selectbox("Select Country", options=country_list, key="temp_country")
            
            fig_temp_breakdown = temperature_impact_analysis.plot_temperature_breakdown(df, temp_country)
            if fig_temp_breakdown:
                st.plotly_chart(fig_temp_breakdown, use_container_width=True)
            else:
                st.warning("No temperature breakdown data available for this country.")
        
        st.markdown("---")
        st.subheader("Cumulative Temperature Impact")
        country_list = sorted(df["country"].dropna().unique())
        selected_countries = st.multiselect(
            "Select Countries to Compare",
            options=country_list,
            default=country_list[:5] if len(country_list) >= 5 else country_list,
            key="temp_countries"
        )
        
        if selected_countries:
            fig_cum_temp = temperature_impact_analysis.plot_cumulative_temperature_impact(df, selected_countries)
            if fig_cum_temp:
                st.plotly_chart(fig_cum_temp, use_container_width=True)
            else:
                st.warning("No cumulative temperature data available.")


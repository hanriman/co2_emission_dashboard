"""Streamlit page for advanced CO2 emissions analysis."""
import streamlit as st
import pandas as pd
from src.analysis import (
    fuel_source_analysis,
    consumption_analysis,
    efficiency_analysis,
    cumulative_analysis,
    greenhouse_gas_analysis,
    temperature_impact_analysis
)


def render_advanced_analysis_page(df: pd.DataFrame):
    """Render the Advanced Analysis page into the current Streamlit app context."""
    st.header("Advanced CO2 Emissions Analysis")
    st.markdown("Explore deeper insights into CO2 emissions: fuel sources, consumption patterns, efficiency, cumulative emissions, and greenhouse gases.")
    
    # Create tabs for different analysis types
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Fuel Sources",
        "Consumption vs Production",
        "Efficiency Metrics",
        "Cumulative Emissions",
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
    
    # Tab 2: Consumption vs Production
    with tab2:
        st.subheader("Production vs Consumption-Based CO2 Emissions")
        st.markdown("Compare emissions from production (within borders) vs consumption (including trade).")
        
        country_list = sorted(df["country"].dropna().unique())
        selected_country = st.selectbox("Select Country", options=country_list, key="cons_country")
        
        fig = consumption_analysis.plot_production_vs_consumption(df, selected_country)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No consumption data available for this country.")
        
        st.markdown("---")
        st.subheader("Emission Trade Balance")
        st.markdown("Countries with positive balance are net exporters of emissions (via trade), negative are net importers.")
        
        years = sorted(df["year"].dropna().astype(int).unique())
        trade_year = st.selectbox("Select Year", options=years, index=len(years)-1, key="trade_year")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Map View**")
            fig_map = consumption_analysis.plot_trade_balance_map(df, trade_year)
            if fig_map:
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No trade balance data available.")
        
        with col2:
            st.markdown("**Top Exporters & Importers**")
            trade_data = consumption_analysis.get_net_exporters_importers(df, trade_year, top_n=10)
            
            if not trade_data["exporters"].empty:
                st.markdown("**Top Net Exporters**")
                st.dataframe(trade_data["exporters"], use_container_width=True)
            
            if not trade_data["importers"].empty:
                st.markdown("**Top Net Importers**")
                st.dataframe(trade_data["importers"], use_container_width=True)
    
    # Tab 3: Efficiency Metrics
    with tab3:
        st.subheader("CO2 Emissions Efficiency")
        st.markdown("Analyze how efficiently countries use energy and GDP to produce CO2 emissions.")
        
        years = sorted(df["year"].dropna().astype(int).unique())
        eff_year = st.selectbox("Select Year", options=years, index=len(years)-1, key="eff_year")
        
        metric = st.selectbox(
            "Efficiency Metric",
            options=["co2_per_gdp", "co2_per_unit_energy"],
            format_func=lambda x: x.replace("_", " ").title(),
            key="eff_metric"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Most Efficient Countries**")
            top_efficient = efficiency_analysis.get_most_efficient_countries(df, eff_year, metric, top_n=15)
            if not top_efficient.empty:
                st.dataframe(top_efficient, use_container_width=True)
            else:
                st.warning("No efficiency data available.")
        
        with col2:
            st.markdown("**Efficiency vs GDP**")
            fig_eff = efficiency_analysis.plot_efficiency_vs_gdp(df, eff_year)
            if fig_eff:
                st.plotly_chart(fig_eff, use_container_width=True)
            else:
                st.warning("No efficiency data available.")
        
        st.markdown("---")
        st.subheader("Efficiency Trends")
        country_list = sorted(df["country"].dropna().unique())
        selected_countries = st.multiselect(
            "Select Countries to Compare",
            options=country_list,
            default=country_list[:5] if len(country_list) >= 5 else country_list,
            key="eff_countries"
        )
        
        if selected_countries:
            fig_trends = efficiency_analysis.plot_efficiency_trends(df, selected_countries, metric)
            if fig_trends:
                st.plotly_chart(fig_trends, use_container_width=True)
            else:
                st.warning("No efficiency trend data available.")
        
        # Efficiency improvement for a country
        st.markdown("---")
        st.subheader("Efficiency Improvement Analysis")
        single_country = st.selectbox("Select Country", options=country_list, key="eff_single_country")
        
        improvement = efficiency_analysis.get_efficiency_improvement(df, single_country)
        if improvement:
            st.json(improvement)
        else:
            st.warning("No improvement data available for this country.")
    
    # Tab 4: Cumulative Emissions
    with tab4:
        st.subheader("Cumulative CO2 Emissions")
        st.markdown("Historical perspective on total emissions accumulated over time.")
        
        years = sorted(df["year"].dropna().astype(int).unique())
        cum_year = st.selectbox("Select Year", options=years, index=len(years)-1, key="cum_year")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Historical Emitters**")
            top_historical = cumulative_analysis.get_top_historical_emitters(df, cum_year, top_n=15)
            if not top_historical.empty:
                # Add share calculation
                total = top_historical["cumulative_co2"].sum()
                top_historical["share_pct"] = (top_historical["cumulative_co2"] / total * 100).round(2)
                st.dataframe(top_historical, use_container_width=True)
            else:
                st.warning("No cumulative emissions data available.")
        
        with col2:
            st.markdown("**Cumulative Trends**")
            country_list = sorted(df["country"].dropna().unique())
            selected_countries = st.multiselect(
                "Select Countries",
                options=country_list,
                default=country_list[:5] if len(country_list) >= 5 else country_list,
                key="cum_countries"
            )
            
            if selected_countries:
                fig_cum = cumulative_analysis.plot_cumulative_trends(df, selected_countries)
                if fig_cum:
                    st.plotly_chart(fig_cum, use_container_width=True)
                else:
                    st.warning("No cumulative data available.")
        
        st.markdown("---")
        st.subheader("Cumulative Emissions by Fuel Source")
        single_country = st.selectbox("Select Country", options=country_list, key="cum_single_country")
        
        fig_fuel_cum = cumulative_analysis.plot_cumulative_by_fuel(df, single_country)
        if fig_fuel_cum:
            st.plotly_chart(fig_fuel_cum, use_container_width=True)
        else:
            st.warning("No cumulative fuel data available for this country.")
    
    # Tab 5: Greenhouse Gases
    with tab5:
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
    
    # Tab 6: Temperature Impact
    with tab6:
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


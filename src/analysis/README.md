# Advanced CO2 Emissions Analysis

This folder contains comprehensive analysis modules for exploring CO2 emissions data beyond the basic visualizations.

## Modules

### 1. Fuel Source Analysis (`fuel_source_analysis.py`)
Analyzes CO2 emissions breakdown by fuel type:
- **Coal** emissions
- **Oil** emissions  
- **Gas** emissions
- **Cement** production emissions
- **Flaring** emissions

**Key Functions:**
- `get_fuel_breakdown()` - Get fuel source breakdown for countries/years
- `plot_fuel_breakdown_timeseries()` - Stacked area chart of fuel sources over time
- `plot_fuel_breakdown_pie()` - Pie chart for specific country/year
- `get_top_fuel_consumers()` - Top countries by fuel type

### 2. Consumption Analysis (`consumption_analysis.py`)
Compares production-based vs consumption-based CO2 emissions:
- **Production-based**: Emissions within country borders
- **Consumption-based**: Emissions including trade (embodied in imports/exports)
- **Trade balance**: Net exporters vs importers of emissions

**Key Functions:**
- `get_production_vs_consumption()` - Compare both metrics
- `plot_production_vs_consumption()` - Time series comparison
- `get_net_exporters_importers()` - Top net exporters and importers
- `plot_trade_balance_map()` - Choropleth map of emission trade balance

### 3. Efficiency Analysis (`efficiency_analysis.py`)
Analyzes how efficiently countries use resources:
- **CO2 per GDP**: Emissions intensity relative to economic output
- **CO2 per unit energy**: Emissions per energy consumed
- Efficiency trends and improvements over time

**Key Functions:**
- `calculate_efficiency_metrics()` - Calculate efficiency metrics
- `get_most_efficient_countries()` - Top countries by efficiency
- `plot_efficiency_trends()` - Efficiency trends over time
- `plot_efficiency_vs_gdp()` - Scatter plot of efficiency vs GDP
- `get_efficiency_improvement()` - Calculate efficiency improvements

### 4. Cumulative Analysis (`cumulative_analysis.py`)
Historical perspective on total accumulated emissions:
- **Cumulative CO2**: Total emissions since records began
- **Cumulative by fuel**: Historical breakdown by fuel source
- **Historical responsibility**: Countries' share of total cumulative emissions

**Key Functions:**
- `get_cumulative_emissions()` - Get cumulative emission data
- `plot_cumulative_trends()` - Cumulative trends over time
- `get_top_historical_emitters()` - Top historical emitters
- `plot_cumulative_by_fuel()` - Cumulative emissions by fuel source
- `calculate_historical_share()` - Calculate historical share of emissions

### 5. Greenhouse Gas Analysis (`greenhouse_gas_analysis.py`)
Analysis beyond CO2:
- **Methane** emissions (CO2-equivalent)
- **Nitrous oxide** emissions (CO2-equivalent)
- **Total GHG** emissions per capita
- Comparison of CO2 vs total GHG

**Key Functions:**
- `get_ghg_data()` - Get greenhouse gas data
- `plot_ghg_composition()` - Composition of GHGs over time
- `get_ghg_per_capita_ranking()` - Top GHG emitters per capita
- `plot_ghg_vs_co2()` - Comparison of total GHG vs CO2

### 6. Temperature Impact Analysis (`temperature_impact_analysis.py`) ⭐ NEW
**Unique and powerful analysis** showing direct climate impact:
- **Temperature contribution** from CO2, methane, and N2O emissions
- **Global temperature change** attributed to each country
- **Share of temperature change** from different greenhouse gases
- **Cumulative temperature impact** over time

**Key Functions:**
- `get_temperature_data()` - Get temperature impact data
- `plot_temperature_contribution_map()` - Choropleth map of temperature contributions
- `plot_temperature_breakdown()` - Breakdown by gas type (CO2, CH4, N2O)
- `get_top_temperature_contributors()` - Top contributors to global warming
- `plot_temperature_vs_emissions()` - Relationship between emissions and temperature impact
- `plot_cumulative_temperature_impact()` - Cumulative temperature impact over time

## Usage

All analysis modules are integrated into the Streamlit dashboard. Navigate to the **"Advanced Analysis"** page in the sidebar to access:

1. **Fuel Sources** tab - Explore emissions by fuel type
2. **Consumption vs Production** tab - Compare emission accounting methods
3. **Efficiency Metrics** tab - Analyze emission efficiency
4. **Cumulative Emissions** tab - Historical perspective
5. **Greenhouse Gases** tab - Beyond CO2 analysis
6. **Temperature Impact** tab - Direct climate impact visualization ⭐

## Data Requirements

The analysis modules work with the OWID CO2 dataset and expect the following columns (when available):
- Basic: `country`, `year`, `iso_code`, `continent_name`
- Emissions: `co2`, `co2_per_capita`, `consumption_co2`
- Fuel sources: `coal_co2`, `oil_co2`, `gas_co2`, `cement_co2`, `flaring_co2`
- Cumulative: `cumulative_co2`, `cumulative_coal_co2`, etc.
- Efficiency: `gdp`, `co2_per_gdp`, `co2_per_unit_energy`
- GHG: `methane`, `nitrous_oxide`, `ghg_per_capita`
- Temperature: `temperature_change_from_co2`, `temperature_change_from_ch4`, `temperature_change_from_n2o`, `temperature_change_from_ghg`, `share_of_temperature_change_from_ghg`

All modules handle missing data gracefully and will return empty results or None when data is unavailable.


"""Analysis of temperature impact from greenhouse gas emissions."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict


def get_temperature_data(df: pd.DataFrame) -> pd.DataFrame:
    """Get temperature impact data from emissions."""
    data = df.copy()
    
    temp_cols = [
        "temperature_change_from_co2",
        "temperature_change_from_ch4",
        "temperature_change_from_n2o",
        "temperature_change_from_ghg",
        "share_of_temperature_change_from_ghg"
    ]
    
    for col in temp_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    
    return data


def plot_temperature_contribution_map(df: pd.DataFrame, year: int) -> Optional[go.Figure]:
    """Plot choropleth map showing countries' contribution to global temperature change."""
    data = get_temperature_data(df)
    data_year = data[data["year"] == year].copy()
    
    if "temperature_change_from_ghg" not in data_year.columns or "iso_code" not in data_year.columns:
        return None
    
    data_year = data_year.dropna(subset=["iso_code", "temperature_change_from_ghg"])
    
    if data_year.empty:
        return None
    
    fig = px.choropleth(
        data_year,
        locations="iso_code",
        color="temperature_change_from_ghg",
        hover_name="country",
        hover_data=["temperature_change_from_ghg", "share_of_temperature_change_from_ghg"],
        color_continuous_scale="Reds",
        title=f"Contribution to Global Temperature Change ({year})<br>Change in °C from GHG emissions",
        labels={"temperature_change_from_ghg": "Temperature Change (°C)"}
    )
    
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    
    return fig


def plot_temperature_breakdown(df: pd.DataFrame, country: str) -> Optional[go.Figure]:
    """Plot breakdown of temperature contribution by gas type (CO2, methane, N2O)."""
    data = get_temperature_data(df)
    country_data = data[data["country"] == country].sort_values("year")
    
    if country_data.empty:
        return None
    
    available_cols = []
    if "temperature_change_from_co2" in country_data.columns:
        available_cols.append("temperature_change_from_co2")
    if "temperature_change_from_ch4" in country_data.columns:
        available_cols.append("temperature_change_from_ch4")
    if "temperature_change_from_n2o" in country_data.columns:
        available_cols.append("temperature_change_from_n2o")
    
    if not available_cols:
        return None
    
    country_data = country_data.dropna(subset=["year"] + available_cols, how="all")
    
    if country_data.empty:
        return None
    
    fig = go.Figure()
    
    colors = {
        "temperature_change_from_co2": "#FF6B6B",
        "temperature_change_from_ch4": "#4ECDC4",
        "temperature_change_from_n2o": "#95E1D3"
    }
    
    labels = {
        "temperature_change_from_co2": "CO2",
        "temperature_change_from_ch4": "Methane",
        "temperature_change_from_n2o": "Nitrous Oxide"
    }
    
    for col in available_cols:
        fig.add_trace(go.Scatter(
            x=country_data["year"],
            y=country_data[col],
            mode='lines+markers',
            name=labels.get(col, col),
            line=dict(color=colors.get(col, "#CCCCCC"), width=2),
            stackgroup='one'
        ))
    
    fig.update_layout(
        title=f"Temperature Contribution by Gas Type - {country}",
        xaxis_title="Year",
        yaxis_title="Temperature Change (°C)",
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig


def get_top_temperature_contributors(df: pd.DataFrame, year: int, top_n: int = 15) -> pd.DataFrame:
    """Get top contributors to global temperature change."""
    data = get_temperature_data(df)
    data_year = data[data["year"] == year].copy()
    
    if "temperature_change_from_ghg" not in data_year.columns:
        return pd.DataFrame()
    
    data_year = data_year.dropna(subset=["temperature_change_from_ghg"])
    
    top = data_year.nlargest(top_n, "temperature_change_from_ghg")[
        ["country", "temperature_change_from_ghg", "share_of_temperature_change_from_ghg", "continent_name"]
    ].sort_values("temperature_change_from_ghg", ascending=False)
    
    return top


def plot_temperature_vs_emissions(df: pd.DataFrame, year: int) -> Optional[go.Figure]:
    """Scatter plot showing relationship between emissions and temperature impact."""
    data = get_temperature_data(df)
    data_year = data[data["year"] == year].copy()
    
    if "temperature_change_from_ghg" not in data_year.columns or "co2" not in data_year.columns:
        return None
    
    data_year = data_year.dropna(subset=["temperature_change_from_ghg", "co2"])
    
    if data_year.empty:
        return None
    
    size_col = "population" if "population" in data_year.columns else None
    
    fig = px.scatter(
        data_year,
        x="co2",
        y="temperature_change_from_ghg",
        size=size_col,
        hover_name="country",
        color="continent_name",
        title=f"CO2 Emissions vs Temperature Impact ({year})",
        labels={
            "co2": "CO2 Emissions (million tonnes)",
            "temperature_change_from_ghg": "Temperature Change (°C)"
        }
    )
    
    return fig


def plot_cumulative_temperature_impact(df: pd.DataFrame, countries: List[str]) -> Optional[go.Figure]:
    """Plot cumulative temperature impact over time for selected countries."""
    data = get_temperature_data(df)
    data_filtered = data[data["country"].isin(countries)].copy()
    
    if "temperature_change_from_ghg" not in data_filtered.columns:
        return None
    
    data_filtered = data_filtered.dropna(subset=["temperature_change_from_ghg", "year"])
    
    if data_filtered.empty:
        return None
    
    # Calculate cumulative impact (sum of temperature changes)
    cumulative_data = []
    for country in countries:
        country_data = data_filtered[data_filtered["country"] == country].sort_values("year")
        if not country_data.empty:
            country_data = country_data.copy()
            country_data["cumulative_temp"] = country_data["temperature_change_from_ghg"].cumsum()
            cumulative_data.append(country_data)
    
    if not cumulative_data:
        return None
    
    combined = pd.concat(cumulative_data, ignore_index=True)
    
    fig = px.line(
        combined,
        x="year",
        y="cumulative_temp",
        color="country",
        markers=True,
        title="Cumulative Temperature Impact Over Time"
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative Temperature Change (°C)",
        hovermode='x unified'
    )
    
    return fig


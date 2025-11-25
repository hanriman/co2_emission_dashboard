"""Analysis of cumulative CO2 emissions and historical responsibility."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict


def get_cumulative_emissions(df: pd.DataFrame, country: Optional[str] = None) -> pd.DataFrame:
    """Get cumulative CO2 emissions data."""
    data = df.copy()
    
    if country:
        data = data[data["country"] == country]
    
    # Ensure numeric
    cumulative_cols = ["cumulative_co2", "cumulative_co2_including_luc", 
                       "cumulative_coal_co2", "cumulative_oil_co2", "cumulative_gas_co2"]
    
    for col in cumulative_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    
    return data


def plot_cumulative_trends(df: pd.DataFrame, countries: List[str]) -> Optional[go.Figure]:
    """Plot cumulative CO2 emissions over time for selected countries."""
    data = get_cumulative_emissions(df)
    data_filtered = data[data["country"].isin(countries)].copy()
    
    if "cumulative_co2" not in data_filtered.columns:
        return None
    
    data_filtered = data_filtered.dropna(subset=["cumulative_co2", "year"])
    
    if data_filtered.empty:
        return None
    
    fig = px.line(
        data_filtered,
        x="year",
        y="cumulative_co2",
        color="country",
        markers=True,
        title="Cumulative CO2 Emissions Over Time"
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative CO2 Emissions (million tonnes)",
        hovermode='x unified'
    )
    
    return fig


def get_top_historical_emitters(df: pd.DataFrame, year: int, top_n: int = 10) -> pd.DataFrame:
    """Get top historical emitters based on cumulative emissions."""
    data = get_cumulative_emissions(df)
    data_year = data[data["year"] == year].copy()
    
    if "cumulative_co2" not in data_year.columns:
        return pd.DataFrame()
    
    data_year = data_year.dropna(subset=["cumulative_co2"])
    
    top = data_year.nlargest(top_n, "cumulative_co2")[
        ["country", "cumulative_co2", "co2", "continent_name"]
    ].sort_values("cumulative_co2", ascending=False)
    
    return top


def plot_cumulative_by_fuel(df: pd.DataFrame, country: str) -> Optional[go.Figure]:
    """Plot cumulative emissions breakdown by fuel source."""
    data = get_cumulative_emissions(df, country=country)
    
    if data.empty:
        return None
    
    fuel_cols = ["cumulative_coal_co2", "cumulative_oil_co2", "cumulative_gas_co2"]
    available_cols = [col for col in fuel_cols if col in data.columns]
    
    if not available_cols:
        return None
    
    data = data.dropna(subset=["year"] + available_cols, how="all")
    
    if data.empty:
        return None
    
    fig = go.Figure()
    
    colors = {
        "cumulative_coal_co2": "#8B4513",
        "cumulative_oil_co2": "#000000",
        "cumulative_gas_co2": "#4169E1"
    }
    
    labels = {
        "cumulative_coal_co2": "Coal",
        "cumulative_oil_co2": "Oil",
        "cumulative_gas_co2": "Gas"
    }
    
    for col in available_cols:
        fig.add_trace(go.Scatter(
            x=data["year"],
            y=data[col],
            mode='lines',
            name=labels.get(col, col),
            line=dict(color=colors.get(col, "#CCCCCC"), width=2)
        ))
    
    fig.update_layout(
        title=f"Cumulative CO2 Emissions by Fuel Source - {country}",
        xaxis_title="Year",
        yaxis_title="Cumulative CO2 Emissions (million tonnes)",
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig


def calculate_historical_share(df: pd.DataFrame, year: int, top_n: int = 10) -> pd.DataFrame:
    """Calculate historical share of total cumulative emissions."""
    data = get_cumulative_emissions(df)
    data_year = data[data["year"] == year].copy()
    
    if "cumulative_co2" not in data_year.columns:
        return pd.DataFrame()
    
    data_year = data_year.dropna(subset=["cumulative_co2"])
    
    total_cumulative = data_year["cumulative_co2"].sum()
    
    top = get_top_historical_emitters(df, year, top_n)
    top["share_pct"] = (top["cumulative_co2"] / total_cumulative * 100).round(2)
    
    return top


"""Analysis of CO2 emissions by fuel source (coal, oil, gas, cement, flaring)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict


def get_fuel_breakdown(df: pd.DataFrame, country: Optional[str] = None, year: Optional[int] = None) -> pd.DataFrame:
    """Get CO2 emissions breakdown by fuel source for a country/year or aggregated.
    
    Args:
        df: Main dataframe
        country: If provided, filter to this country
        year: If provided, filter to this year
        
    Returns:
        DataFrame with fuel source columns and totals
    """
    data = df.copy()
    
    if country:
        data = data[data["country"] == country]
    if year:
        data = data[data["year"] == year]
    
    fuel_cols = ["coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2"]
    available_cols = [col for col in fuel_cols if col in data.columns]
    
    if not available_cols:
        return pd.DataFrame()
    
    # Convert to numeric
    for col in available_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    
    # Aggregate if needed
    if country and year:
        result = data[available_cols + ["country", "year"]].iloc[0:1]
    elif country:
        result = data.groupby(["country", "year"])[available_cols].sum().reset_index()
    elif year:
        result = data.groupby(["year", "country"])[available_cols].sum().reset_index()
    else:
        result = data.groupby(["year"])[available_cols].sum().reset_index()
    
    # Calculate total and percentages
    result["total_fuel_co2"] = result[available_cols].sum(axis=1)
    for col in available_cols:
        result[f"{col}_pct"] = (result[col] / result["total_fuel_co2"] * 100).round(2)
    
    return result


def plot_fuel_breakdown_timeseries(df: pd.DataFrame, country: Optional[str] = None) -> Optional[go.Figure]:
    """Plot stacked area chart showing fuel source breakdown over time."""
    fuel_data = get_fuel_breakdown(df, country=country)
    
    if fuel_data.empty:
        return None
    
    fuel_cols = ["coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2"]
    available_cols = [col for col in fuel_cols if col in fuel_data.columns]
    
    if not available_cols:
        return None
    
    # Aggregate by year if multiple countries
    if country is None:
        fuel_data = fuel_data.groupby("year")[available_cols].sum().reset_index()
    
    fig = go.Figure()
    
    colors = {
        "coal_co2": "#8B4513",
        "oil_co2": "#000000",
        "gas_co2": "#4169E1",
        "cement_co2": "#808080",
        "flaring_co2": "#FFD700"
    }
    
    labels = {
        "coal_co2": "Coal",
        "oil_co2": "Oil",
        "gas_co2": "Gas",
        "cement_co2": "Cement",
        "flaring_co2": "Flaring"
    }
    
    for col in available_cols:
        fig.add_trace(go.Scatter(
            x=fuel_data["year"],
            y=fuel_data[col],
            mode='lines',
            name=labels.get(col, col),
            stackgroup='one',
            fillcolor=colors.get(col, "#CCCCCC"),
            line=dict(width=0.5, color=colors.get(col, "#CCCCCC"))
        ))
    
    title = f"CO2 Emissions by Fuel Source Over Time"
    if country:
        title += f" - {country}"
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="CO2 Emissions (million tonnes)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_fuel_breakdown_pie(df: pd.DataFrame, country: str, year: int) -> Optional[go.Figure]:
    """Plot pie chart showing fuel source breakdown for a specific country/year."""
    fuel_data = get_fuel_breakdown(df, country=country, year=year)
    
    if fuel_data.empty:
        return None
    
    fuel_cols = ["coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2"]
    available_cols = [col for col in fuel_cols if col in fuel_data.columns]
    
    if not available_cols:
        return None
    
    values = []
    labels = []
    colors_list = []
    
    color_map = {
        "coal_co2": "#8B4513",
        "oil_co2": "#000000",
        "gas_co2": "#4169E1",
        "cement_co2": "#808080",
        "flaring_co2": "#FFD700"
    }
    
    label_map = {
        "coal_co2": "Coal",
        "oil_co2": "Oil",
        "gas_co2": "Gas",
        "cement_co2": "Cement",
        "flaring_co2": "Flaring"
    }
    
    for col in available_cols:
        val = fuel_data[col].iloc[0]
        if pd.notna(val) and val > 0:
            values.append(val)
            labels.append(label_map.get(col, col))
            colors_list.append(color_map.get(col, "#CCCCCC"))
    
    if not values:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors_list
    )])
    
    fig.update_layout(
        title=f"CO2 Emissions by Fuel Source - {country} ({year})"
    )
    
    return fig


def get_top_fuel_consumers(df: pd.DataFrame, year: int, fuel_type: str = "coal_co2", top_n: int = 10) -> pd.DataFrame:
    """Get top N countries by a specific fuel type for a given year."""
    df_year = df[df["year"] == year].copy()
    
    if fuel_type not in df_year.columns:
        return pd.DataFrame()
    
    df_year[fuel_type] = pd.to_numeric(df_year[fuel_type], errors="coerce")
    df_year = df_year.dropna(subset=[fuel_type])
    
    top = df_year.nlargest(top_n, fuel_type)[["country", fuel_type, "continent_name"]]
    
    return top.sort_values(fuel_type, ascending=True)


"""Analysis comparing production-based vs consumption-based CO2 emissions."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict


def get_production_vs_consumption(df: pd.DataFrame, country: Optional[str] = None) -> pd.DataFrame:
    """Compare production-based (co2) vs consumption-based (consumption_co2) emissions.
    
    Returns DataFrame with both metrics and their difference (trade balance).
    """
    data = df.copy()
    
    if country:
        data = data[data["country"] == country]
    
    # Ensure numeric
    if "co2" in data.columns:
        data["co2"] = pd.to_numeric(data["co2"], errors="coerce")
    if "consumption_co2" in data.columns:
        data["consumption_co2"] = pd.to_numeric(data["consumption_co2"], errors="coerce")
    
    # Calculate trade balance (positive = net exporter, negative = net importer)
    if "co2" in data.columns and "consumption_co2" in data.columns:
        data["emission_trade_balance"] = data["co2"] - data["consumption_co2"]
    
    cols = ["country", "year", "co2", "consumption_co2"]
    if "emission_trade_balance" in data.columns:
        cols.append("emission_trade_balance")
    
    available_cols = [col for col in cols if col in data.columns]
    
    return data[available_cols].dropna(subset=["co2", "consumption_co2"], how="all")


def plot_production_vs_consumption(df: pd.DataFrame, country: str) -> Optional[go.Figure]:
    """Plot comparison of production vs consumption CO2 emissions over time."""
    data = get_production_vs_consumption(df, country=country)
    
    if data.empty or "year" not in data.columns:
        return None
    
    fig = go.Figure()
    
    if "co2" in data.columns:
        fig.add_trace(go.Scatter(
            x=data["year"],
            y=data["co2"],
            mode='lines+markers',
            name='Production-based CO2',
            line=dict(color='#FF6B6B', width=2)
        ))
    
    if "consumption_co2" in data.columns:
        fig.add_trace(go.Scatter(
            x=data["year"],
            y=data["consumption_co2"],
            mode='lines+markers',
            name='Consumption-based CO2',
            line=dict(color='#4ECDC4', width=2)
        ))
    
    fig.update_layout(
        title=f"Production vs Consumption CO2 Emissions - {country}",
        xaxis_title="Year",
        yaxis_title="CO2 Emissions (million tonnes)",
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig


def get_net_exporters_importers(df: pd.DataFrame, year: int, top_n: int = 10) -> Dict[str, pd.DataFrame]:
    """Get top net exporters and importers of CO2 emissions (via trade).
    
    Returns dict with 'exporters' and 'importers' DataFrames.
    """
    data = get_production_vs_consumption(df)
    data_year = data[data["year"] == year].copy()
    
    if "emission_trade_balance" not in data_year.columns:
        return {"exporters": pd.DataFrame(), "importers": pd.DataFrame()}
    
    data_year = data_year.dropna(subset=["emission_trade_balance"])
    
    exporters = data_year.nlargest(top_n, "emission_trade_balance")[
        ["country", "co2", "consumption_co2", "emission_trade_balance"]
    ].sort_values("emission_trade_balance", ascending=False)
    
    importers = data_year.nsmallest(top_n, "emission_trade_balance")[
        ["country", "co2", "consumption_co2", "emission_trade_balance"]
    ].sort_values("emission_trade_balance", ascending=True)
    
    return {"exporters": exporters, "importers": importers}


def plot_trade_balance_map(df: pd.DataFrame, year: int) -> Optional[go.Figure]:
    """Plot choropleth map showing emission trade balance by country."""
    data = get_production_vs_consumption(df)
    data_year = data[data["year"] == year].copy()
    
    if "emission_trade_balance" not in data_year.columns or "iso_code" not in data_year.columns:
        return None
    
    data_year = data_year.dropna(subset=["iso_code", "emission_trade_balance"])
    
    if data_year.empty:
        return None
    
    fig = px.choropleth(
        data_year,
        locations="iso_code",
        color="emission_trade_balance",
        hover_name="country",
        color_continuous_scale="RdBu_r",
        title=f"CO2 Emission Trade Balance ({year})<br>Positive = Net Exporter, Negative = Net Importer",
        labels={"emission_trade_balance": "Trade Balance (million tonnes)"}
    )
    
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    
    return fig


"""Analysis of greenhouse gases beyond CO2 (methane, nitrous oxide)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict


def get_ghg_data(df: pd.DataFrame) -> pd.DataFrame:
    """Get greenhouse gas emissions data (CO2, methane, nitrous oxide)."""
    data = df.copy()
    
    ghg_cols = ["co2", "methane", "nitrous_oxide", "ghg_per_capita", "ghg_excluding_lucf_per_capita"]
    
    for col in ghg_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    
    return data


def plot_ghg_composition(df: pd.DataFrame, country: str) -> Optional[go.Figure]:
    """Plot composition of greenhouse gases (CO2, methane, nitrous oxide) over time."""
    data = get_ghg_data(df)
    country_data = data[data["country"] == country].sort_values("year")
    
    if country_data.empty:
        return None
    
    # Convert methane and nitrous oxide to CO2 equivalents (they're already in CO2-eq)
    available_cols = []
    if "co2" in country_data.columns:
        available_cols.append("co2")
    if "methane" in country_data.columns:
        available_cols.append("methane")
    if "nitrous_oxide" in country_data.columns:
        available_cols.append("nitrous_oxide")
    
    if not available_cols:
        return None
    
    country_data = country_data.dropna(subset=["year"] + available_cols, how="all")
    
    if country_data.empty:
        return None
    
    fig = go.Figure()
    
    colors = {
        "co2": "#FF6B6B",
        "methane": "#4ECDC4",
        "nitrous_oxide": "#95E1D3"
    }
    
    labels = {
        "co2": "CO2",
        "methane": "Methane (CO2-eq)",
        "nitrous_oxide": "Nitrous Oxide (CO2-eq)"
    }
    
    for col in available_cols:
        fig.add_trace(go.Scatter(
            x=country_data["year"],
            y=country_data[col],
            mode='lines+markers',
            name=labels.get(col, col),
            line=dict(color=colors.get(col, "#CCCCCC"), width=2)
        ))
    
    fig.update_layout(
        title=f"Greenhouse Gas Emissions - {country}",
        xaxis_title="Year",
        yaxis_title="Emissions (million tonnes CO2-eq)",
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig


def get_ghg_per_capita_ranking(df: pd.DataFrame, year: int, top_n: int = 10) -> pd.DataFrame:
    """Get top countries by GHG emissions per capita."""
    data = get_ghg_data(df)
    data_year = data[data["year"] == year].copy()
    
    # Try different GHG per capita columns
    ghg_cols = ["ghg_per_capita", "ghg_excluding_lucf_per_capita"]
    ghg_col = None
    
    for col in ghg_cols:
        if col in data_year.columns:
            ghg_col = col
            break
    
    if ghg_col is None:
        return pd.DataFrame()
    
    data_year[ghg_col] = pd.to_numeric(data_year[ghg_col], errors="coerce")
    data_year = data_year.dropna(subset=[ghg_col])
    
    top = data_year.nlargest(top_n, ghg_col)[
        ["country", ghg_col, "co2_per_capita", "continent_name"]
    ].sort_values(ghg_col, ascending=False)
    
    return top


def plot_ghg_vs_co2(df: pd.DataFrame, year: int) -> Optional[go.Figure]:
    """Scatter plot comparing total GHG vs CO2 emissions."""
    data = get_ghg_data(df)
    data_year = data[data["year"] == year].copy()
    
    # Calculate total GHG if we have components
    if "co2" in data_year.columns and "methane" in data_year.columns and "nitrous_oxide" in data_year.columns:
        data_year["total_ghg"] = (
            data_year["co2"].fillna(0) + 
            data_year["methane"].fillna(0) + 
            data_year["nitrous_oxide"].fillna(0)
        )
        
        data_year = data_year.dropna(subset=["co2", "total_ghg"])
        
        if data_year.empty:
            return None
        
        size_col = "population" if "population" in data_year.columns else None

        # Handle NaN / non-numeric values in the size column to avoid Plotly errors
        if size_col is not None:
            # Ensure numeric and coerce invalid values
            data_year[size_col] = pd.to_numeric(data_year[size_col], errors="coerce")

            if data_year[size_col].notna().any():
                # Replace remaining NaNs with a reasonable fallback (median or 1)
                median_size = data_year[size_col].median()
                if pd.isna(median_size) or median_size <= 0:
                    median_size = 1
                data_year[size_col] = data_year[size_col].fillna(median_size)
            else:
                # If all values are NaN, don't use size encoding
                size_col = None

        fig = px.scatter(
            data_year,
            x="co2",
            y="total_ghg",
            size=size_col,
            hover_name="country",
            color="continent_name",
            title=f"CO2 vs Total GHG Emissions ({year})",
            labels={
                "co2": "CO2 Emissions (million tonnes)",
                "total_ghg": "Total GHG Emissions (million tonnes CO2-eq)"
            }
        )
        
        # Add diagonal line (y=x)
        max_val = max(data_year["co2"].max(), data_year["total_ghg"].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='CO2 = Total GHG',
            line=dict(color='gray', dash='dash'),
            showlegend=False
        ))
        
        return fig
    
    return None


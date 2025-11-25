"""Analysis of CO2 emissions efficiency (CO2 per GDP, CO2 per energy unit)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict


def calculate_efficiency_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate efficiency metrics: CO2 per GDP and CO2 per unit energy."""
    data = df.copy()
    
    # Ensure numeric
    efficiency_cols = ["co2", "gdp", "energy_per_capita", "co2_per_gdp", "co2_per_unit_energy"]
    for col in efficiency_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    
    # Calculate if not present
    if "co2_per_gdp" not in data.columns and "co2" in data.columns and "gdp" in data.columns:
        data["co2_per_gdp"] = (data["co2"] * 1000) / data["gdp"]  # kg per $ (co2 in million tonnes, gdp in $)
        data["co2_per_gdp"] = data["co2_per_gdp"].replace([float('inf'), float('-inf')], pd.NA)
    
    return data


def get_most_efficient_countries(df: pd.DataFrame, year: int, metric: str = "co2_per_gdp", top_n: int = 10) -> pd.DataFrame:
    """Get countries with best (lowest) CO2 efficiency for a given metric."""
    data = calculate_efficiency_metrics(df)
    data_year = data[data["year"] == year].copy()
    
    if metric not in data_year.columns:
        return pd.DataFrame()
    
    data_year = data_year.dropna(subset=[metric])
    
    # For efficiency, lower is better
    top = data_year.nsmallest(top_n, metric)[["country", metric, "co2", "gdp", "continent_name"]]
    
    return top.sort_values(metric, ascending=True)


def plot_efficiency_trends(df: pd.DataFrame, countries: List[str], metric: str = "co2_per_gdp") -> Optional[go.Figure]:
    """Plot efficiency trends over time for selected countries."""
    data = calculate_efficiency_metrics(df)
    data_filtered = data[data["country"].isin(countries)].copy()
    
    if metric not in data_filtered.columns:
        return None
    
    data_filtered = data_filtered.dropna(subset=[metric, "year"])
    
    if data_filtered.empty:
        return None
    
    fig = px.line(
        data_filtered,
        x="year",
        y=metric,
        color="country",
        markers=True,
        title=f"{metric.replace('_', ' ').title()} Over Time"
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=metric.replace("_", " ").title(),
        hovermode='x unified'
    )
    
    return fig


def plot_efficiency_vs_gdp(df: pd.DataFrame, year: int) -> Optional[go.Figure]:
    """Scatter plot showing relationship between GDP and CO2 efficiency."""
    data = calculate_efficiency_metrics(df)
    data_year = data[data["year"] == year].copy()
    
    if "co2_per_gdp" not in data_year.columns or "gdp" not in data_year.columns:
        return None
    
    data_year = data_year.dropna(subset=["co2_per_gdp", "gdp"])
    
    if data_year.empty:
        return None
    
    # Add population for bubble size if available
    size_col = "population" if "population" in data_year.columns else None
    
    fig = px.scatter(
        data_year,
        x="gdp",
        y="co2_per_gdp",
        size=size_col,
        hover_name="country",
        color="continent_name",
        title=f"GDP vs CO2 Efficiency ({year})",
        labels={
            "gdp": "GDP (international $)",
            "co2_per_gdp": "CO2 per GDP (kg per $)"
        }
    )
    
    return fig


def get_efficiency_improvement(df: pd.DataFrame, country: str) -> Dict:
    """Calculate efficiency improvement metrics for a country."""
    data = calculate_efficiency_metrics(df)
    country_data = data[data["country"] == country].sort_values("year")
    
    if country_data.empty:
        return {}
    
    result = {"country": country}
    
    metrics = ["co2_per_gdp", "co2_per_unit_energy"]
    
    for metric in metrics:
        if metric in country_data.columns:
            values = country_data[metric].dropna()
            if len(values) >= 2:
                start_val = values.iloc[0]
                end_val = values.iloc[-1]
                if pd.notna(start_val) and pd.notna(end_val) and start_val != 0:
                    improvement_pct = ((end_val - start_val) / start_val) * 100
                    result[f"{metric}_change_pct"] = improvement_pct
                    result[f"{metric}_start"] = start_val
                    result[f"{metric}_end"] = end_val
    
    return result


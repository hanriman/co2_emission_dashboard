import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def render_country_page(df: pd.DataFrame):
    """Render the Country page as a timeseries analysis with line charts and a CO2 forecast.

    Shows:
    - Title: "Timeseries analysis"
    - Line charts for historical `co2`, `co2_per_capita`, and `population`.
    - CO2 forecast overlay when forecast data is available (reads `data/forecasts_co2.csv`).
    - Download button for the country time-series used.
    """
    st.subheader("Timeseries analysis")

    country_list = sorted(df["country"].dropna().unique())
    sel_country = st.selectbox("Choose a country", options=country_list, index=0)

    cdf = df[df["country"] == sel_country].sort_values("year").copy()
    if cdf.empty:
        st.write("No data for selected country")
        return

    # Ensure numeric columns
    for col in ("gdp", "co2", "co2_per_capita", "population"):
        if col in cdf.columns:
            cdf[col] = pd.to_numeric(cdf.get(col), errors="coerce")

    # Years covered
    years_min = int(cdf["year"].min())
    years_max = int(cdf["year"].max())
    st.write(f"Period: {years_min} — {years_max}")

    # CO2 line chart (with forecast overlay if available)
    fig_co2 = go.Figure()
    if "co2" in cdf.columns:
        fig_co2.add_trace(go.Scatter(x=cdf["year"], y=cdf["co2"], mode="lines+markers", name="Observed CO2 (Mt)"))

    # try to load forecast data for this country (pre-computed forecasts file)
    try:
        fdf = pd.read_csv("data/forecasts_co2.csv")
        f_country = fdf[(fdf["country"] == sel_country) & (fdf["metric"] == "co2")].copy()
        if not f_country.empty:
            # prediction columns: y_pred, y_lower, y_upper
            f_country = f_country.sort_values("year")
            if "y_pred" in f_country.columns and f_country["y_pred"].notna().any():
                fig_co2.add_trace(go.Scatter(x=f_country["year"], y=f_country["y_pred"], mode="lines", name="Forecast CO2", line=dict(dash="dash")))
                if "y_lower" in f_country.columns and "y_upper" in f_country.columns:
                    fig_co2.add_trace(go.Scatter(x=f_country["year"].tolist() + f_country["year"].tolist()[::-1],
                                                 y=f_country["y_upper"].tolist() + f_country["y_lower"].tolist()[::-1],
                                                 fill='toself', fillcolor='rgba(0,100,80,0.1)', line=dict(color='rgba(255,255,255,0)'),
                                                 hoverinfo="skip", showlegend=True, name="Forecast 95% CI"))
    except FileNotFoundError:
        f_country = pd.DataFrame()

    fig_co2.update_layout(title=f"CO2 emissions — {sel_country}", xaxis_title="Year", yaxis_title="CO2 (million tonnes)")
    st.plotly_chart(fig_co2, use_container_width=True)

    # CO2 per capita line chart
    if "co2_per_capita" in cdf.columns:
        fig_co2pc = px.line(cdf, x="year", y="co2_per_capita", markers=True, title=f"CO2 per capita — {sel_country}")
        fig_co2pc.update_yaxes(title_text="tonnes per person")
        st.plotly_chart(fig_co2pc, use_container_width=True)

    # Population trend
    if "population" in cdf.columns:
        fig_pop = px.line(cdf, x="year", y="population", markers=True, title=f"Population — {sel_country}")
        fig_pop.update_yaxes(title_text="people")
        st.plotly_chart(fig_pop, use_container_width=True)

    # Download enriched historical CSV
    display_cols = ["year"]
    for c in ("gdp", "co2", "co2_per_capita", "population"):
        if c in cdf.columns:
            display_cols.append(c)

    st.markdown("---")
    st.subheader("Country historical table")
    st.dataframe(cdf[display_cols].fillna("n/a"))
    csv = cdf[display_cols].to_csv(index=False)
    st.download_button("Download country historical CSV", data=csv, file_name=f"{sel_country}_history.csv")
    # Forecasting is provided from the precomputed CSV `data/forecasts_co2.csv` above.
    # On-demand forecasting utilities were removed to keep the app dependent
    # only on the precomputed CSV file.

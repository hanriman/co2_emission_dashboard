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

    # Accumulation (multi-country) — allow selecting which countries to show
    from src.pages.timeseries.viz_accumulation import plot_cumulative_trends
    # Forecast plotting helpers (global and GDP per-country)
    from src.pages.timeseries.viz_timeseries import global_forecast_plot, country_gdp_forecast_plot

    # default: show top 10 countries by total CO2 (baseline)
    if "co2" in df.columns:
        totals = df.groupby("country", dropna=True)["co2"].sum(min_count=1)
        top10 = totals.sort_values(ascending=False).dropna().head(10).index.tolist()
    else:
        top10 = country_list[:10]

    selected_countries = st.multiselect(
        "Countries — cumulative plot",
        options=country_list,
        default=top10,
        key="accum_countries",
    )

    fig_acc = plot_cumulative_trends(df, selected_countries)
    if fig_acc is None:
        st.write("No cumulative data available for selected countries")
    else:
        st.plotly_chart(fig_acc, use_container_width=True)

    # Forecast horizon control used for both global and per-country forecasts
    steps = st.slider("Forecast horizon (years)", min_value=1, max_value=20, value=5, key="forecast_steps")

    # Global CO2 total forecast (aggregate across countries)
    try:
        fig_global = global_forecast_plot(df, metric="co2", steps=steps)
        st.subheader("Global CO2 forecast (total)")
        st.plotly_chart(fig_global, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not compute global CO2 forecast: {e}")

    sel_country = st.selectbox("Choose a country", options=country_list, index=0)

    cdf = df[df["country"] == sel_country].sort_values("year").copy()
    if cdf.empty:
        st.write("No data for selected country")
        return

    # Ensure numeric columns
    for col in ("gdp", "co2", "co2_per_capita", "population"):
        if col in cdf.columns:
            cdf[col] = pd.to_numeric(cdf.get(col), errors="coerce")


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

    # Per-country GDP forecast (if GDP exists for this country)
    try:
        if "gdp" in cdf.columns and cdf["gdp"].notna().any():
            fig_gdp = country_gdp_forecast_plot(df, sel_country, steps=steps)
            st.subheader(f"GDP forecast — {sel_country}")
            st.plotly_chart(fig_gdp, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not compute GDP forecast for {sel_country}: {e}")

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

import streamlit as st
from src.country_analysis import country_summary, plot_country_trends, find_green_growth_countries
import pandas as pd


def render_country_page(df: pd.DataFrame):
    """Render the Country deep dive page into the current Streamlit app context."""
    st.subheader("Country deep dive")

    # Show countries that demonstrate "green growth" (GDP ↑ and CO2 per capita ↓)
    with st.expander("Countries showing green growth (GDP up & CO2 per capita down)"):
        gg_df = find_green_growth_countries(df)
        if gg_df.empty:
            st.write("No countries with confirmed green-growth pattern in data range.")
        else:
            # show only the positive ones
            gg_pos = gg_df[gg_df["green_growth"]].sort_values("country")
            if gg_pos.empty:
                st.write("No countries with confirmed green-growth pattern in data range.")
            else:
                display_df = gg_pos[["country", "years", "gdp_growth_pct", "co2_per_capita_change_pct"]].copy()
                # format percentages for readability
                display_df["gdp_growth_pct"] = display_df["gdp_growth_pct"].map(lambda v: f"{v:.1f}%" if pd.notna(v) else "n/a")
                display_df["co2_per_capita_change_pct"] = display_df["co2_per_capita_change_pct"].map(lambda v: f"{v:.1f}%" if pd.notna(v) else "n/a")
                st.dataframe(display_df.reset_index(drop=True))

    country_list = sorted(df["country"].dropna().unique())
    sel_country = st.selectbox("Choose a country", options=country_list, index=0)
    summary, cdf = country_summary(df, sel_country)
    if summary is None:
        st.write("No data for selected country")
        return

    st.metric(label="Period", value=f"{summary['years'][0]} — {summary['years'][1]}")
    gdp_text = f"{summary['gdp_growth_pct']:.1f}%" if summary['gdp_growth_pct'] is not None else "n/a"
    co2_text = f"{summary['co2_per_capita_change_pct']:.1f}%" if summary['co2_per_capita_change_pct'] is not None else "n/a"
    st.write(f"GDP growth: {gdp_text}")
    st.write(f"CO2 per capita change: {co2_text}")
    if summary.get('green_growth'):
        st.success("This country shows GDP growth while reducing CO2 per capita (green growth).")
    else:
        st.info("No clear green-growth pattern detected (GDP up & CO2pc down).")

    figs = plot_country_trends(cdf)
    for f in figs:
        st.plotly_chart(f, use_container_width=True)

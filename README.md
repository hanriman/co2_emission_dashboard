# CO2 Emissions Streamlit Dashboard

This small Streamlit app visualizes CO2 emissions from the Our World in Data dataset included in `data/`.

Files added:

How to run

1. Create a python environment (recommended: venv or conda).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run Streamlit:

```bash
streamlit run app.py
```

Then open the local URL printed by Streamlit in your browser.

Notes

Pages

- Overview: world choropleth, continent totals, and a Top-10 countries chart for the selected year and continent filters.
- Time series analysis: select a country to see GDP and CO2 per-capita trends and a small summary indicating whether the country experienced "green growth" (GDP up while CO2 per capita decreased) in the available period.

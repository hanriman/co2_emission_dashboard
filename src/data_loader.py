import pandas as pd
import streamlit as st


@st.cache_data
def load_data(data_dir: str = "data") -> pd.DataFrame:
    """Load and merge the OWID CO2 dataset with continent mapping.

    Returns a DataFrame with a normalized `continent_name` column.
    """
    df = pd.read_csv(f"{data_dir}/owid-co2-data.csv")
    countries = pd.read_csv(f"{data_dir}/country-and-continent-codes-list-csv.csv")

    countries = countries.rename(columns={
        "Three_Letter_Country_Code": "three_letter_code",
        "Country_Name": "country_name",
        "Continent_Name": "continent_name",
    })

    # Resolve known duplicates / transcontinental assignments with explicit overrides
    # User-specified preference: assign these ISO3 codes to the listed continent
    OVERRIDES = {
        "RUS": "Europe",   # Russian Federation -> Europe only
        "AZE": "Asia",     # Azerbaijan -> Asia
        "ARM": "Asia",     # Armenia -> Asia
        "CYP": "Europe",   # Cyprus -> Europe
        "GEO": "Europe",   # Georgia -> Europe
        "KAZ": "Asia",     # Kazakhstan -> Asia
        "UMI": "Oceania",  # United States Minor Outlying Islands -> Oceania
        "TUR": "Europe",   # Turkey -> Europe
    }

    # Apply overrides where applicable
    countries.loc[countries["three_letter_code"].isin(OVERRIDES.keys()), "continent_name"] = (
        countries.loc[countries["three_letter_code"].isin(OVERRIDES.keys()), "three_letter_code"].map(OVERRIDES)
    )

    # If the mapping file contains duplicate rows for the same three_letter_code,
    # keep the first occurrence after applying overrides to avoid producing multiple
    # matches during the merge (which would duplicate country-year rows).
    countries = countries.drop_duplicates(subset=["three_letter_code"]) 

    merged = df.merge(countries[["three_letter_code", "continent_name"]],
                      left_on="iso_code", right_on="three_letter_code", how="left")

    merged["continent_name"] = merged["continent_name"].fillna("Other")

    # Keep only country-level rows: drop entries without an ISO code
    # Some aggregate rows have empty or missing iso_code; remove them
    merged["iso_code"] = merged["iso_code"].replace("", pd.NA)
    merged = merged.dropna(subset=["iso_code"]) 

    # Ensure `year` is numeric and filter to the requested range (2000-2022)
    merged["year"] = pd.to_numeric(merged["year"], errors="coerce")
    merged = merged[merged["year"].between(2000, 2022)]

    return merged

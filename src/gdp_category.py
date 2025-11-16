import pandas as pd


def add_gdp_category(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a per-year `gdp_category` column: low/mid/high.

    Categories are determined per-year using tertiles (33% and 66%). Missing GDP -> 'Unknown'.
    """
    out = df.copy()
    out["gdp"] = pd.to_numeric(out.get("gdp"), errors="coerce")

    def assign(group: pd.DataFrame) -> pd.Series:
        g = group["gdp"].dropna()
        if g.empty:
            return pd.Series(["Unknown"] * len(group), index=group.index)
        q1 = g.quantile(0.33)
        q2 = g.quantile(0.66)

        def cat(v):
            if pd.isna(v):
                return "Unknown"
            if v <= q1:
                return "low"
            if v <= q2:
                return "mid"
            return "high"

        return group["gdp"].map(cat)

    out["gdp_category"] = out.groupby("year", group_keys=False).apply(assign)
    out["gdp_category"] = out["gdp_category"].fillna("Unknown")
    return out

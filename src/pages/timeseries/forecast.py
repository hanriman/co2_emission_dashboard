import numpy as np
import pandas as pd
from typing import Tuple

from statsmodels.tsa.statespace.sarimax import SARIMAX


def forecast_series(years: pd.Series, values: pd.Series, steps: int = 5, order=(1, 1, 1)) -> pd.DataFrame:
    """Fit a simple SARIMAX model to yearly data and forecast forward.

    Args:
        years: Series-like of integer year values (e.g., 2000, 2001, ...)
        values: Series-like of observed values aligned to `years`.
        steps: Number of years to forecast into the future.
        order: ARIMA order passed to SARIMAX.

    Returns:
        DataFrame with columns: `year`, `y` (observed, NaN for forecast years),
        `y_pred`, `y_lower`, `y_upper` (predictions and 95% CI).
    """
    # Prepare series indexed by year
    idx = pd.Index(np.asarray(years).astype(int), name="year")
    series = pd.Series(np.asarray(values, dtype=float), index=idx)

    # Drop missing values for fitting
    series_clean = series.dropna()
    if series_clean.empty:
        raise ValueError("No non-missing values to fit")

    last_year = int(series_clean.index.max())
    forecast_years = np.arange(last_year + 1, last_year + 1 + steps)

    # Fit a simple SARIMAX model (no seasonal component)
    try:
        model = SARIMAX(series_clean, order=order, enforce_stationarity=False, enforce_invertibility=False)
        res = model.fit(disp=False)
    except Exception:
        # Fall back to a very simple persistence forecast if fitting fails
        mean_val = series_clean.mean()
        preds = np.full(steps, mean_val)
        lower = preds - 0.1 * np.abs(preds)
        upper = preds + 0.1 * np.abs(preds)
        pred_index = pd.Index(forecast_years, name="year")
        df = pd.DataFrame({"y": series.reindex(series.index.union(pred_index)),
                           "y_pred": np.nan,
                           "y_lower": np.nan,
                           "y_upper": np.nan})
        df.loc[pred_index, ["y_pred", "y_lower", "y_upper"]] = np.vstack([preds, lower, upper]).T
        df = df.reset_index()
        return df

    # Produce forecast and 95% confidence intervals
    pred = res.get_forecast(steps=steps)
    pred_mean = pred.predicted_mean
    conf = pred.conf_int(alpha=0.05)

    # Build result DataFrame combining history and forecast
    all_index = series.index.union(pd.Index(forecast_years, name="year"))
    result = pd.DataFrame(index=all_index)
    result["y"] = series.reindex(all_index)
    result["y_pred"] = np.nan
    result["y_lower"] = np.nan
    result["y_upper"] = np.nan

    # Fill forecast portion
    result.loc[forecast_years, "y_pred"] = pred_mean.values
    # conf columns are named like 'lower y' and 'upper y'
    lower_col = conf.columns[0]
    upper_col = conf.columns[1]
    result.loc[forecast_years, "y_lower"] = conf[lower_col].values
    result.loc[forecast_years, "y_upper"] = conf[upper_col].values

    result = result.reset_index().rename(columns={"index": "year"})
    return result

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_log_returns(close: pd.Series) -> pd.Series:
    """
    Compute daily log returns.
    """
    log_ret = np.log(close / close.shift(1))
    log_ret = log_ret.dropna()
    log_ret.name = "log_return"
    return log_ret


def annualized_volatility(log_returns: pd.Series, trading_days: int = 252) -> float:
    """
    Annualized historical volatility from daily log returns.
    """
    return float(np.sqrt(trading_days) * log_returns.std(ddof=1))


def annualized_volatility_by_window(
    log_returns: pd.Series,
    windows: dict[str, int] | None = None,
    trading_days: int = 252,
) -> dict[str, float]:
    """
    Compute annualized vol over multiple trailing windows.
    """
    if windows is None:
        windows = {"3m": 63, "6m": 126, "1y": 252}

    vol_map: dict[str, float] = {}

    for label, win in windows.items():
        if len(log_returns) < win:
            vol_map[label] = float("nan")
        else:
            vol_map[label] = annualized_volatility(log_returns.tail(win), trading_days=trading_days)

    return vol_map


def summarize_market_inputs(
    market_df: pd.DataFrame,
    trading_days: int = 252,
) -> dict[str, float]:
    """
    Return a compact summary of key market inputs.
    """
    log_ret = compute_log_returns(market_df["close"])
    sigma = annualized_volatility(log_ret, trading_days=trading_days)

    return {
        "spot": float(market_df["close"].iloc[-1]),
        "risk_free_rate": float(market_df["rf"].iloc[-1]),
        "hist_vol": sigma,
    }
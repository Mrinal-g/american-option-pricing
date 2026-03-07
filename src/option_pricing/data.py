from __future__ import annotations

import pandas as pd
import yfinance as yf


def _to_series(obj: pd.Series | pd.DataFrame, name: str) -> pd.Series:
    """
    Convert yfinance output into a clean pandas Series with a fixed name.
    Handles Series, 1-column DataFrames, and MultiIndex-column DataFrames.
    """
    if isinstance(obj, pd.Series):
        s = obj.copy()
        s.name = name
        return s

    if isinstance(obj, pd.DataFrame):
        df = obj.copy()

        # If columns are MultiIndex, flatten by taking the first level if possible
        if isinstance(df.columns, pd.MultiIndex):
            # Try to find a column whose first level is "Close"
            close_cols = [col for col in df.columns if col[0] == "Close"]
            if close_cols:
                s = df[close_cols[0]].copy()
                s.name = name
                return s

        # If normal DataFrame and requested column exists
        if "Close" in df.columns:
            s = df["Close"].copy()
            s.name = name
            return s

        # If only one column exists, use it
        if df.shape[1] == 1:
            s = df.iloc[:, 0].copy()
            s.name = name
            return s

    raise ValueError(f"Could not convert downloaded data into Series for '{name}'.")


def fetch_adjusted_close(
    ticker: str,
    start_date: str,
    end_date: str,
) -> pd.Series:
    """
    Download adjusted close prices for the underlying from Yahoo Finance.
    """
    df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"No price data returned for ticker={ticker}.")

    close = _to_series(df, name="close").dropna()
    return close


def fetch_risk_free_rate(
    start_date: str,
    end_date: str,
    rf_ticker: str = "^IRX",
) -> pd.Series:
    """
    Download short-term risk-free proxy from Yahoo Finance.

    ^IRX is quoted in percent, so we convert it to decimal.
    """
    df = yf.download(
        rf_ticker,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"No risk-free data returned for ticker={rf_ticker}.")

    rf = _to_series(df, name="rf").dropna() / 100.0
    rf.name = "rf"
    return rf


def build_market_dataframe(
    ticker: str,
    start_date: str,
    end_date: str,
    rf_ticker: str = "^IRX",
) -> pd.DataFrame:
    """
    Build a combined market dataframe with columns:
    - close
    - rf
    """
    close = fetch_adjusted_close(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    rf = fetch_risk_free_rate(
        start_date=start_date,
        end_date=end_date,
        rf_ticker=rf_ticker,
    )

    # Align rf to stock trading dates
    rf = rf.reindex(close.index).ffill().bfill()

    market_df = pd.concat([close, rf], axis=1)
    market_df.columns = ["close", "rf"]
    market_df = market_df.dropna()

    if market_df.empty:
        raise ValueError("Combined market dataframe is empty after alignment.")

    return market_df


def fetch_option_expiries(ticker: str) -> list[str]:
    """
    Fetch all available option expiry dates for a ticker.
    """
    tk = yf.Ticker(ticker)
    expiries = tk.options

    if expiries is None:
        return []

    return list(expiries)


def fetch_option_chain(
    ticker: str,
    expiry: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch option chain for a given expiry.
    """
    tk = yf.Ticker(ticker)
    chain = tk.option_chain(expiry)

    calls = chain.calls.copy()
    puts = chain.puts.copy()

    return calls, puts


def fetch_option_mid_prices(
    ticker: str,
    expiry: str,
    option_type: str = "call",
) -> pd.DataFrame:
    """
    Fetch option chain and compute midpoint price = (bid + ask) / 2.
    """
    calls, puts = fetch_option_chain(ticker, expiry)

    if option_type.lower() == "call":
        df = calls.copy()
    elif option_type.lower() == "put":
        df = puts.copy()
    else:
        raise ValueError("option_type must be 'call' or 'put'.")

    df["mid"] = (df["bid"] + df["ask"]) / 2.0
    return df


def get_latest_market_inputs(
    ticker: str,
    start_date: str,
    end_date: str,
    rf_ticker: str = "^IRX",
) -> dict[str, float]:
    """
    Convenience helper to fetch latest spot and risk-free rate.
    """
    market_df = build_market_dataframe(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        rf_ticker=rf_ticker,
    )

    return {
        "spot": float(market_df["close"].iloc[-1]),
        "rate": float(market_df["rf"].iloc[-1]),
    }
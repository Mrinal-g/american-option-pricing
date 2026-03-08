from __future__ import annotations

import pandas as pd

from option_pricing.black_scholes import BlackScholesEngine
from option_pricing.binomial_crr import CRREngine
from option_pricing.instruments import OptionContract
from option_pricing.market import MarketData


def compare_bsm_vs_crr(
    contract: OptionContract,
    market: MarketData,
    steps: int,
) -> dict[str, float | int | str]:
    """
    Compare Black-Scholes price with CRR European price for a given step count.

    Notes
    -----
    Black-Scholes is only valid for European options, so this function assumes
    the input contract is European.
    """
    if contract.style != "european":
        raise ValueError("compare_bsm_vs_crr requires a European contract.")

    bs_engine = BlackScholesEngine()
    crr_engine = CRREngine(steps=steps)

    bs_result = bs_engine.price(contract, market)
    crr_result = crr_engine.price(contract, market)

    abs_error = abs(crr_result.price - bs_result.price)
    rel_error = abs_error / abs(bs_result.price) if bs_result.price != 0 else float("nan")

    return {
        "option_type": contract.option_type,
        "strike": contract.strike,
        "maturity": contract.maturity,
        "steps": steps,
        "bs_price": bs_result.price,
        "crr_price": crr_result.price,
        "abs_error": abs_error,
        "rel_error": rel_error,
        "bs_delta": bs_result.delta,
        "crr_delta": crr_result.delta,
        "bs_gamma": bs_result.gamma,
        "crr_gamma": crr_result.gamma,
        "bs_theta": bs_result.theta,
        "crr_theta": crr_result.theta,
    }


def run_crr_convergence_study(
    contract: OptionContract,
    market: MarketData,
    step_list: list[int] | None = None,
) -> pd.DataFrame:
    """
    Run a convergence study of CRR European pricing versus Black-Scholes.
    """
    if contract.style != "european":
        raise ValueError("run_crr_convergence_study requires a European contract.")

    if step_list is None:
        step_list = [10, 25, 50, 100, 250, 500, 1000]

    rows = []
    for steps in step_list:
        row = compare_bsm_vs_crr(contract, market, steps)
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def summarize_convergence(df: pd.DataFrame) -> dict[str, float]:
    """
    Return a compact summary of convergence results.
    """
    if df.empty:
        raise ValueError("Convergence DataFrame is empty.")

    best_row = df.loc[df["abs_error"].idxmin()]

    return {
        "min_abs_error": float(df["abs_error"].min()),
        "min_rel_error": float(df["rel_error"].min()),
        "best_steps": int(best_row["steps"]),
        "best_crr_price": float(best_row["crr_price"]),
        "bs_price": float(best_row["bs_price"]),
    }
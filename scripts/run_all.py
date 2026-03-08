
# from __future__ import annotations

# import sys
# from pathlib import Path

# # Allow running from project root: python scripts/run_all.py
# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# SRC_PATH = PROJECT_ROOT / "src"
# sys.path.append(str(SRC_PATH))

# from option_pricing.config import ProjectConfig
# from option_pricing.data import build_market_dataframe
# from option_pricing.instruments import OptionContract
# from option_pricing.market import MarketData
# from option_pricing.stats import summarize_market_inputs


# def main() -> None:
#     cfg = ProjectConfig()

#     market_df = build_market_dataframe(
#         ticker=cfg.ticker,
#         start_date=cfg.start_date,
#         end_date=cfg.end_date,
#     )

#     print("market_df columns:", market_df.columns.tolist())
#     print(market_df.head())
#     print()
    
#     summary = summarize_market_inputs(
#         market_df,
#         trading_days=cfg.trading_days,
#     )

#     maturity_years = cfg.maturity_days / cfg.trading_days

#     contract = OptionContract(
#         option_type=cfg.option_type,
#         strike=cfg.strikes[0],
#         maturity=maturity_years,
#         style=cfg.style,
#     )

#     market = MarketData(
#         spot=summary["spot"],
#         rate=summary["risk_free_rate"],
#         volatility=summary["hist_vol"],
#         dividend=cfg.dividend_yield,
#     )

#     print("=== Project Config ===")
#     print(cfg)
#     print()

#     print("=== Market Input Summary ===")
#     for key, value in summary.items():
#         print(f"{key}: {value:.6f}")
#     print()

#     print("=== Sample Contract ===")
#     print(contract)
#     print()

#     print("=== Sample MarketData ===")
#     print(market)


# if __name__ == "__main__":
#     main()



from __future__ import annotations

import sys
from pathlib import Path

# Allow running from project root: python scripts/run_all.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from option_pricing.black_scholes import BlackScholesEngine
from option_pricing.config import ProjectConfig
from option_pricing.data import build_market_dataframe
from option_pricing.instruments import OptionContract
from option_pricing.market import MarketData
from option_pricing.stats import summarize_market_inputs


def main() -> None:
    cfg = ProjectConfig()

    market_df = build_market_dataframe(
        ticker=cfg.ticker,
        start_date=cfg.start_date,
        end_date=cfg.end_date,
    )

    print("market_df columns:", market_df.columns.tolist())
    print(market_df.head())
    print()

    summary = summarize_market_inputs(
        market_df,
        trading_days=cfg.trading_days,
    )

    maturity_years = cfg.maturity_days / cfg.trading_days

    contract = OptionContract(
        option_type=cfg.option_type,
        strike=cfg.strikes[0],
        maturity=maturity_years,
        style=cfg.style,
    )

    market = MarketData(
        spot=summary["spot"],
        rate=summary["risk_free_rate"],
        volatility=summary["hist_vol"],
        dividend=cfg.dividend_yield,
    )

    print("=== Project Config ===")
    print(cfg)
    print()

    print("=== Market Input Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value:.6f}")
    print()

    print("=== Sample Contract ===")
    print(contract)
    print()

    print("=== Sample MarketData ===")
    print(market)
    print()

    # Black-Scholes requires a European option
    european_contract = OptionContract(
        option_type=cfg.option_type,
        strike=cfg.strikes[0],
        maturity=maturity_years,
        style="european",
    )

    bs_engine = BlackScholesEngine()
    bs_result = bs_engine.price(european_contract, market)

    print("=== Black-Scholes Result (European) ===")
    print(f"option type : {european_contract.option_type}")
    print(f"strike      : {european_contract.strike}")
    print(f"maturity    : {european_contract.maturity:.6f} years")
    print()

    print(f"price : {bs_result.price:.6f}")
    print(f"delta : {bs_result.delta:.6f}")
    print(f"gamma : {bs_result.gamma:.6f}")

    theta_daily = bs_result.theta / cfg.trading_days
    print(f"theta (annual): {bs_result.theta:.6f}")
    print(f"theta (daily) : {theta_daily:.6f}")

    print(f"vega  : {bs_result.vega:.6f}")
    print(f"rho   : {bs_result.rho:.6f}")


if __name__ == "__main__":
    main()
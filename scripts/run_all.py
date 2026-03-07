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
#         rf_source=cfg.rf_source,
#         fred_series=cfg.fred_series,
#         constant_rf=cfg.constant_rf,
#     )

#     summary = summarize_market_inputs(market_df, trading_days=cfg.trading_days)

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


if __name__ == "__main__":
    main()
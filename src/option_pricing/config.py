from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectConfig:
    # Underlying and market data window
    ticker: str = "GOOG"
    start_date: str = "2022-12-01"
    end_date: str = "2023-12-02"

    # Trading convention
    trading_days: int = 252

    # Option setup
    strikes: list[float] = field(default_factory=lambda: [120, 121, 123, 125, 126, 128, 130])
    maturity_days: int = 10
    option_type: str = "put"
    style: str = "american"
    dividend_yield: float = 0.0

    # Binomial settings
    crr_steps: int = 100

    # LSM settings
    lsm_paths: int = 20000
    lsm_steps: int = 50
    random_seed: int = 42

    # Hedging settings
    contract_size: int = 100
    transaction_cost_bps: float = 0.0
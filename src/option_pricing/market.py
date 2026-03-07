from dataclasses import dataclass


@dataclass(frozen=True)
class MarketData:
    spot: float
    rate: float
    volatility: float
    dividend: float = 0.0

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("spot must be positive.")

        if self.volatility <= 0:
            raise ValueError("volatility must be positive.")
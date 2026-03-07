from dataclasses import dataclass


@dataclass
class PricingResult:
    price: float
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    rho: float | None = None
    stderr: float | None = None
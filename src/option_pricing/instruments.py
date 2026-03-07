from dataclasses import dataclass


@dataclass(frozen=True)
class OptionContract:
    option_type: str   # "call" or "put"
    strike: float
    maturity: float    # in years
    style: str         # "european" or "american"

    def __post_init__(self) -> None:
        if self.option_type not in {"call", "put"}:
            raise ValueError("option_type must be 'call' or 'put'.")

        if self.style not in {"european", "american"}:
            raise ValueError("style must be 'european' or 'american'.")

        if self.strike <= 0:
            raise ValueError("strike must be positive.")

        if self.maturity <= 0:
            raise ValueError("maturity must be positive.")
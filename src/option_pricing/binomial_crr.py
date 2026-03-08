from __future__ import annotations

import math

from option_pricing.instruments import OptionContract
from option_pricing.market import MarketData
from option_pricing.results import PricingResult


def _validate_inputs(contract: OptionContract, market: MarketData, steps: int) -> None:
    if contract.maturity <= 0:
        raise ValueError("Maturity must be positive.")

    if contract.strike <= 0:
        raise ValueError("Strike must be positive.")

    if market.spot <= 0:
        raise ValueError("Spot must be positive.")

    if market.volatility <= 0:
        raise ValueError("Volatility must be positive.")

    if steps <= 0:
        raise ValueError("Number of steps must be positive.")


def _payoff(option_type: str, stock_price: float, strike: float) -> float:
    if option_type == "call":
        return max(stock_price - strike, 0.0)
    elif option_type == "put":
        return max(strike - stock_price, 0.0)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")


class CRREngine:
    """
    Cox-Ross-Rubinstein binomial tree pricing engine.

    Supports:
    - European call/put
    - American call/put
    - price, delta, gamma, theta
    """

    def __init__(self, steps: int) -> None:
        self.steps = steps

    def price(self, contract: OptionContract, market: MarketData) -> PricingResult:
        _validate_inputs(contract, market, self.steps)

        S0 = market.spot
        K = contract.strike
        r = market.rate
        q = market.dividend
        sigma = market.volatility
        T = contract.maturity
        N = self.steps

        dt = T / N
        u = math.exp(sigma * math.sqrt(dt))
        d = 1.0 / u
        disc = math.exp(-r * dt)

        p = (math.exp((r - q) * dt) - d) / (u - d)

        if not (0.0 < p < 1.0):
            raise ValueError(
                f"Risk-neutral probability out of bounds: p={p:.6f}. "
                "Check inputs or increase steps."
            )

        # Stock prices at maturity
        stock_tree = []
        for i in range(N + 1):
            level = []
            for j in range(i + 1):
                stock_price = S0 * (u ** j) * (d ** (i - j))
                level.append(stock_price)
            stock_tree.append(level)

        # Option values at maturity
        option_tree = []
        for i in range(N + 1):
            option_tree.append([0.0] * (i + 1))

        for j in range(N + 1):
            option_tree[N][j] = _payoff(contract.option_type, stock_tree[N][j], K)

        # Backward induction
        for i in range(N - 1, -1, -1):
            for j in range(i + 1):
                continuation = disc * (
                    p * option_tree[i + 1][j + 1] + (1.0 - p) * option_tree[i + 1][j]
                )

                if contract.style == "american":
                    exercise = _payoff(contract.option_type, stock_tree[i][j], K)
                    option_tree[i][j] = max(exercise, continuation)
                else:
                    option_tree[i][j] = continuation

        price = option_tree[0][0]

        # Delta from first step
        delta = (
            option_tree[1][1] - option_tree[1][0]
        ) / (
            stock_tree[1][1] - stock_tree[1][0]
        )

        # Gamma from second step
        delta_up = (
            option_tree[2][2] - option_tree[2][1]
        ) / (
            stock_tree[2][2] - stock_tree[2][1]
        )

        delta_down = (
            option_tree[2][1] - option_tree[2][0]
        ) / (
            stock_tree[2][1] - stock_tree[2][0]
        )

        gamma = (
            delta_up - delta_down
        ) / (
            (stock_tree[2][2] - stock_tree[2][0]) / 2.0
        )

        # Theta approximation using central node at step 2
        theta = (option_tree[2][1] - option_tree[0][0]) / (2.0 * dt)

        return PricingResult(
            price=float(price),
            delta=float(delta),
            gamma=float(gamma),
            theta=float(theta),
        )
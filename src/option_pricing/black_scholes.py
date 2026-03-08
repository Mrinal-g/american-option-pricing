from __future__ import annotations

import math

from scipy.stats import norm

from option_pricing.instruments import OptionContract
from option_pricing.market import MarketData
from option_pricing.results import PricingResult


def _validate_inputs(contract: OptionContract, market: MarketData) -> None:
    if contract.style != "european":
        raise ValueError("Black-Scholes-Merton pricing is only valid for european options.")

    if contract.maturity <= 0:
        raise ValueError("Maturity must be positive.")

    if market.spot <= 0:
        raise ValueError("Spot price must be positive.")

    if market.volatility <= 0:
        raise ValueError("Volatility must be positive.")


def d1(
    spot: float,
    strike: float,
    rate: float,
    dividend: float,
    volatility: float,
    maturity: float,
) -> float:
    return (
        math.log(spot / strike)
        + (rate - dividend + 0.5 * volatility**2) * maturity
    ) / (volatility * math.sqrt(maturity))


def d2(
    spot: float,
    strike: float,
    rate: float,
    dividend: float,
    volatility: float,
    maturity: float,
) -> float:
    return d1(spot, strike, rate, dividend, volatility, maturity) - volatility * math.sqrt(maturity)


def black_scholes_price(
    contract: OptionContract,
    market: MarketData,
) -> float:
    _validate_inputs(contract, market)

    S = market.spot
    K = contract.strike
    r = market.rate
    q = market.dividend
    sigma = market.volatility
    T = contract.maturity

    d_1 = d1(S, K, r, q, sigma, T)
    d_2 = d2(S, K, r, q, sigma, T)

    if contract.option_type == "call":
        price = (
            S * math.exp(-q * T) * norm.cdf(d_1)
            - K * math.exp(-r * T) * norm.cdf(d_2)
        )
    else:
        price = (
            K * math.exp(-r * T) * norm.cdf(-d_2)
            - S * math.exp(-q * T) * norm.cdf(-d_1)
        )

    return float(price)


def black_scholes_delta(
    contract: OptionContract,
    market: MarketData,
) -> float:
    _validate_inputs(contract, market)

    S = market.spot
    K = contract.strike
    r = market.rate
    q = market.dividend
    sigma = market.volatility
    T = contract.maturity

    d_1 = d1(S, K, r, q, sigma, T)

    if contract.option_type == "call":
        delta = math.exp(-q * T) * norm.cdf(d_1)
    else:
        delta = math.exp(-q * T) * (norm.cdf(d_1) - 1.0)

    return float(delta)


def black_scholes_gamma(
    contract: OptionContract,
    market: MarketData,
) -> float:
    _validate_inputs(contract, market)

    S = market.spot
    K = contract.strike
    r = market.rate
    q = market.dividend
    sigma = market.volatility
    T = contract.maturity

    d_1 = d1(S, K, r, q, sigma, T)

    gamma = (
        math.exp(-q * T) * norm.pdf(d_1)
    ) / (S * sigma * math.sqrt(T))

    return float(gamma)


def black_scholes_vega(
    contract: OptionContract,
    market: MarketData,
) -> float:
    _validate_inputs(contract, market)

    S = market.spot
    K = contract.strike
    r = market.rate
    q = market.dividend
    sigma = market.volatility
    T = contract.maturity

    d_1 = d1(S, K, r, q, sigma, T)

    vega = S * math.exp(-q * T) * norm.pdf(d_1) * math.sqrt(T)

    return float(vega)


def black_scholes_theta(
    contract: OptionContract,
    market: MarketData,
) -> float:
    _validate_inputs(contract, market)

    S = market.spot
    K = contract.strike
    r = market.rate
    q = market.dividend
    sigma = market.volatility
    T = contract.maturity

    d_1 = d1(S, K, r, q, sigma, T)
    d_2 = d2(S, K, r, q, sigma, T)

    first_term = -(
        S * math.exp(-q * T) * norm.pdf(d_1) * sigma
    ) / (2.0 * math.sqrt(T))

    if contract.option_type == "call":
        theta = (
            first_term
            - r * K * math.exp(-r * T) * norm.cdf(d_2)
            + q * S * math.exp(-q * T) * norm.cdf(d_1)
        )
    else:
        theta = (
            first_term
            + r * K * math.exp(-r * T) * norm.cdf(-d_2)
            - q * S * math.exp(-q * T) * norm.cdf(-d_1)
        )

    return float(theta)


def black_scholes_rho(
    contract: OptionContract,
    market: MarketData,
) -> float:
    _validate_inputs(contract, market)

    S = market.spot
    K = contract.strike
    r = market.rate
    q = market.dividend
    sigma = market.volatility
    T = contract.maturity

    d_2 = d2(S, K, r, q, sigma, T)

    if contract.option_type == "call":
        rho = K * T * math.exp(-r * T) * norm.cdf(d_2)
    else:
        rho = -K * T * math.exp(-r * T) * norm.cdf(-d_2)

    return float(rho)


class BlackScholesEngine:
    """
    Black-Scholes-Merton pricing engine for European options.
    """

    def price(
        self,
        contract: OptionContract,
        market: MarketData,
    ) -> PricingResult:
        price = black_scholes_price(contract, market)
        delta = black_scholes_delta(contract, market)
        gamma = black_scholes_gamma(contract, market)
        theta = black_scholes_theta(contract, market)
        vega = black_scholes_vega(contract, market)
        rho = black_scholes_rho(contract, market)

        return PricingResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
        )
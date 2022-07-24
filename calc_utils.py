from cmath import exp, log, sqrt
from copy import copy, deepcopy
from typing import List

import numpy as np
from pytest import mark, param

from scipy import optimize, stats
from sqlalchemy import null


class Market:
    """_summary_ class of market"""

    __convention_dict = {"EURUSD": "pips", "USDJPY": "percent", "EURJPY": "percent"}
    ccy_pair = str()

    def __init__(
        self,
        ccy_pair,
        spot,
        r_d,
        r_f,
        sigma,
        ATM_vol,
        RR25_vol,
        RR10_vol,
        BF25_vol,
        BF10_Vol,
    ) -> None:
        self.ccy_pair = ccy_pair
        self.spot = spot
        self.r_d = r_d
        self.r_f = r_f
        self.sigma = sigma
        self.ATM_vol = ATM_vol
        self.RR25_vol = RR25_vol
        self.RR10_vol = RR10_vol
        self.BF25_vol = BF25_vol
        self.BF10_Vol = BF10_Vol

    def delta_convnetion(self):

        if self.ccy_pair not in self.__convention_dict.keys():
            return null
        return self.__convention_dict.get(self.ccy_pair)


class Trade:
    def __init__(self, stirke, maturity) -> None:
        self.strike = stirke
        self.maturity = maturity


def _d1(market: Market, trade: Trade) -> float:
    a = (
        log(calc_forward(market, trade) / trade.strike)
        + 0.5 * market.sigma**2 * trade.maturity
    )
    b = market.sigma * sqrt(trade.maturity)
    return a / b


def _d2(market: Market, trade: Trade) -> float:
    a = (
        log(calc_forward(market, trade) / trade.strike)
        - 0.5 * market.sigma**2 * trade.maturity
    )
    b = market.sigma * sqrt(trade.maturity)
    return a / b


def _N(x):
    return stats.norm.cdf(x)


def calc_european_option(call_or_put: int, market, trade):
    d1 = _d1(market, trade)
    d2 = _d2(market, trade)
    if abs(call_or_put) == 1:
        return null
    return (
        call_or_put
        * exp(-market.r_d * market.maturity)
        * (
            calc_forward(market, trade) * _N(call_or_put * d1)
            - trade.strike * _N(call_or_put * d2)
        )
    )


def calc_forward(market: Market, trade: Trade):
    return market.spot * exp((market.r_d - market.r_f) * trade.maturity)


def calc_ATM_strike(market: Market, trade: Trade):
    fwd = calc_forward(market, trade)
    multiple_factor = exp(0.5 * (market.sigma**2) * trade.maturity)
    if market.delta_convnetion() is "pips":
        return fwd * multiple_factor
    if market.delta_convnetion() is "percent":
        return fwd / multiple_factor
    return null


def calc_spot_delta_pips(call_or_put: int, market: Market, trade: Trade):
    d1 = _d1(market, trade)
    return call_or_put * exp(-market.r_f * trade.maturity) * _N(call_or_put * d1)


def calc_spot_delta_pct(call_or_put: int, market: Market, trade: Trade):
    v_pct_f = calc_european_option(call_or_put, market, trade) / market.spot
    return calc_spot_delta_pips(call_or_put, market, trade) - v_pct_f


def calc_MS_stirke(call_or_put, market: Market, trade: Trade, target_vol_MS, delta):
    def f(target_strike):
        """return delta(strike)"""
        market_copy = deepcopy(market)
        market_copy.sigma = market.ATM_vol + target_vol_MS
        trade_copy = deepcopy(trade)
        trade_copy.strike = target_strike
        if market.delta_convnetion() is "pips":
            return calc_spot_delta_pips(call_or_put, market_copy, trade_copy) - delta
        if market.delta_convnetion() is "percent":
            return calc_spot_delta_pct(call_or_put, market_copy, trade_copy) - delta
        return null

    root = optimize.brentq(f, 1e-4, market.spot * 10)
    return root


def smile_curve(x: float, market: Market, trade: Trade, params: List):
    fwd = calc_forward(market, trade)
    x = log(fwd / trade.strike)
    delta_0 = exp(params[0])
    delta_x = _N(x / (delta_0 * sqrt(trade.maturity)))
    f_x = params[0] + params[1] * delta_x + params[2] * delta_x**2
    return exp(f_x)


def calc_sigma_delta(market: Market, delta10_or_25):
    left = [[1, -1], [0.5, 0.5]]
    if delta10_or_25 is "10":
        right = [market.RR10_vol, market.BF10_Vol + market.ATM_vol]
    else:
        right = [market.RR25_vol, market.BF25_vol + market.ATM_vol]
    return np.linalg.solve(left, right)

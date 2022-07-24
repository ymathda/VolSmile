import warnings

from calc_utils import *

warnings.simplefilter("ignore")

market_EURUSD = Market(
    "EURUSD", 1.3465, 0.0294, 0.0346, 0.1825, 0.1825, 0.00950, 0, 0, 0
)
trade_EURUSD = Trade(0, 1.0)


def test_convention():
    expected = "pips"
    actual = market_EURUSD.delta_convnetion()
    assert expected == actual


def test_calc_forward():
    """1Y EUR USD"""
    exptected = 1.3395
    sigma = 0.1825
    r_d = 0.0294
    r_f = 0.0346
    maturity = 1.0
    spot = 1.3465
    actual = calc_forward(market_EURUSD, trade_EURUSD)
    actual = np.round(actual, 4)
    assert exptected == actual


def test_calc_ATM_strike():
    exptected = 1.3620
    actual = calc_ATM_strike(market_EURUSD, trade_EURUSD)
    actual = np.round(actual, 4)
    assert exptected == actual


def test_calc_MS_strike():
    expected_call = 1.5449
    expected_put = 1.2050

    call_or_put = 1
    delta = 0.25
    actual_call = calc_MS_stirke(
        call_or_put, market_EURUSD, trade_EURUSD, market_EURUSD.RR25_vol, delta
    )
    assert expected_call == np.round(actual_call, 4)

    call_or_put = -1
    delta = -0.25
    actual_put = calc_MS_stirke(
        call_or_put, market_EURUSD, trade_EURUSD, market_EURUSD.RR25_vol, delta
    )
    assert expected_put == np.round(actual_put, 4)


def test_calc_sigma_delta():
    mkt = Market("USDJPY", 0, 0, 0, 0, 0.1825, -0.0060, 0, 0.0095, 0)
    sigma_c, sigma_p = calc_sigma_delta(market=mkt, delta10_or_25="25")
    expected = [0.1890, 0.1950]
    assert sigma_c == expected[0]
    assert sigma_p == expected[1]

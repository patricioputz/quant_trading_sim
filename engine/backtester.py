import pandas as pd

from data.loader import load_price_data, load_pair_data
from engine.metrics import calculate_metrics
from strategies import moving_average, pairs_trading


def run_momentum(
    ticker: str = "SPY",
    start: str = "2018-01-01",
    end: str = "2026-01-01",
    short_window: int = 20,
    long_window: int = 100,
) -> dict:
    data = load_price_data(ticker, start, end)
    close = data["Close"].squeeze()
    buy_hold_return = close.pct_change()

    strategy_return = moving_average.run(data, short_window, long_window)

    return {
        "strategy": calculate_metrics(strategy_return),
        "buy_hold": calculate_metrics(buy_hold_return),
        "strategy_name": f"MA({short_window}/{long_window})",
        "ticker": ticker,
    }


def run_pairs(
    ticker_a: str = "SPY",
    ticker_b: str = "QQQ",
    start: str = "2018-01-01",
    end: str = "2026-01-01",
    zscore_window: int = 60,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.0,
) -> dict:
    price_a, price_b = load_pair_data(ticker_a, ticker_b, start, end)

    strategy_return = pairs_trading.run(
        price_a, price_b, zscore_window, entry_threshold, exit_threshold
    )

    # Baseline: buy-and-hold ticker_a
    buy_hold_return = price_a.pct_change()

    return {
        "strategy": calculate_metrics(strategy_return),
        "buy_hold": calculate_metrics(buy_hold_return),
        "strategy_name": f"Pairs({ticker_a}/{ticker_b})",
        "ticker": f"{ticker_a}/{ticker_b}",
    }

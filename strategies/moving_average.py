import pandas as pd


def run(data: pd.DataFrame, short_window: int = 20, long_window: int = 100) -> pd.Series:
    """MA crossover: long SPY when short MA > long MA, else cash."""
    df = data.copy()
    close = df["Close"].squeeze()
    daily_return = close.pct_change()
    short_ma = close.rolling(short_window).mean()
    long_ma = close.rolling(long_window).mean()

    signal = (short_ma > long_ma).astype(int)
    strategy_return = signal.shift(1) * daily_return
    strategy_return.name = "strategy_return"
    return strategy_return

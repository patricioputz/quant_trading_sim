import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.tsa.stattools import coint


def run(
    price_a: pd.Series,
    price_b: pd.Series,
    zscore_window: int = 60,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.0,
) -> pd.Series:
    """
    Engle-Granger cointegration pairs strategy.

    Computes spread = price_A - hedge_ratio * price_B via OLS.
    Enters long spread when z-score < -entry_threshold,
    short spread when z-score > entry_threshold,
    exits when z-score crosses exit_threshold.

    Returns a daily return series with no lookahead bias.
    """
    price_a = price_a.squeeze()
    price_b = price_b.squeeze()

    score, pvalue, _ = coint(price_a, price_b)
    if pvalue > 0.05:
        print(
            f"  Warning: pair not cointegrated at 5% level (p={pvalue:.3f}). "
            "Proceeding anyway."
        )

    # Estimate hedge ratio over full in-sample period (fixed ratio)
    model = OLS(price_a, add_constant(price_b)).fit()
    hedge_ratio = model.params.iloc[1]

    spread = price_a - hedge_ratio * price_b

    # Rolling z-score — no lookahead: use expanding mean/std until window is full
    rolling_mean = spread.rolling(zscore_window).mean()
    rolling_std = spread.rolling(zscore_window).std()
    zscore = (spread - rolling_mean) / rolling_std

    # Generate position: +1 = long spread, -1 = short spread, 0 = flat
    # Signal is determined from yesterday's z-score to avoid lookahead bias
    position = pd.Series(0.0, index=zscore.index)
    pos = 0.0
    prev_z = zscore.shift(1)

    for i in range(1, len(prev_z)):
        z = prev_z.iloc[i]
        if np.isnan(z):
            position.iloc[i] = 0.0
            continue
        if pos == 0.0:
            if z < -entry_threshold:
                pos = 1.0
            elif z > entry_threshold:
                pos = -1.0
        elif pos == 1.0:
            if z >= exit_threshold:
                pos = 0.0
        elif pos == -1.0:
            if z <= -exit_threshold:
                pos = 0.0
        position.iloc[i] = pos

    # P&L: daily change in spread value, normalised by initial spread level
    spread_return = spread.diff() / spread.abs().shift(1)
    strategy_return = position * spread_return
    strategy_return.name = "strategy_return"
    return strategy_return

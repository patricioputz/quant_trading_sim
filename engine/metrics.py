import numpy as np
import pandas as pd

TRADING_DAYS = 252


def calculate_metrics(returns: pd.Series) -> dict:
    returns = returns.dropna()
    equity_curve = (1 + returns).cumprod()

    total_return = equity_curve.iloc[-1] - 1

    mean_r = returns.mean()
    std_r = returns.std()
    sharpe = (mean_r / std_r * np.sqrt(TRADING_DAYS)) if std_r > 0 else np.nan

    downside = returns[returns < 0]
    downside_std = downside.std()
    sortino = (mean_r / downside_std * np.sqrt(TRADING_DAYS)) if downside_std > 0 else np.nan

    n_years = len(returns) / TRADING_DAYS
    cagr = (equity_curve.iloc[-1] ** (1 / n_years) - 1) if n_years > 0 else np.nan

    peak = equity_curve.cummax()
    drawdown = equity_curve / peak - 1
    max_drawdown = drawdown.min()

    calmar = (cagr / abs(max_drawdown)) if max_drawdown < 0 else np.nan

    win_rate = (returns > 0).sum() / len(returns)

    return {
        "total_return": total_return,
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "equity_curve": equity_curve,
    }

import numpy as np
import pandas as pd
import yfinance as yf

# ============================================================
# 1. SETTINGS
# ============================================================

TICKER = "SPY"
START_DATE = "2018-01-01"
END_DATE = "2026-01-01"

SHORT_WINDOW = 20
LONG_WINDOW = 100

TRADING_DAYS = 252

# ============================================================
# 2. DATA LOADING
# ============================================================

def load_price_data(ticker, start_date, end_date):
    """
    Downloads real price data from Yahoo Finance. 
    Returns it to a Panda database.
    """
    data = yf.download(
        TICKER,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False
    )

    return data

# ============================================================
# 3. INDICATORS
# ============================================================

def add_indicators(data):
    """
    Adds daily returns and moving averages.
    """

    data = data.copy()

    # Calculate daily returns
    data["daily_return"] = data["Close"].pct_change()

    # Calculate moving avgs
    data["short_ma"] = data["Close"].rolling(SHORT_WINDOW).mean()
    data["long_ma"] = data["Close"].rolling(LONG_WINDOW).mean()

    return data

# ============================================================
# 4. STRATEGY
# ============================================================
def run_moving_average_strategy(data):  
    """
    Momentum strategy:
    If short moving average > long moving average, hold SPY.
    Otherwise, stay in cash.
    """

    data = data.copy()

    data["signal"] = 0
    data.loc[data["short_ma"] > data["long_ma"], "signal"] = 1

    #use yesterday's signal for today's return to avoid lookahead bias
    data["strategy_return"] = data["signal"].shift(1) * data["daily_return"]

    return data

def add_buy_and_hold_baseline(data):
    """
    Buy-and-hold baseline:
    Own SPY every day.
    """

    data = data.copy()
    data["buy_hold_return"] = data["daily_return"]

    return data

# ============================================================
# 5. METRICS
# ============================================================

def calculate_metrics(returns):
    """
    Takes a return series and calculates:
    total return, Sharpe ratio, max drawdown, and equity curve.
    """

    returns = returns.dropna()

    equity_curve = (1 + returns).cumprod()

    total_return = equity_curve.iloc[-1] - 1

    sharpe = (returns.mean() / returns.std() * np.sqrt(TRADING_DAYS))

    peak = equity_curve.cummax()
    drawdown = equity_curve / peak - 1
    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "equity_curve": equity_curve
    }

# ============================================================
# 6. PRINTING
# ============================================================

def print_results(strategy_metrics, buy_hold_metrics):
    """
    Prints results in a clean table.
    """
     
    print("\nREAL BACKTEST SUMMARY")
    print("=" * 90)

    header = (
        f"{'Strategy':<20}"
        f"{'Total Return':>15}"
        f"{'Sharpe':>12}"
        f"{'Max Drawdown':>15}"
    )

    print(header)
    print("-" * 90)

    strategy_row = (
        f"{'Moving Average':<20}"
        f"{round(strategy_metrics['total_return'] * 100, 2):>14}%"
        f"{round(strategy_metrics['sharpe'], 2):>12}"
        f"{round(strategy_metrics['max_drawdown'] * 100, 2):>14}%"
    )

    buy_hold_row = (
        f"{'Buy and Hold':<20}"
        f"{round(buy_hold_metrics['total_return'] * 100, 2):>14}%"
        f"{round(buy_hold_metrics['sharpe'], 2):>12}"
        f"{round(buy_hold_metrics['max_drawdown'] * 100, 2):>14}%"
    )

    print(strategy_row)
    print(buy_hold_row)
    print("=" * 90)

# ============================================================
# 7. RUN PROGRAM (MAIN)
# ============================================================

data = load_price_data(TICKER, START_DATE, END_DATE)

data = add_indicators(data)

data = run_moving_average_strategy(data)

data = add_buy_and_hold_baseline(data)

strategy_metrics = calculate_metrics(data["strategy_return"])
buy_hold_metrics = calculate_metrics(data["buy_hold_return"])

print_results(strategy_metrics, buy_hold_metrics)

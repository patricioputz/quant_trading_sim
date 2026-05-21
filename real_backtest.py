import numpy as np
import pandas as pd
import yfinance as yf

data = yf.download(
    "SPY",
    start="2018-01-01",
    end="2026-01-01",
    auto_adjust=True,
    progress=False
)

# Calculate daily returns
data["daily_return"] = data["Close"].pct_change()

# Calculate moving avgs
data["short_ma"] = data["Close"].rolling(20).mean()
data["long_ma"] = data["Close"].rolling(100).mean()

print("\nMOVING AVERAGES")
print(data[["Close", "short_ma", "long_ma"]].head(110))

#SIGNAL COLUMN
# 1 = INVEST SPY
# 0 = STAY OUT / CASH

data["signal"] = 0
data.loc[data["short_ma"] > data["long_ma"], "signal"] = 1

print("\nSIGNAL")
print(data[["Close", "short_ma", "long_ma", "signal"]].tail(30))

# Strategy return
#yesterday's signal for today's return
data["strategy_return"] = data["signal"].shift(1) * data["daily_return"]
print(data["strategy_return"])

print("\nSTRATEGY RETURNS")
print(data[["Close", "daily_return", "signal", "strategy_return"]].tail(30))

#Buy and Hold Return
#Baseline of owning SPY every day
data["buy_hold_return"] = data["daily_return"]

# Remove rows with missing values
data = data.dropna()

# EQUITY Curves
#Shows $1 Growth over time
data["strategy_equity"] = (1 + data["strategy_return"]).cumprod()
data["buy_hold_equity"] = (1 + data["buy_hold_return"]).cumprod()

#TOTAL RETURNS
strategy_total_return = data["strategy_equity"].iloc[-1] - 1
buy_hold_total_return = data["buy_hold_equity"].iloc[-1] - 1

print("\nTOTAL RETURNS")
print("Moving Average Strategy:", round(strategy_total_return * 100, 2), "%")
print("Buy and Hold:", round(buy_hold_total_return * 100, 2), "%")

#Sharpe and DrawDown

strategy_sharpe = (data["strategy_return"].mean() / data["strategy_return"].std()) * np.sqrt(252)
buy_hold_sharpe = (data["buy_hold_return"].mean() / data["buy_hold_return"].std()) * np.sqrt(252)

data["strategy_peak"] = data["strategy_equity"].cummax()
data["buy_hold_peak"] = data["buy_hold_equity"].cummax()

data["strategy_drawdown"] = data["strategy_equity"] / data["strategy_peak"] - 1
data["buy_hold_drawdown"] = data["buy_hold_equity"] / data["buy_hold_peak"] - 1

strategy_max_drawdown = data["strategy_drawdown"].min()
buy_hold_max_drawdown = data["buy_hold_drawdown"].min()

print("\nRISK METRICS")
print("Moving Average Sharpe:", round(strategy_sharpe, 2))
print("Buy ad Hold Sharpe:", round(buy_hold_sharpe, 2))
print("Moving Average Max Drawdown:", round(strategy_max_drawdown * 100, 2), "%")
print("Buy and Hold Max Drawdown:", round(buy_hold_max_drawdown * 100, 2), "%")
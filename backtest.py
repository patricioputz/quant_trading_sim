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


data["daily_return"] = data["Close"].pct_change()

data["short_ma"] = data["Close"].rolling(20).mean()
data["long_ma"] = data["Close"].rolling(100).mean()

print("\nMOVING AVERAGES")
print(data[["Close", "short_ma", "long_ma"]].head(110))
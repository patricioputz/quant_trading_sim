# QuantLab — Systematic Strategy Backtester

A quantitative trading research platform built in Python. Backtest systematic strategies on real market data, analyse performance with institutional-grade metrics, and simulate live paper trading — all from an interactive web dashboard.

**Live app:** [quanttradingsim-production.up.railway.app](https://quanttradingsim-production.up.railway.app)

---

## Overview

QuantLab provides a full research loop: load historical price data, run a strategy backtest, inspect seven performance metrics, and then switch to paper trading mode to track how the same strategy would perform starting from any date through today. Everything is available through a Streamlit dashboard or the command-line interface.

---

## Strategies

### MA Crossover (Momentum)
Trend-following strategy based on a dual moving-average crossover. Holds the asset when the short-term MA is above the long-term MA, otherwise stays in cash. Window lengths are configurable.

- Signal: `short_MA > long_MA` → long; otherwise flat
- No leverage, no short selling
- Parameters: `short_window` (default 20), `long_window` (default 100)

### Pairs Trading (Statistical Arbitrage)
Mean-reversion strategy built on the Engle-Granger cointegration test. Estimates a hedge ratio via OLS, constructs a spread, and trades a rolling z-score of that spread.

- Tests for cointegration at 5% significance (proceeds with a warning if not met)
- Entry: z-score crosses ±2.0 (configurable); exit: z-score reverts to 0.0
- Fixed hedge ratio estimated over the full in-sample period
- No lookahead bias — positions are determined from the prior day's z-score
- Parameters: `zscore_window` (default 60), `entry_threshold` (default 2.0), `exit_threshold` (default 0.0)

---

## Performance Metrics

| Metric | Formula |
|---|---|
| Total Return | `equity[-1] / equity[0] − 1` |
| CAGR | `equity[-1]^(1/years) − 1` |
| Sharpe Ratio | `mean(r) / std(r) × √252` |
| Sortino Ratio | `mean(r) / std(r<0) × √252` |
| Calmar Ratio | `CAGR / |max drawdown|` |
| Max Drawdown | `min(equity / cummax(equity) − 1)` |
| Win Rate | `count(r > 0) / count(r)` |

---

## Dashboard Features

- **Backtest Analysis tab** — equity curve + drawdown panel, monthly returns heatmap, metric cards for all 7 metrics
- **Paper Portfolio tab** — live equity curve from a user-defined start date to today, current signal badge, full trade log
- **Sidebar controls** — strategy selector, ticker inputs, date range, strategy parameters, paper capital

---

## Quickstart

### Prerequisites

```bash
pip install -r requirements.txt
```

Dependencies: `numpy`, `pandas`, `yfinance`, `statsmodels`, `matplotlib`, `streamlit`, `plotly`

### Interactive Dashboard

```bash
streamlit run app.py
```

Open `http://localhost:8501`, then use the sidebar to configure strategy, tickers, and date range.

### Command-Line Backtest

```bash
# Momentum strategy
python3 main.py --strategy momentum --ticker SPY --start 2018-01-01 --end 2026-01-01

# Pairs trading
python3 main.py --strategy pairs --ticker-a SPY --ticker-b QQQ --start 2018-01-01 --end 2026-01-01
```

CLI output includes a summary table and saves an equity curve PNG.

---

## Project Structure

```
trading-bot/
├── app.py                   # Streamlit dashboard (main UI)
├── main.py                  # CLI entry point (argparse)
├── requirements.txt
├── Procfile                 # Railway deployment config
├── .streamlit/config.toml   # Dark theme + headless settings
├── data/
│   └── loader.py            # yfinance: load_price_data(), load_pair_data()
├── engine/
│   ├── backtester.py        # Orchestration: run_momentum(), run_pairs()
│   ├── metrics.py           # calculate_metrics() → 7 metrics dict
│   └── paper_trader.py      # run_momentum_paper(), run_pairs_paper()
├── strategies/
│   ├── moving_average.py    # MA crossover — returns daily return series
│   └── pairs_trading.py     # Engle-Granger cointegration strategy
└── reporting/
    └── report.py            # CLI: print_summary(), save_equity_chart() PNG
```

---

## Deployment

### Railway (live)

Push to GitHub → Railway auto-detects `Procfile` and deploys.

```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

The `--server.address=0.0.0.0` flag is required; without it Streamlit only binds to localhost and Railway cannot route traffic to it.

### Streamlit Cloud (free alternative)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Point to `app.py` and deploy

---

## Extending the Platform

To add a new strategy:

1. `strategies/my_strategy.py` — implement `run(...) -> pd.Series` of daily returns
2. `engine/backtester.py` — add `run_my_strategy()` orchestration function
3. `engine/paper_trader.py` — add `run_my_strategy_paper()` for live simulation
4. `main.py` — wire `--strategy my_strategy` in argparse
5. `app.py` — add the option to the sidebar selectbox and hook into the run/paper blocks

---

## Disclaimer

For research and educational purposes only. Past backtest performance does not guarantee future results. Nothing here constitutes financial advice.

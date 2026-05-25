# QuantLab — Systematic Strategy Backtester

A Python-based quantitative research platform for backtesting systematic trading strategies on real market data. Includes an interactive web dashboard and paper trading simulator.

---

## Features

- **MA Crossover** — momentum strategy using configurable short/long moving averages
- **Pairs Trading** — cointegration-based stat-arb using Engle-Granger test and OLS spread
- **7 performance metrics** — Total Return, CAGR, Sharpe, Sortino, Calmar, Max Drawdown, Win Rate
- **Interactive dashboard** — Plotly charts, monthly returns heatmap, equity + drawdown panels
- **Paper portfolio** — simulates live trading from any start date to today, tracks every trade

---

## Quickstart

```bash
pip install -r requirements.txt
```

### Interactive Dashboard (Streamlit)

```bash
streamlit run app.py
```

Open `http://localhost:8501` — use the sidebar to configure strategy, tickers, and date range.

### Command-Line Backtest

```bash
# Momentum strategy
python3 main.py --strategy momentum --ticker SPY --start 2018-01-01 --end 2026-01-01

# Pairs trading
python3 main.py --strategy pairs --ticker-a SPY --ticker-b QQQ --start 2018-01-01 --end 2026-01-01
```

---

## Project Structure

```
trading-bot/
├── app.py                   # Streamlit dashboard
├── main.py                  # CLI entry point
├── requirements.txt
├── data/
│   └── loader.py            # yfinance data fetching
├── engine/
│   ├── backtester.py        # Orchestration layer
│   ├── metrics.py           # Performance metric calculations
│   └── paper_trader.py      # Paper trading simulator
├── strategies/
│   ├── moving_average.py    # MA crossover strategy
│   └── pairs_trading.py     # Cointegration pairs strategy
└── reporting/
    └── report.py            # CLI summary table + equity curve PNG
```

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select your repo, set **Main file** to `app.py`
4. Deploy — free, no server required

---

## Metrics

| Metric | Description |
|---|---|
| Total Return | Cumulative return over the full period |
| CAGR | Compound Annual Growth Rate |
| Sharpe Ratio | Annualised return / annualised volatility |
| Sortino Ratio | Like Sharpe, but only penalises downside volatility |
| Calmar Ratio | CAGR / absolute max drawdown |
| Max Drawdown | Largest peak-to-trough equity decline |
| Win Rate | Fraction of trading days with positive return |

---

## Disclaimer

For research and educational purposes only. Not financial advice.

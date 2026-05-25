# QuantLab — Developer Guide

## Git Workflow

After every meaningful set of changes in a conversation — not every single file edit, but at natural checkpoints (feature complete, bug fixed, refactor done) — commit and push to GitHub:

```bash
git add <changed files>
git commit -m "short description of what changed"
git push origin main
```

Don't let multiple unrelated changes pile up in one commit. One logical change = one commit.

---

## Running the App

```bash
# Interactive dashboard
streamlit run app.py

# CLI backtest
python3 main.py --strategy momentum --ticker SPY --start 2018-01-01 --end 2026-01-01
python3 main.py --strategy pairs --ticker-a SPY --ticker-b QQQ --start 2018-01-01 --end 2026-01-01
```

## Project Structure

```
trading-bot/
├── app.py                   # Streamlit dashboard (main UI)
├── main.py                  # CLI entry point (argparse)
├── real_backtest.py         # Original monolithic script (reference)
├── requirements.txt
├── .streamlit/config.toml   # Dark theme settings
├── data/
│   └── loader.py            # yfinance: load_price_data(), load_pair_data()
├── engine/
│   ├── backtester.py        # run_momentum(), run_pairs()
│   ├── metrics.py           # calculate_metrics() → all 7 metrics
│   └── paper_trader.py      # run_momentum_paper(), run_pairs_paper()
├── strategies/
│   ├── moving_average.py    # MA crossover, returns daily return series
│   └── pairs_trading.py     # Engle-Granger + OLS spread + z-score signal
└── reporting/
    └── report.py            # CLI: print_summary(), save_equity_chart()
```

## Adding a New Strategy

1. Add `strategies/my_strategy.py` with a `run(data, **params) -> pd.Series` function
2. Add a `run_my_strategy()` function in `engine/backtester.py`
3. Wire `--strategy my_strategy` in `main.py`
4. Add a paper trader variant in `engine/paper_trader.py`
5. Add the option to the sidebar in `app.py`

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Visit share.streamlit.io → New app
3. Point to `app.py`, deploy

## Metrics Reference

| Key | Formula |
|---|---|
| `total_return` | `equity[-1] / equity[0] - 1` |
| `cagr` | `equity[-1]^(1/years) - 1` |
| `sharpe` | `mean(r) / std(r) * sqrt(252)` |
| `sortino` | `mean(r) / std(r<0) * sqrt(252)` |
| `calmar` | `cagr / abs(max_drawdown)` |
| `max_drawdown` | `min(equity / cummax(equity) - 1)` |
| `win_rate` | `count(r > 0) / count(r)` |

## Dependencies

```
numpy  pandas  yfinance  statsmodels  matplotlib  streamlit  plotly
```

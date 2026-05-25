from datetime import datetime

import numpy as np
import pandas as pd

from data.loader import load_price_data, load_pair_data


def run_momentum_paper(
    ticker: str = "SPY",
    short_window: int = 20,
    long_window: int = 100,
    initial_capital: float = 100_000,
    start: str = "2020-01-01",
) -> dict:
    end = datetime.today().strftime("%Y-%m-%d")
    data = load_price_data(ticker, start, end)
    close = data["Close"].squeeze()

    short_ma = close.rolling(short_window).mean()
    long_ma  = close.rolling(long_window).mean()
    signal   = (short_ma > long_ma).astype(float)

    cash   = float(initial_capital)
    shares = 0.0
    trades_raw = []
    port_values = []
    prev_sig = 0.0

    for i in range(len(close)):
        date_idx = close.index[i]
        price    = float(close.iloc[i])
        # use yesterday's signal — no lookahead
        sig = float(signal.iloc[i - 1]) if i > 0 and not np.isnan(signal.iloc[i - 1]) else 0.0

        if sig == 1.0 and prev_sig < 1.0 and cash > 0:
            shares    = cash / price
            entry_val = cash
            cash      = 0.0
            trades_raw.append({
                "date": date_idx, "action": "BUY",
                "price": price, "shares": shares,
                "value": entry_val, "pnl": None,
            })
        elif sig < 1.0 and prev_sig == 1.0 and shares > 0:
            proceeds = shares * price
            pnl      = proceeds - trades_raw[-1]["value"]
            trades_raw.append({
                "date": date_idx, "action": "SELL",
                "price": price, "shares": shares,
                "value": proceeds, "pnl": pnl,
            })
            cash   = proceeds
            shares = 0.0

        port_values.append((date_idx, cash + shares * price))
        prev_sig = sig

    dates, vals = zip(*port_values)
    equity_curve = pd.Series(list(vals), index=list(dates), name="value")

    df_raw = pd.DataFrame(trades_raw)
    if not df_raw.empty:
        trades_display = pd.DataFrame({
            "Date":        df_raw["date"].dt.date,
            "Action":      df_raw["action"],
            "Price":       df_raw["price"].map("${:,.2f}".format),
            "Shares":      df_raw["shares"].map("{:.3f}".format),
            "Trade Value": df_raw["value"].map("${:,.0f}".format),
            "P&L":         df_raw["pnl"].map(
                lambda x: f"${x:+,.0f}" if pd.notna(x) else "—"
            ),
        })
    else:
        trades_display = pd.DataFrame()

    current_value = float(equity_curve.iloc[-1])
    return {
        "equity_curve":     equity_curve,
        "trades":           trades_display,
        "current_position": "IN MARKET" if shares > 0 else "CASH",
        "current_value":    current_value,
        "total_return":     current_value / initial_capital - 1,
        "pnl_dollars":      current_value - initial_capital,
        "cash":             cash,
        "shares":           shares,
        "current_price":    float(close.iloc[-1]),
        "ticker":           ticker,
        "last_updated":     str(close.index[-1].date()),
        "initial_capital":  initial_capital,
    }


def run_pairs_paper(
    ticker_a: str = "SPY",
    ticker_b: str = "QQQ",
    zscore_window: int = 60,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.0,
    initial_capital: float = 100_000,
    start: str = "2020-01-01",
) -> dict:
    import warnings
    from statsmodels.regression.linear_model import OLS
    from statsmodels.tools import add_constant
    from strategies.pairs_trading import run as pairs_run

    end = datetime.today().strftime("%Y-%m-%d")
    price_a, price_b = load_pair_data(ticker_a, ticker_b, start, end)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        strategy_return = pairs_run(
            price_a, price_b, zscore_window, entry_threshold, exit_threshold
        )

    equity_curve = initial_capital * (1 + strategy_return.fillna(0)).cumprod()

    # derive current position from replaying the z-score signal
    model        = OLS(price_a, add_constant(price_b)).fit()
    hedge_ratio  = model.params.iloc[1]
    spread       = price_a - hedge_ratio * price_b
    zscore       = (spread - spread.rolling(zscore_window).mean()) / spread.rolling(zscore_window).std()

    pos = 0.0
    for z in zscore.shift(1).values:
        if np.isnan(z):
            continue
        if pos == 0.0:
            if z < -entry_threshold:  pos =  1.0
            elif z > entry_threshold: pos = -1.0
        elif pos == 1.0:
            if z >= exit_threshold:   pos = 0.0
        elif pos == -1.0:
            if z <= -exit_threshold:  pos = 0.0

    if   pos ==  1.0: position_label = "LONG SPREAD"
    elif pos == -1.0: position_label = "SHORT SPREAD"
    else:             position_label = "FLAT"

    current_value = float(equity_curve.iloc[-1])
    return {
        "equity_curve":     equity_curve,
        "trades":           pd.DataFrame(),
        "current_position": position_label,
        "current_value":    current_value,
        "total_return":     current_value / initial_capital - 1,
        "pnl_dollars":      current_value - initial_capital,
        "ticker":           f"{ticker_a} / {ticker_b}",
        "last_updated":     str(equity_curve.index[-1].date()),
        "initial_capital":  initial_capital,
    }

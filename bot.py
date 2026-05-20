import numpy as np

NUM_DAYS = 1_000_000
THRESHOLDS = [0, 2, 5, 10, 15, 20]
SIGNAL_NOISE = 10
MIN_VALUE = 80
MAX_VALUE = 120

def calculate_max_drawdown(equity_curve):
    if len(equity_curve) == 0:
        return 0
    
    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = equity_curve - peaks

    return drawdowns.min()

def calculate_sharpe_ratio(trade_profits):
    if len(trade_profits) == 0:
        return 0
    
    average_profit = trade_profits.mean()
    profit_std = trade_profits.std()

    if profit_std == 0:
        return 0
    
    sharpe_ratio = average_profit / profit_std
    return sharpe_ratio

def run_simulation(threshold, num_days = NUM_DAYS):
    #1 Generate Market Data
    true_values = np.random.randint(MIN_VALUE, MAX_VALUE + 1, size=num_days)
    signals = true_values + np.random.normal(0, SIGNAL_NOISE, size=num_days)
    market_prices = np.random.randint(MIN_VALUE, MAX_VALUE + 1, size=num_days)

    #2 Calculate Edge
    edges = signals - market_prices

    #3 Decide which days we execute trades
    trade_mask = edges > threshold

    #4 Calculate profits only on the days we are making trades
    trade_profits = true_values[trade_mask] - market_prices[trade_mask]

    #5 Core metrics

    trades = len(trade_profits)
    cash = trade_profits.sum()

    if trades > 0:
        avg_profit_per_trade = cash / trades
        wins = np.sum(trade_profits > 0)
        losses = np.sum(trade_profits < 0)
        win_rate = wins / trades
        equity_curve = np.cumsum(trade_profits)
    else:
        avg_profit_per_trade = 0
        wins = 0
        losses = 0
        win_rate = 0
        equity_curve = 0

    #6 Win/Loss Metrics
    winning_trades = trade_profits[trade_profits > 0]
    losing_trades = trade_profits[trade_profits < 0]

    if len(winning_trades) > 0:
        avg_win = winning_trades.mean()
        total_winning_profit = winning_trades.sum()
    else:
        avg_win = 0
        total_winning_profit = 0

    if len(losing_trades) > 0:
        avg_loss = losing_trades.mean()
        total_losing_profit = losing_trades.sum()
    else:
        avg_loss = 0
        total_losing_profit = 0
    
    if total_losing_profit != 0:
        profit_factor = total_winning_profit / abs(total_losing_profit)
    else:
        profit_factor = 0

    max_drawdown = calculate_max_drawdown(equity_curve)
    sharpe_ratio = calculate_sharpe_ratio(trade_profits)

    return {
        "threshold": threshold,
        "cash": cash,
        "trades": trades,
        "average_profit_per_trade": avg_profit_per_trade,
        "win_rate": win_rate,
        "wins": wins,
        "losses": losses,
        "average_win": avg_win,
        "average_loss": avg_loss,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "equity_curve": equity_curve
    }

thresholds = [0, 2, 5, 10, 15, 20]
results = []

for threshold in thresholds:
    experiment= run_simulation(threshold, num_days = NUM_DAYS)
    results.append(experiment)

best_by_profit = max(results, key=lambda x: x["cash"])
best_by_sharpe = max(results, key=lambda x: x["sharpe_ratio"])

for experiment in results:
    print("Threshold:", experiment["threshold"])
    print("Total profit:", round(experiment["cash"], 2))
    print("Trades:", experiment["trades"])
    print("Average profit per trade:", round(experiment["average_profit_per_trade"], 2))
    print("Win rate:", round(experiment["win_rate"] * 100, 2), "%")
    print("Average win:", round(experiment["average_win"], 2))
    print("Average loss:", round(experiment["average_loss"], 2))
    print("Profit factor:", round(experiment["profit_factor"], 2))
    print("Max drawdown:", round(experiment["max_drawdown"], 2))
    print("Sharpe ratio:", round(experiment["sharpe_ratio"], 2))
    print("Final equity:", round(experiment["cash"], 2))
    print("----------------------")


print("Best threshold by profit:", best_by_profit["threshold"])
print("Best total profit:", round(best_by_profit["cash"], 2))

print("Best threshold by Sharpe:", best_by_sharpe["threshold"])
print("Best Sharpe ratio:", round(best_by_sharpe["sharpe_ratio"], 2))


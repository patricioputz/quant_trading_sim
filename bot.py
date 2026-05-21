import numpy as np

# ======================
# SETTINGS
# ======================

NUM_DAYS = 1_000_000
THRESHOLDS = [0, 2, 5, 10, 15, 20]
SIGNAL_NOISE = 10
MIN_VALUE = 80
MAX_VALUE = 120

TRANSACTION_COST_RATE = 0.0001   # 0.01%
SLIPPAGE_RATE = 0.0005           # 0.05%

# ======================
# METRICS
# ======================

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

def calculate_metrics(trade_profits):
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
        equity_curve = np.array([])

    #Win/Loss Metrics
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

# ======================
# COSTS
# ======================

def apply_trading_costs(trade_profits, traded_prices):
    total_cost_rate = TRANSACTION_COST_RATE + SLIPPAGE_RATE
    costs = traded_prices * total_cost_rate
    return trade_profits - costs

# ======================
# Market Simulation
# ======================

def generate_market_data(num_days):
    true_values = np.random.randint(MIN_VALUE, MAX_VALUE + 1, size=num_days)
    signals = true_values + np.random.normal(0, SIGNAL_NOISE, size=num_days)
    market_prices = np.random.randint(MIN_VALUE, MAX_VALUE + 1, size=num_days)

    return true_values, signals, market_prices

# ======================
# Strategies
# ======================

def run_signal_strategy(true_values, signals, market_prices, threshold):
    #Calculate Edge
    edges = signals - market_prices

    #Decide which days we execute trades
    trade_mask = edges > threshold

    #Calculate profits on traded days
    trade_profits = true_values[trade_mask] - market_prices[trade_mask]
    trade_profits = apply_trading_costs(
        trade_profits=trade_profits,
        traded_prices=market_prices[trade_mask]
    )

    metrics = calculate_metrics(trade_profits)
    metrics["strategy"] = "signal"
    metrics["threshold"] = threshold

    return metrics

def run_random_strategy(true_values, market_prices, trade_probability):
    random_numbers = np.random.random(size=len(true_values))
    trade_mask = random_numbers < trade_probability

    trade_profits = true_values[trade_mask] - market_prices[trade_mask]
    trade_profits = apply_trading_costs(
        trade_profits=trade_profits,
        traded_prices=market_prices[trade_mask]
    )

    metrics = calculate_metrics(trade_profits)
    metrics["strategy"] = "random"
    metrics["threshold"] = None
    metrics["trade_probability"] = trade_probability

    return metrics


# ======================
# Printing
# ======================

def print_results_table(results):
    print("\n RESULTS SUMMARY")
    print("=" * 115)

    header = (
        f"{'Strategy':<10}"
        f"{'Threshold':>10}"
        f"{'Profit':>15}"
        f"{'Trades':>12}"
        f"{'Avg/Trade':>12}"
        f"{'Win Rate':>12}"
        f"{'Profit F.':>12}"
        f"{'Max DD':>12}"
        f"{'Sharpe':>10}"
    )
    
    print(header)
    print("-" * 115)

    for experiment in results:
        threshold = experiment["threshold"]

        if threshold is None:
            threshold_display = "N/A"
        else: 
            threshold_display = str(threshold)
        
        row = (
            f"{experiment['strategy']:<10}"
            f"{threshold_display:>10}"
            f"{round(experiment['cash'], 2):>15,}"
            f"{experiment['trades']:>12,}"
            f"{round(experiment['average_profit_per_trade'], 2):>12}"
            f"{round(experiment['win_rate'] * 100, 2):>11}%"
            f"{round(experiment['profit_factor'], 2):>12}"
            f"{round(experiment['max_drawdown'], 2):>12}"
            f"{round(experiment['sharpe_ratio'], 2):>10}"
        )

        print(row)
    
    print("=" * 115)
        

# ======================
# Experiment Runner
# ======================

true_values, signals, market_prices = generate_market_data(NUM_DAYS)

results = []

for threshold in THRESHOLDS:
    signal_experiment = run_signal_strategy(
        true_values=true_values,
        signals=signals,
        market_prices=market_prices,
        threshold=threshold
    )

    results.append(signal_experiment)

    trade_probability = signal_experiment["trades"] / NUM_DAYS

    random_experiment = run_random_strategy(
        true_values = true_values,
        market_prices = market_prices,
        trade_probability = trade_probability
    )

    results.append(random_experiment)

print_results_table(results)

# ======================
# Best Threshold
# ======================

best_by_profit = max(results, key=lambda x: x["cash"])
best_by_sharpe = max(results, key=lambda x: x["sharpe_ratio"])

print("Best strategy by profit:", best_by_profit["strategy"])
print("Best threshold by profit:", best_by_profit["threshold"])
print("Best total profit:", round(best_by_profit["cash"], 2))

print("Best strategy by Sharpe:", best_by_sharpe["strategy"])
print("Best threshold by Sharpe:", best_by_sharpe["threshold"])
print("Best Sharpe ratio:", round(best_by_sharpe["sharpe_ratio"], 2))
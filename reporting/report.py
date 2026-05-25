import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


_COL_WIDTH = {
    "Strategy": 24,
    "Total Ret": 12,
    "CAGR": 10,
    "Sharpe": 10,
    "Sortino": 10,
    "Calmar": 10,
    "Max DD": 12,
    "Win Rate": 10,
}

_TOTAL = sum(_COL_WIDTH.values())


def _fmt_pct(v) -> str:
    return f"{v * 100:.2f}%" if v == v else "N/A"


def _fmt_ratio(v) -> str:
    return f"{v:.2f}" if v == v else "N/A"


def print_summary(results: dict) -> None:
    strategy_name = results["strategy_name"]
    sm = results["strategy"]
    bm = results["buy_hold"]

    print("\nBACKTEST SUMMARY")
    print("=" * _TOTAL)

    header = (
        f"{'Strategy':<{_COL_WIDTH['Strategy']}}"
        f"{'Total Ret':>{_COL_WIDTH['Total Ret']}}"
        f"{'CAGR':>{_COL_WIDTH['CAGR']}}"
        f"{'Sharpe':>{_COL_WIDTH['Sharpe']}}"
        f"{'Sortino':>{_COL_WIDTH['Sortino']}}"
        f"{'Calmar':>{_COL_WIDTH['Calmar']}}"
        f"{'Max DD':>{_COL_WIDTH['Max DD']}}"
        f"{'Win Rate':>{_COL_WIDTH['Win Rate']}}"
    )
    print(header)
    print("-" * _TOTAL)

    for label, m in [(strategy_name, sm), ("Buy & Hold", bm)]:
        row = (
            f"{label:<{_COL_WIDTH['Strategy']}}"
            f"{_fmt_pct(m['total_return']):>{_COL_WIDTH['Total Ret']}}"
            f"{_fmt_pct(m['cagr']):>{_COL_WIDTH['CAGR']}}"
            f"{_fmt_ratio(m['sharpe']):>{_COL_WIDTH['Sharpe']}}"
            f"{_fmt_ratio(m['sortino']):>{_COL_WIDTH['Sortino']}}"
            f"{_fmt_ratio(m['calmar']):>{_COL_WIDTH['Calmar']}}"
            f"{_fmt_pct(m['max_drawdown']):>{_COL_WIDTH['Max DD']}}"
            f"{_fmt_pct(m['win_rate']):>{_COL_WIDTH['Win Rate']}}"
        )
        print(row)

    print("=" * _TOTAL)


def save_equity_chart(results: dict, output_path: str = "equity_curve.png") -> None:
    strategy_name = results["strategy_name"]
    sm = results["strategy"]
    bm = results["buy_hold"]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(sm["equity_curve"], label=strategy_name, linewidth=1.5)
    ax.plot(bm["equity_curve"], label="Buy & Hold", linewidth=1.5, linestyle="--")
    ax.set_title(f"Equity Curve — {strategy_name}")
    ax.set_ylabel("Portfolio Value (normalised to 1)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Equity curve saved to: {os.path.abspath(output_path)}")

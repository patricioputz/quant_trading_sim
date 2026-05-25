import argparse
import sys

from engine.backtester import run_momentum, run_pairs
from reporting.report import print_summary, save_equity_chart


def parse_args():
    parser = argparse.ArgumentParser(description="Trading strategy backtester")
    parser.add_argument(
        "--strategy",
        choices=["momentum", "pairs"],
        default="momentum",
        help="Strategy to run (default: momentum)",
    )
    parser.add_argument("--ticker", default="SPY", help="Ticker for momentum (default: SPY)")
    parser.add_argument(
        "--ticker-a", default="SPY", help="First ticker for pairs (default: SPY)"
    )
    parser.add_argument(
        "--ticker-b", default="QQQ", help="Second ticker for pairs (default: QQQ)"
    )
    parser.add_argument("--start", default="2018-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2026-01-01", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--short-window", type=int, default=20, help="Short MA window (momentum only)"
    )
    parser.add_argument(
        "--long-window", type=int, default=100, help="Long MA window (momentum only)"
    )
    parser.add_argument(
        "--zscore-window", type=int, default=60, help="Rolling z-score window (pairs only)"
    )
    parser.add_argument(
        "--entry-threshold",
        type=float,
        default=2.0,
        help="Z-score entry threshold (pairs only)",
    )
    parser.add_argument(
        "--exit-threshold",
        type=float,
        default=0.0,
        help="Z-score exit threshold (pairs only)",
    )
    parser.add_argument(
        "--chart",
        default="equity_curve.png",
        help="Output path for equity curve PNG (default: equity_curve.png)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Running {args.strategy} strategy  ({args.start} → {args.end})")

    if args.strategy == "momentum":
        results = run_momentum(
            ticker=args.ticker,
            start=args.start,
            end=args.end,
            short_window=args.short_window,
            long_window=args.long_window,
        )
    else:
        results = run_pairs(
            ticker_a=args.ticker_a,
            ticker_b=args.ticker_b,
            start=args.start,
            end=args.end,
            zscore_window=args.zscore_window,
            entry_threshold=args.entry_threshold,
            exit_threshold=args.exit_threshold,
        )

    print_summary(results)
    save_equity_chart(results, output_path=args.chart)


if __name__ == "__main__":
    main()

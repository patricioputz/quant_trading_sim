# Quant Trading Sim

A Python-based quant research sandbox for learning trading simulations, signal testing, strategy optimization, and risk metrics.

## Current Version

This project currently runs a vectorized NumPy simulation of a threshold-based signal strategy.

The simulation:

- Generates hidden true values
- Creates noisy signals
- Generates market prices
- Calculates estimated edge
- Trades only when edge exceeds a threshold
- Tests multiple thresholds
- Tracks total profit, trades, win rate, average win/loss, profit factor, equity curve, and max drawdown

## Goal

The goal is to build this into a larger quant research pipeline with:

- Strategy comparison
- Backtesting on real market data
- Risk analytics
- Transaction costs and slippage
- Paper trading integration
- Cleaner research reports and visualizations

## Day 1 Progress

Built the first version of the signal simulation and converted it to a vectorized NumPy implementation for faster testing across larger sample sizes.
import yfinance as yf
import pandas as pd


def load_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )
    if data.empty:
        raise ValueError(f"No data returned for {ticker} ({start_date} – {end_date})")
    return data


def load_pair_data(
    ticker_a: str, ticker_b: str, start_date: str, end_date: str
) -> tuple[pd.Series, pd.Series]:
    raw = yf.download(
        [ticker_a, ticker_b],
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False,
    )
    closes = raw["Close"].dropna()
    return closes[ticker_a], closes[ticker_b]

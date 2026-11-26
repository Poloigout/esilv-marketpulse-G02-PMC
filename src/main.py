from pathlib import Path
import csv
import json
import yfinance as yf
from analytics import (
    align_series,
    calculate_base_100,
    calculate_period_return,
    calculate_relative_performance,
)
from providers.yahoo_provider import YAHOO_SYMBOLS, fetch_yahoo_prices

DATA_DIR = Path("data/sample")

LOOKBACK_LABEL = "1_month"
INTERVAL_LABEL = "Daily"


def get_first_date(prices):
    return prices[0]["date"]


def get_last_date(prices):
    return prices[-1]["date"]


def load_instruments():
    with open(DATA_DIR / "instruments.json", encoding="utf-8") as file:
        return json.load(file)


def load_prices():
    with open(DATA_DIR / "prices.csv", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def filter_prices(prices, ticker):
    result = []

    for row in prices:
        if row["ticker"] == ticker:
            result.append(row)

    return result


def get_first_close(prices):
    first_price = prices[0]
    close = first_price["close"]

    return float(close)


def get_last_close(prices):
    last_price = prices[-1]
    close = last_price["close"]

    return float(close)


def display_market_summary(asset, prices, show_currency=True):
    ticker = asset["ticker"]
    name = asset["name"]

    first_close = get_first_close(prices)
    last_close = get_last_close(prices)
    print("Observations :", len(prices))
    print("First date :", get_first_date(prices))
    print("Last date :", get_last_date(prices))
    print(ticker + " - " + name)
    print("Observations :", len(prices))

    if show_currency:
        currency = asset["currency"]

        print("First close :", first_close, currency)
        print("Last close :", last_close, currency)

    else:
        print("First close :", first_close)
        print("Last close :", last_close)


def normalize_price_row(row):
    return {
        "date": row["date"],
        "ticker": row["ticker"],
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": int(row["volume"]),
    }


def fetch_yahoo_prices(
    symbol,
    canonical_ticker,
    period="1mo",
    interval="1d",
):
    history = yf.Ticker(symbol).history(
        period=period,
        interval=interval,
        auto_adjust=False,
    )

    if history.empty:
        raise ValueError(
            "No Yahoo Finance data returned for " + symbol
        )

    rows = []

    for timestamp, row in history.iterrows():
        rows.append({
            "date": timestamp.strftime("%Y-%m-%d"),
            "ticker": canonical_ticker,
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
        })

    return rows


def main():
    instrument_ticker = "AAPL"
    benchmark_ticker = "SP500"

    instrument_prices = fetch_yahoo_prices(
        symbol=YAHOO_SYMBOLS[instrument_ticker],
        canonical_ticker=instrument_ticker,
        period="1mo",
        interval="1d",
    )

    benchmark_prices = fetch_yahoo_prices(
        symbol=YAHOO_SYMBOLS[benchmark_ticker],
        canonical_ticker=benchmark_ticker,
        period="1mo",
        interval="1d",
    )

    aligned_instrument, aligned_benchmark = align_series(
        instrument_prices,
        benchmark_prices,
    )

    instrument_return = calculate_period_return(aligned_instrument)
    benchmark_return = calculate_period_return(aligned_benchmark)
    relative_performance = calculate_relative_performance(
        instrument_return,
        benchmark_return,
    )
    instrument_base_100 = calculate_base_100(aligned_instrument)
    benchmark_base_100 = calculate_base_100(aligned_benchmark)

    rel_perf_rounded = round(relative_performance, 2)
    if rel_perf_rounded > 0:
        rel_perf_str = "+" + str(rel_perf_rounded)
    else:
        rel_perf_str = str(rel_perf_rounded)

    print("=== MarketPulse ===")
    print()
    print("Provider")
    print("Yahoo Finance via yfinance")
    print()
    print("Market configuration")
    print("Instrument :", instrument_ticker, "- Apple Inc.")
    print("Benchmark  : S&P 500")
    print("Period     :", LOOKBACK_LABEL)
    print("Interval   :", INTERVAL_LABEL)
    print()
    print("Instrument return :", str(round(instrument_return, 2)) + "%")
    print("Benchmark return  :", str(round(benchmark_return, 2)) + "%")
    print()
    print("Relative performance")
    print(instrument_ticker, "vs", benchmark_ticker, ":", rel_perf_str, "percentage points")
    print()
    print("Base 100")
    print(instrument_ticker, " :", round(instrument_base_100[0]["value"], 2), "->", round(instrument_base_100[-1]["value"], 2))
    print(benchmark_ticker, ":", round(benchmark_base_100[0]["value"], 2), "->", round(benchmark_base_100[-1]["value"], 2))


if __name__ == "__main__":
    main()
from pathlib import Path
import csv
import json
from analytics import (
    align_series,
    calculate_base_100,
    calculate_period_return,
    calculate_relative_performance,
)


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

def main():
    instruments = load_instruments()
    prices = load_prices()

    instrument = instruments["instrument"]
    benchmark = instruments["benchmark"]

    normalized_prices = [
        normalize_price_row(row)
        for row in prices
    ]

    instrument_prices = filter_prices(
        normalized_prices,
        instrument["ticker"],
    )

    benchmark_prices = filter_prices(
        normalized_prices,
        benchmark["ticker"],
    )

    aligned_instrument, aligned_benchmark = align_series(
        instrument_prices,
        benchmark_prices,
    )

    instrument_return = calculate_period_return(
        aligned_instrument,
    )
    benchmark_return = calculate_period_return(
        aligned_benchmark,
    )
    relative_performance = calculate_relative_performance(
        instrument_return,
        benchmark_return,
    )
    instrument_base_100 = calculate_base_100(
        aligned_instrument,
    )
    benchmark_base_100 = calculate_base_100(
        aligned_benchmark,
    )

    instrument_ticker = instrument["ticker"]
    benchmark_ticker = benchmark["ticker"]

    rel_perf_rounded = round(relative_performance, 2)
    if rel_perf_rounded > 0:
        rel_perf_str = "+" + str(rel_perf_rounded)
    else:
        rel_perf_str = str(rel_perf_rounded)

    print("=== MarketPulse ===")
    print()

    print("Market configuration")
    print("Period   :", LOOKBACK_LABEL)
    print("Interval :", INTERVAL_LABEL)
    print()

    print("Instrument")
    print(instrument_ticker, "-", instrument["name"])
    print("Period return :", str(round(instrument_return, 2)) + "%")
    print()

    print("Benchmark")
    print(benchmark_ticker, "-", benchmark["name"])
    print("Period return :", str(round(benchmark_return, 2)) + "%")
    print()

    print("Relative performance")
    print(instrument_ticker, "vs", benchmark_ticker, ":", rel_perf_str, "percentage points")
    print()

    print("Base 100")
    print(instrument_ticker, " :", round(instrument_base_100[0]["value"], 2), "->", round(instrument_base_100[-1]["value"], 2))
    print(benchmark_ticker, ":", round(benchmark_base_100[0]["value"], 2), "->", round(benchmark_base_100[-1]["value"], 2))



if __name__ == "__main__":
    main()
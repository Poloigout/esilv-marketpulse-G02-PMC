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
from analytics import align_series


from providers.yahoo_provider import YAHOO_SYMBOLS, fetch_yahoo_prices
from providers.bloomberg_provider import (
    BLOOMBERG_IDENTIFIERS,
    fetch_raw_bloomberg_history,
    normalize_bloomberg_history,
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
    market = asset["market"]

    first_close = get_first_close(prices)
    last_close = get_last_close(prices)
    print("Observations :", len(prices))
    print("First date :", get_first_date(prices))
    print("Last date :", get_last_date(prices))
    print(ticker + " - " + name)
    print("Market :", market)
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
def build_market_snapshot():
    instrument_ticker = "AAPL"
    benchmark_ticker = "SP500"

    raw_instrument = fetch_raw_bloomberg_history(
        BLOOMBERG_IDENTIFIERS[instrument_ticker],
        None,
        None,
    )
    raw_benchmark = fetch_raw_bloomberg_history(
        BLOOMBERG_IDENTIFIERS[benchmark_ticker],
        None,
        None,
    )

    instrument_prices = normalize_bloomberg_history(
        raw_instrument,
        instrument_ticker,
    )
    benchmark_prices = normalize_bloomberg_history(
        raw_benchmark,
        benchmark_ticker,
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

    return {
        "provider": "Bloomberg stage - APPROVED_SAMPLE",
        "lookback": LOOKBACK_LABEL,
        "interval": INTERVAL_LABEL,
        "instrument": {
            "ticker": instrument_ticker,
            "name": "Apple Inc.",
        },
        "benchmark": {
            "ticker": benchmark_ticker,
            "name": "S&P 500",
        },
        "instrument_return": instrument_return,
        "benchmark_return": benchmark_return,
        "relative_performance": relative_performance,
        "instrument_base_100": instrument_base_100,
        "benchmark_base_100": benchmark_base_100,
    }


def main():
    snapshot = build_market_snapshot()

    print("=== MarketPulse ===")
    print()
    print("Provider")
    print("Bloomberg stage")
    print()
    print("Access mode")
    print("APPROVED_SAMPLE")
    print()
    print("Market configuration")
    print("Instrument :", snapshot["instrument"]["ticker"], "-", snapshot["instrument"]["name"])
    print("Benchmark  :", snapshot["benchmark"]["name"])
    print("Period     :", snapshot["lookback"])
    print("Interval   :", snapshot["interval"])
    print()
    print("Instrument return :", str(round(snapshot["instrument_return"], 2)) + "%")
    print("Benchmark return  :", str(round(snapshot["benchmark_return"], 2)) + "%")
    print()
    print("Relative performance")
    print(
        snapshot["instrument"]["ticker"],
        "vs",
        snapshot["benchmark"]["ticker"],
        ":",
        round(snapshot["relative_performance"], 2),
        "percentage points",
    )
    print()
    print("Base 100")
    print(
        snapshot["instrument"]["ticker"],
        " :",
        round(snapshot["instrument_base_100"][0]["value"], 2),
        "->",
        round(snapshot["instrument_base_100"][-1]["value"], 2),
    )
    print(
        snapshot["benchmark"]["ticker"],
        ":",
        round(snapshot["benchmark_base_100"][0]["value"], 2),
        "->",
        round(snapshot["benchmark_base_100"][-1]["value"], 2),
    )


if __name__ == "__main__":
    main()

from dash import Dash, dcc, html
import plotly.graph_objects as go

from main import build_market_snapshot

app = Dash(__name__)
snapshot = build_market_snapshot()
provider = snapshot["provider"]
lookback = snapshot["lookback"]
interval = snapshot["interval"]

instrument = snapshot["instrument"]
benchmark = snapshot["benchmark"]

instrument_return = snapshot["instrument_return"]
benchmark_return = snapshot["benchmark_return"]
relative_performance = snapshot["relative_performance"]

instrument_base_100 = snapshot["instrument_base_100"]
benchmark_base_100 = snapshot["benchmark_base_100"]

performance = html.Div(
    [
        html.Div(
            [
                html.H3("Instrument Return"),
                html.P(
                    f"{instrument_return:+.2f}%"
                ),
            ]
        ),
        html.Div(
            [
                html.H3("Benchmark Return"),
                html.P(
                    f"{benchmark_return:+.2f}%"
                ),
            ]
        ),
        html.Div(
            [
                html.H3("Relative Performance"),
                html.P(
                    f"{relative_performance:+.2f} pts"
                ),
            ]
        ),
    ]
)
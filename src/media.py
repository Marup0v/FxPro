from __future__ import annotations

from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


def make_chart(frame: pd.DataFrame, symbol: str, interval: str) -> BytesIO:
    chart = frame[["Open", "High", "Low", "Close"]].dropna().tail(80).copy()
    close = chart["Close"].astype(float)
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()

    figure, axis = plt.subplots(figsize=(10, 5), dpi=150)
    figure.patch.set_facecolor("#101820")
    axis.set_facecolor("#101820")
    axis.plot(close.index, close, color="#f5c542", linewidth=1.8, label="Close")
    axis.plot(close.index, ema9, color="#36c5f0", linewidth=1.2, label="EMA9")
    axis.plot(close.index, ema21, color="#ff6b6b", linewidth=1.2, label="EMA21")
    axis.set_title(f"{symbol} | {interval}", color="white")
    axis.tick_params(colors="#dce6ee")
    for spine in axis.spines.values():
        spine.set_color("#405363")
    axis.grid(alpha=0.18, color="white")
    axis.legend(facecolor="#182532", labelcolor="white")
    figure.tight_layout()

    output = BytesIO()
    figure.savefig(output, format="png", facecolor=figure.get_facecolor())
    plt.close(figure)
    output.seek(0)
    return output


def make_candlestick_chart(frame: pd.DataFrame, symbol: str, interval: str) -> BytesIO:
    chart = frame[["Open", "High", "Low", "Close"]].dropna().tail(80).copy()
    figure, axis = plt.subplots(figsize=(10, 5), dpi=150)
    figure.patch.set_facecolor("#101820")
    axis.set_facecolor("#101820")

    for position, (_, candle) in enumerate(chart.iterrows()):
        opening = float(candle["Open"])
        high = float(candle["High"])
        low = float(candle["Low"])
        closing = float(candle["Close"])
        bullish = closing >= opening
        color = "#35d07f" if bullish else "#ff6b6b"
        body_bottom = min(opening, closing)
        body_height = max(abs(closing - opening), 1e-10)
        axis.vlines(position, low, high, color=color, linewidth=0.9)
        axis.add_patch(
            Rectangle(
                (position - 0.32, body_bottom),
                0.64,
                body_height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.8,
            )
        )

    axis.set_title(f"{symbol} | {interval} | Shamlar", color="white")
    axis.set_xlim(-1, len(chart))
    axis.tick_params(colors="#dce6ee")
    for spine in axis.spines.values():
        spine.set_color("#405363")
    axis.grid(alpha=0.18, color="white")
    figure.tight_layout()

    output = BytesIO()
    figure.savefig(output, format="png", facecolor=figure.get_facecolor())
    plt.close(figure)
    output.seek(0)
    return output

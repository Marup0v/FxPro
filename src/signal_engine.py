from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pandas_ta as pta
import talib


@dataclass(frozen=True)
class Signal:
    action: str
    confidence: int
    price: float
    stop_loss: float | None
    take_profit: float | None
    reasons: tuple[str, ...]


def calculate_signal(frame: pd.DataFrame) -> Signal:
    required = {"Open", "High", "Low", "Close"}
    if not required.issubset(frame.columns):
        raise ValueError("OHLC data must contain Open, High, Low and Close columns")

    clean = frame[list(required)].dropna().copy()
    if len(clean) < 60:
        raise ValueError("At least 60 candles are required")

    close = clean["Close"].astype(float)
    fast_ema = pta.ema(close, length=9)
    slow_ema = pta.ema(close, length=21)
    rsi = pta.rsi(close, length=14)
    atr = pd.Series(
        talib.ATR(
            clean["High"].to_numpy(dtype=float),
            clean["Low"].to_numpy(dtype=float),
            close.to_numpy(dtype=float),
            timeperiod=14,
        ),
        index=clean.index,
    )
    macd, macd_signal, _ = talib.MACD(close.to_numpy(dtype=float))
    latest_price = float(close.iloc[-1])
    latest_atr = float(atr.iloc[-1])
    latest_rsi = float(rsi.iloc[-1])
    latest_macd = float(macd[-1])
    latest_macd_signal = float(macd_signal[-1])

    score = 0
    reasons: list[str] = []
    if fast_ema.iloc[-1] > slow_ema.iloc[-1]:
        score += 1
        reasons.append("EMA9 yuqorida: trend yuqoriga")
    else:
        score -= 1
        reasons.append("EMA9 pastda: trend pastga")

    if latest_rsi < 35:
        score += 1
        reasons.append(f"RSI {latest_rsi:.1f}: oversold")
    elif latest_rsi > 65:
        score -= 1
        reasons.append(f"RSI {latest_rsi:.1f}: overbought")
    else:
        reasons.append(f"RSI {latest_rsi:.1f}: neytral zona")

    if close.iloc[-1] > close.iloc[-4]:
        score += 1
        reasons.append("Oxirgi 4 sham narxi o'sgan")
    else:
        score -= 1
        reasons.append("Oxirgi 4 sham narxi pasaygan")

    if latest_macd > latest_macd_signal:
        score += 1
        reasons.append("TA-Lib MACD bullish")
    else:
        score -= 1
        reasons.append("TA-Lib MACD bearish")

    # Require three of four checks to agree before issuing an actionable signal.
    if score >= 3:
        action = "BUY"
    elif score <= -3:
        action = "SELL"
    else:
        action = "WAIT"

    confidence = min(95, 50 + abs(score) * 15)
    if action == "BUY":
        stop_loss = latest_price - (latest_atr * 1.5)
        take_profit = latest_price + (latest_atr * 2.5)
    elif action == "SELL":
        stop_loss = latest_price + (latest_atr * 1.5)
        take_profit = latest_price - (latest_atr * 2.5)
    else:
        stop_loss = take_profit = None

    return Signal(
        action=action,
        confidence=confidence,
        price=latest_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        reasons=tuple(reasons),
    )

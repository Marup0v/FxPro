from __future__ import annotations

import pandas as pd
import yfinance as yf


SYMBOL_GROUPS = {
    "Forex": {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X",
        "AUDUSD": "AUDUSD=X",
        "USDCAD": "CAD=X",
        "USDCHF": "CHF=X",
        "NZDUSD": "NZDUSD=X",
    },
    "Metallar": {
        "Oltin": "GC=F",
        "Kumush": "SI=F",
        "Platina": "PL=F",
        "Mis": "HG=F",
    },
    "Kripto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "BNB": "BNB-USD",
        "Solana": "SOL-USD",
        "XRP": "XRP-USD",
        "Cardano": "ADA-USD",
        "Dogecoin": "DOGE-USD",
    },
    "Indekslar": {
        "S&P 500": "^GSPC",
        "NASDAQ 100": "^NDX",
        "Dow Jones": "^DJI",
        "DAX": "^GDAXI",
        "Nikkei 225": "^N225",
    },
    "Xomashyo": {
        "Neft WTI": "CL=F",
        "Neft Brent": "BZ=F",
        "Tabiiy gaz": "NG=F",
    },
}

SYMBOLS = {
    name: symbol
    for group in SYMBOL_GROUPS.values()
    for name, symbol in group.items()
}

INTERVALS = {
    "1 daqiqa": ("1m", "1d"),
    "5 daqiqa": ("5m", "5d"),
    "15 daqiqa": ("15m", "5d"),
    "1 soat": ("1h", "30d"),
    "4 soat": ("1h", "60d"),
    "1 kun": ("1d", "1y"),
}

CONFIRMATION_INTERVALS = {
    "1m": ("5m", "5d"),
    "5m": ("15m", "5d"),
    "15m": ("1h", "30d"),
    "1h": ("1d", "1y"),
}


def fetch_ohlcv(symbol: str, interval: str, period: str) -> pd.DataFrame:
    frame = yf.download(
        tickers=symbol,
        interval=interval,
        period=period,
        progress=False,
        auto_adjust=False,
        threads=False,
    )
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    if frame.empty:
        raise ValueError("Bozor ma'lumoti kelmadi")
    return frame

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, replace

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from .market_data import CONFIRMATION_INTERVALS, INTERVALS, SYMBOL_GROUPS, fetch_ohlcv
from .media import make_chart, make_candlestick_chart
from .signal_engine import calculate_signal

logger = logging.getLogger(__name__)

GROUP_ICONS = {
    "Forex": "💱",
    "Metallar": "🥇",
    "Kripto": "₿",
    "Indekslar": "📊",
    "Xomashyo": "🛢️",
}

SYMBOL_ICONS = {
    "Bitcoin": "₿",
    "Ethereum": "Ξ",
    "BNB": "🔶",
    "Solana": "◎",
    "XRP": "✕",
    "Cardano": "🔵",
    "Dogecoin": "Ð",
    "Oltin": "🥇",
    "Kumush": "🥈",
    "Platina": "⚪",
    "Mis": "🟠",
}

DECISION_ICONS = {
    "BUY": "🟢 OLISH",
    "SELL": "🔴 SOTISH",
    "WAIT": "🟡 KUTISH",
}


@dataclass
class UserChoice:
    symbol: str = "EURUSD=X"
    interval: str = "15m"
    period: str = "5d"


choices: dict[int, UserChoice] = {}


def _choice(user_id: int) -> UserChoice:
    return choices.setdefault(
        user_id,
        UserChoice(
            symbol=os.getenv("DEFAULT_SYMBOL", "EURUSD=X"),
            interval=os.getenv("DEFAULT_INTERVAL", "15m"),
            period=os.getenv("DEFAULT_PERIOD", "5d"),
        ),
    )


def _main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Instrument tanlash", callback_data="menu:symbol")],
            [InlineKeyboardButton("Timeframe tanlash", callback_data="menu:interval")],
            [InlineKeyboardButton("Signal olish", callback_data="signal")],
            [InlineKeyboardButton("🔄 Signalni yangilash", callback_data="signal")],
        ]
    )


def _signal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📈 Grafik", callback_data="media:chart")],
            [InlineKeyboardButton("🕯 Shamlar", callback_data="media:candles")],
            [
                InlineKeyboardButton("🎟 Sticker", callback_data="media:sticker"),
                InlineKeyboardButton("🎬 Video", callback_data="media:video"),
            ],
            [InlineKeyboardButton("🔄 Signalni yangilash", callback_data="signal")],
            [InlineKeyboardButton("Menyu", callback_data="menu:main")],
        ]
    )


def _symbol_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{GROUP_ICONS.get(group, '📁')} {group}",
                    callback_data=f"group:{group}",
                )
            ]
            for group in SYMBOL_GROUPS
        ]
        + [[InlineKeyboardButton("Orqaga", callback_data="menu:main")]]
    )


def _group_keyboard(group: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{SYMBOL_ICONS.get(name, '•')} {name}",
                    callback_data=f"symbol:{value}",
                )
            ]
            for name, value in SYMBOL_GROUPS[group].items()
        ]
        + [
            [InlineKeyboardButton("Guruhlar", callback_data="menu:symbol")],
            [InlineKeyboardButton("Orqaga", callback_data="menu:main")],
        ]
    )


def _interval_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(name, callback_data=f"interval:{value[0]}:{value[1]}")]
            for name, value in INTERVALS.items()
        ]
        + [[InlineKeyboardButton("Orqaga", callback_data="menu:main")]]
    )


def _format_signal(symbol: str, interval: str, signal, confirmation=None) -> str:
    decision = DECISION_ICONS.get(signal.action, signal.action)
    lines = [
        f"<b>{symbol}</b> | {interval}",
        f"Signal: {signal.action}",
        f"Ishonch: {signal.confidence}%",
        f"Narx: {signal.price:.5f}",
    ]
    if confirmation is not None:
        lines.append(
            f"Tasdiq timeframe: {confirmation['interval']} | "
            f"{DECISION_ICONS.get(confirmation['action'], confirmation['action'])}"
        )
    if signal.stop_loss is not None:
        lines.extend(
            [
                f"Kirish narxi: {signal.price:.5f}",
                f"Stop-loss: {signal.stop_loss:.5f}",
                f"Take-profit: {signal.take_profit:.5f}",
            ]
        )
    lines.append("\n".join(f"- {reason}" for reason in signal.reasons))
    if signal.action == "BUY":
        plan = "Kirish: 🟢 OLISH. Stop-loss tegsa: pozitsiyani yopish."
    elif signal.action == "SELL":
        plan = "Kirish: 🔴 SOTISH. Stop-loss tegsa: pozitsiyani yopish."
    else:
        plan = "Kirish yo'q: 🟡 KUTISH. Tasdiq kuchaymaguncha savdo qilmang."
    lines.append(f"\n<b>Nima qilish kerak: {decision}</b>")
    lines.append(plan)
    lines.append("\nEslatma: bu moliyaviy maslahat emas. Demo hisobda tekshiring.")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    _choice(update.effective_user.id)
    await update.message.reply_text(
        "FX Signal Bot\n\nInstrument va timeframe tanlang, keyin Signal olish tugmasini bosing.",
        reply_markup=_main_keyboard(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_choice = _choice(query.from_user.id)
    data = query.data or ""

    if data == "menu:main":
        await query.edit_message_text("Tanlov menyusi:", reply_markup=_main_keyboard())
    elif data == "menu:symbol":
        await query.edit_message_text("Instrument guruhini tanlang:", reply_markup=_symbol_keyboard())
    elif data.startswith("group:"):
        group = data.split(":", 1)[1]
        if group in SYMBOL_GROUPS:
            await query.edit_message_text(
                f"{group} instrumentlarini tanlang:",
                reply_markup=_group_keyboard(group),
            )
    elif data == "menu:interval":
        await query.edit_message_text("Timeframe tanlang:", reply_markup=_interval_keyboard())
    elif data.startswith("symbol:"):
        user_choice.symbol = data.split(":", 1)[1]
        await query.edit_message_text("Instrument saqlandi. Yana tanlang:", reply_markup=_main_keyboard())
    elif data.startswith("interval:"):
        _, interval, period = data.split(":")
        user_choice.interval = interval
        user_choice.period = period
        await query.edit_message_text("Timeframe saqlandi. Signal olish mumkin:", reply_markup=_main_keyboard())
    elif data.startswith("media:"):
        media_type = data.split(":", 1)[1]
        try:
            if media_type in {"chart", "candles"}:
                frame = await asyncio.to_thread(
                    fetch_ohlcv,
                    user_choice.symbol,
                    user_choice.interval,
                    user_choice.period,
                )
                chart_builder = make_chart if media_type == "chart" else make_candlestick_chart
                chart = await asyncio.to_thread(
                    chart_builder, frame, user_choice.symbol, user_choice.interval
                )
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=chart,
                    caption=f"{'📈' if media_type == 'chart' else '🕯'} {user_choice.symbol} | {user_choice.interval}",
                )
            else:
                env_name = "STICKER_PATH" if media_type == "sticker" else "VIDEO_PATH"
                media_path = os.getenv(env_name, "")
                if not media_path or not os.path.exists(media_path):
                    await query.message.reply_text(
                        f"Media topilmadi. `.env` faylida {env_name} yo'lini ko'rsating."
                    )
                elif media_type == "sticker":
                    with open(media_path, "rb") as sticker:
                        await context.bot.send_sticker(
                            chat_id=query.message.chat_id,
                            sticker=sticker,
                        )
                else:
                    with open(media_path, "rb") as video:
                        await context.bot.send_video(
                            chat_id=query.message.chat_id,
                            video=video,
                            caption="🎬 Signal botdan foydalanish",
                        )
        except Exception as exc:
            logger.exception("Media send failed")
            await query.message.reply_text(f"Media yuborilmadi: {exc}")
    elif data == "signal":
        await query.edit_message_text("Ma'lumot olinmoqda, biroz kuting...")
        try:
            confirmation_config = CONFIRMATION_INTERVALS.get(user_choice.interval)
            requests = [
                asyncio.to_thread(
                    fetch_ohlcv,
                    user_choice.symbol,
                    user_choice.interval,
                    user_choice.period,
                )
            ]
            if confirmation_config:
                requests.append(
                    asyncio.to_thread(
                        fetch_ohlcv,
                        user_choice.symbol,
                        confirmation_config[0],
                        confirmation_config[1],
                    )
                )
            frames = await asyncio.gather(*requests)
            frame = frames[0]
            signal = calculate_signal(frame)
            confirmation = None
            if confirmation_config:
                higher_signal = calculate_signal(frames[1])
                confirmation = {
                    "action": higher_signal.action,
                    "interval": confirmation_config[0],
                }
                if signal.action in {"BUY", "SELL"} and signal.action != higher_signal.action:
                    signal = replace(
                        signal,
                        action="WAIT",
                        confidence=min(signal.confidence, 55),
                        stop_loss=None,
                        take_profit=None,
                        reasons=signal.reasons
                        + ("Yuqori timeframe tasdiqlamadi: xavfsiz kutish",),
                    )
            await query.edit_message_text(
                _format_signal(
                    user_choice.symbol,
                    user_choice.interval,
                    signal,
                    confirmation,
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=_signal_keyboard(),
            )
        except Exception as exc:
            logger.exception("Signal calculation failed")
            await query.edit_message_text(
                f"Signal hisoblab bo'lmadi: {exc}", reply_markup=_main_keyboard()
            )


def build_application(token: str) -> Application:
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    return application

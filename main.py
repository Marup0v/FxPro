from __future__ import annotations

import logging
import os
import asyncio

from dotenv import load_dotenv

from src.bot import build_application


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN .env faylida berilmagan")
    asyncio.set_event_loop(asyncio.new_event_loop())
    build_application(token).run_polling()


if __name__ == "__main__":
    main()

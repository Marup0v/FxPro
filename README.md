# FX Signal Bot

Telegram ichida instrument va timeframe tanlab, texnik indikatorlar asosida `BUY`, `SELL` yoki `WAIT` signalini oladigan demo bot.

## Pro signal imkoniyatlari

- Forex, metallar, kripto, indekslar va xomashyo guruhlari.
- 1 daqiqadan 1 kungacha timeframe tanlovi.
- EMA, RSI, MACD va ATR indikatorlari (`pandas-ta` va `TA-Lib`).
- Yuqori timeframe tasdig'i: tasdiqlanmagan OLISH/SOTISH signali KUTISHga tushiriladi.
- Kirish narxi, stop-loss, take-profit va aniq amal rejasi.
- Belgilar bilan ajratilgan OLISH, SOTISH va KUTISH qarorlari.
- Signal ostida real bozor grafigi, sticker va video tugmalari.

## Ishga tushirish

1. Python 3.12 yoki 3.13 o'rnating. `pandas-ta` hozircha Python 3.14 bilan rasmiy mos emas.
2. Virtual muhit yarating:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Telegram'da `@BotFather` orqali bot yarating va tokenni oling.
4. Loyiha papkasidagi `.env` faylini oching va tokenni shu qatorga yozing:

```env
TELEGRAM_BOT_TOKEN=123456789:AAExampleBotToken
```

`123456789:AAExampleBotToken` o'rniga @BotFather bergan haqiqiy tokenni qo'ying.
5. Botni ishga tushiring:

```bash
python main.py
```

6. Telegram'da botga `/start` yuboring.

## Rasm, sticker va video

Signal xabaridagi `📈 Grafik` tugmasi tanlangan instrumentning real narx grafigini yuboradi.
Sticker va video uchun fayllarni quyidagi joylarga qo'ying:

```text
media/signal.webp
media/how_to_use.mp4
```

Yoki `.env` ichidagi `STICKER_PATH` va `VIDEO_PATH` qiymatlarini o'zgartiring. Fayl bo'lmasa bot qaysi sozlama yetishmayotganini bildiradi.

## Signal qanday hisoblanadi

Bot EMA9/EMA21 trendini, RSI, oxirgi shamlar yo'nalishi va TA-Lib MACD ni birlashtiradi. `BUY` yoki `SELL` chiqqanda ATR asosida taxminiy stop-loss va take-profit ko'rsatiladi. Tez timeframe signali yuqoriroq timeframe bilan mos kelmasa, bot xavfsiz `WAIT` qaytaradi.

Ushbu loyiha faqat signal beradi va order ochmaydi. Real savdodan oldin demo hisob, backtest va risk limiti bilan tekshiring.

## Test

```bash
python -m unittest discover -s tests -v
```

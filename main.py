import os
import time
import requests
import telegram
from datetime import datetime

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def get_movers():
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    data = requests.get(url).json()["result"]["list"]

    # сортируем по изменению цены (24h)
    movers = sorted(data, key=lambda x: float(x["price24hPcnt"]), reverse=True)

    top = movers[:3]
    bottom = movers[-3:]

    msg = f"📊 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    msg += "🚀 Топ роста:\n"
    for coin in top:
        msg += f"{coin['symbol']} {round(float(coin['price24hPcnt'])*100, 2)}%\n"
    msg += "\n📉 Топ падения:\n"
    for coin in bottom:
        msg += f"{coin['symbol']} {round(float(coin['price24hPcnt'])*100, 2)}%\n"
    return msg

def main():
    while True:
        try:
            text = get_movers()
            bot.send_message(chat_id=CHAT_ID, text=text)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"Ошибка: {e}")
        time.sleep(7200)  # каждые 2 часа

if __name__ == "__main__":
    main()

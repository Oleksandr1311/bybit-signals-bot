import requests, os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()

def get_movers():
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    data = requests.get(url, timeout=30).json()["result"]["list"]
    # сортируем по 24h %
    movers = sorted(data, key=lambda x: float(x["price24hPcnt"]))
    top_gainers = movers[-50:][::-1]   # до 50 ростов
    top_losers  = movers[:50]          # до 50 падений

    def fmt(items, title):
        lines = [title]
        for i, c in enumerate(items, 1):
            pct = float(c["price24hPcnt"]) * 100
            lines.append(f"{i}. {c['symbol']}: {pct:.2f}%  | цена {c['lastPrice']}")
        return "\n".join(lines)

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f"📊 Bybit Futures (USDT Perps)\nВремя: {ts}"
    msg1 = header + "\n\n" + fmt(top_gainers, "🚀 Лидеры роста:")
    msg2 = fmt(top_losers, "\n📉 Лидеры падения:")

    # делим, чтобы не превысить лимит Telegram
    for chunk in (msg1, msg2):
        for i in range(0, len(chunk), 3500):
            yield chunk[i:i+3500]

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise SystemExit("Set TELEGRAM_TOKEN and CHAT_ID in secrets/env")
    for part in get_movers():
        send_telegram(part)

if __name__ == "__main__":
    main()

# webhook_listener.py

from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Define options-eligible US tickers and their exchanges
ticker_exchange_map = {
    "AAPL": "NASDAQ",
    "MSFT": "NASDAQ",
    "NVDA": "NASDAQ",
    "AMD": "NASDAQ",
    "SNAP": "NYSE",
    "TSLA": "NASDAQ",
    "META": "NASDAQ",
    "NFLX": "NASDAQ",
    "GOOG": "NASDAQ",
    "AMZN": "NASDAQ",
    "V": "NYSE",
    "MA": "NYSE",
    "PYPL": "NASDAQ"
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    print(f"📤 Sending to Telegram: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload)
    print("📬 Telegram response:", response.status_code, response.text)
    return response

def build_message(data):
    ticker = data.get("ticker", "UNKNOWN")
    price = data.get("price", "N/A")
    condition = data.get("condition", "alert")
    exchange = data.get("exchange", ticker_exchange_map.get(ticker, "Unknown"))

    base = f"📈 *{ticker}* triggered *{condition}* at ${price}"

    if ticker in ticker_exchange_map:
        suggestion = "📊 *Options Eligible* — consider **CALL** or **PUT** setups"
    else:
        suggestion = "🔍 *Non-US Equity or ETF* — evaluate price action manually"

    return f"{base}\n💡 {suggestion}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(silent=True)

        if data is None:
            print("⚠️ No JSON detected — trying raw data")
            raw_data = request.data.decode('utf-8')
            print("📦 Raw body:", raw_data)
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                print("❌ Not valid JSON. Using as plain text message.")
                data = {"message": raw_data}

        print("✅ Final parsed data:", data)

        alert_message = build_message(data)
        response = send_telegram_message(alert_message)

        return "OK", 200

    except Exception as e:
        print("❌ ERROR in webhook:", str(e))
        return f"500 Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


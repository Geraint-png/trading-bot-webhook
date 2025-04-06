from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Add your key tickers here with optional nicknames
TICKER_NAMES = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "SNAP": "Snapchat",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "META": "Meta",
    # Add more as needed
}

# Optional: mark tickers you're watching for options
OPTIONS_TICKERS = {"AAPL", "TSLA", "SNAP", "NVDA"}

def format_alert(data):
    ticker = data.get("ticker", "UNKNOWN").upper()
    price = data.get("price", "N/A")
    condition = data.get("condition", "Alert").capitalize()
    exchange = data.get("exchange", "Exchange")

    company = TICKER_NAMES.get(ticker, ticker)
    emoji = "📈" if condition.lower() in ["breakout", "momentum"] else "🔔"
    options_tag = "💥" if ticker in OPTIONS_TICKERS else ""

    return (
        f"{emoji} *{company}* `{ticker}`\n"
        f"*Condition:* {condition} {options_tag}\n"
        f"*Exchange:* {exchange}\n"
        f"*Price:* ${price}"
    )

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

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(silent=True)
        if data is None:
            print("⚠️ No JSON detected — trying raw data")
            raw_data = request.data.decode('utf-8')
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                data = {"message": raw_data}

        print("✅ Final parsed data:", data)
        alert_message = format_alert(data)
        send_telegram_message(alert_message)
        return "OK", 200

    except Exception as e:
        print("❌ ERROR in webhook:", str(e))
        return f"500 Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)




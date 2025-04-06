from flask import Flask, request
import requests
import json
import os
import time

app = Flask(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Cooldown tracking to prevent spam (per ticker-condition combo)
last_sent = {}

# Customize cooldown duration (seconds)
COOLDOWN_SECONDS = 600  # 10 minutes

# Define US stocks you trade options on
OPTIONS_TICKERS = {"AAPL", "TSLA", "AMD", "NVDA", "MSFT", "GOOGL", "AMZN"}

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
            raw_data = request.data.decode('utf-8')
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                data = {"message": raw_data}

        print("✅ Parsed Webhook Data:", data)

        ticker = data.get("ticker", "UNKNOWN").upper()
        condition = data.get("condition", "alert")
        price = data.get("price", "N/A")

        key = f"{ticker}:{condition}"
        now = time.time()

        # Cooldown filter
        if key in last_sent and now - last_sent[key] < COOLDOWN_SECONDS:
            print(f"⏳ Cooldown active for {key}, skipping alert")
            return "Cooldown active", 200

        last_sent[key] = now  # Update last sent time

        # Options tag if ticker is options-active
        options_tag = "💥 [Options]" if ticker in OPTIONS_TICKERS else ""

        alert_message = f"📈 *{ticker}* triggered *{condition}* at ${price} {options_tag}"
        send_telegram_message(alert_message)

        return "OK", 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return f"500 Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message.encode("utf-16", "surrogatepass").decode("utf-16"),  # Safe emoji encoding
        "parse_mode": "Markdown"
    }

    print(f"📤 Sending to Telegram URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")

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

        print("✅ Final parsed data:", data)

        ticker = data.get("ticker", "UNKNOWN")
        price = data.get("price", "N/A")
        condition = data.get("condition", "alert")
        exchange = data.get("exchange", "")

        # Clean up message format
        exchange_part = f" ({exchange})" if exchange else ""
        message = f"📈 *{ticker.upper()}*{exchange_part} triggered *{condition}* at ${price}"

        response = send_telegram_message(message)
        return "OK", 200

    except Exception as e:
        print("❌ ERROR in webhook:", str(e))
        return f"500 Internal Server Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


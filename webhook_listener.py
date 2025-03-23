# webhook_listener.py

from flask import Flask, request
import requests
import json

app = Flask(__name__)

# Replace with your actual Telegram bot token and chat ID
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
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
        # Try to get JSON — fallback to raw string
        data = request.get_json(silent=True)

        if data is None:
            print("⚠️ No JSON detected — trying raw data")
            raw_data = request.data.decode('utf-8')
            print("📦 Raw body:", raw_data)

            # If raw_data looks like a valid JSON string, try parsing it
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                print("❌ Not valid JSON. Using as plain text message.")
                data = {"message": raw_data}

        print("✅ Final parsed data:", data)

        # Fallback message
        alert_message = data.get("message", "📢 Alert Received")
        response = send_telegram_message(alert_message)
        print("📬 Telegram response:", response.status_code, response.text)

        return "OK", 200

    except Exception as e:
        print("❌ ERROR in webhook:", str(e))
        return f"500 Internal Server Error: {str(e)}", 500




if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



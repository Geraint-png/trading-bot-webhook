from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Your tickers from Trading212 export
TRACKED_TICKERS = [
    '3NVD', 'AAPL', 'ADC', 'ADP', 'AFL', 'AGNC', 'AIR', 'AMD', 'AMZN', 'BA',
    'BP', 'BRK.B', 'BX', 'CCI', 'CG', 'CLX', 'COST', 'CRM', 'CRWD', 'CSCO',
    'CVS', 'CVX', 'DASH', 'DG', 'DHR', 'DIVO', 'DOW', 'DUK', 'EOG', 'EPD',
    'ET', 'ETSY', 'F', 'FDX', 'FLTR', 'GOOG', 'GOOGL', 'HD', 'INTC', 'JNJ',
    'JPM', 'KHC', 'KO', 'LMT', 'MA', 'MCD', 'META', 'MMM', 'MO', 'MRK', 'MSFT',
    'NEE', 'NFLX', 'NKE', 'NVDA', 'O', 'PEP', 'PFE', 'PG', 'PLTR', 'PM', 'PSEC',
    'PYPL', 'QCOM', 'REX', 'RYCEY', 'SCHD', 'SO', 'SPY', 'T', 'TGT', 'TSLA',
    'UAL', 'UL', 'UNH', 'UNP', 'USB', 'V', 'VTI', 'VUAG', 'VUSA', 'VWRP', 'WBA',
    'WFC', 'WMT', 'XOM'
]

US_OPTIONABLE = {'AAPL', 'AMD', 'AMZN', 'GOOG', 'MSFT', 'META', 'NVDA', 'TSLA'}


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    print(f"\ud83d\udce4 Sending to Telegram: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload)
    print("\ud83d\udcec Telegram response:", response.status_code, response.text)
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

        print("\u2705 Final parsed data:", data)

        ticker = data.get("ticker", "UNKNOWN").upper()
        price = data.get("price", "N/A")
        condition = data.get("condition", "alert")
        exchange = data.get("exchange", "").upper()

        # Smart Filtering
        if ticker not in TRACKED_TICKERS:
            print(f"\u274c Ignoring untracked ticker: {ticker}")
            return "Ignored", 200

        # Tailor for US Options
        if ticker in US_OPTIONABLE and exchange == "NASDAQ":
            emoji = "\ud83d\ude80"
            note = "(optionable)"
        else:
            emoji = "\ud83d\udcc8"
            note = ""

        alert_message = f"{emoji} *{ticker}* triggered *{condition}* at ${price} {note}"
        send_telegram_message(alert_message)

        return "OK", 200

    except Exception as e:
        print("\u274c ERROR in webhook:", str(e))
        return f"500 Internal Server Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import requests
import os

# --- Read Credentials from Environment Variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
FMP_API_KEY = os.environ.get("FMP_API_KEY")

def get_market_data():
    """Fetches USD Index (DXY) and USD/INR exchange rate from FMP."""
    try:
        dxy_url = f"https://financialmodelingprep.com/api/v3/quote/%5EDXY?apikey={FMP_API_KEY}"
        usdinr_url = f"https://financialmodelingprep.com/api/v3/fx/USDINR?apikey={FMP_API_KEY}"
        
        dxy_response = requests.get(dxy_url)
        usdinr_response = requests.get(usdinr_url)
        
        dxy_response.raise_for_status()
        usdinr_response.raise_for_status()

        dxy_data = dxy_response.json()[0]
        usdinr_data = usdinr_response.json()[0]

        dxy_price = dxy_data.get('price', 'N/A')
        usdinr_price = usdinr_data.get('ask', 'N/A')

        return dxy_price, usdinr_price
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None

def send_telegram_message(message):
    """Sends a message to your Telegram chat via the bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        print("Message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, FMP_API_KEY]):
        print("Error: One or more environment variables are not set. Please check your Dokploy configuration.")
    else:
        print("Fetching market data...")
        dxy, usdinr = get_market_data()

        if dxy is not None and usdinr is not None:
            message_to_send = (
                f"📈 *Market Update*\n\n"
                f"💵 *US Dollar Index (DXY):* `{dxy:.2f}`\n"
                f"🇮🇳 *USD/INR Exchange Rate:* `{usdinr:.2f}`"
            )
            print("Sending message to Telegram...")
            send_telegram_message(message_to_send)
        else:
            print("Could not fetch data. Message not sent.")
          

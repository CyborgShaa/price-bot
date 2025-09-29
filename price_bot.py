import requests
import os
import json

# --- File path for storing the last prices ---
PRICE_FILE = '/app/last_prices.json'

# --- Read Credentials from Environment Variables ---
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

def read_last_prices():
    """Reads the last saved prices from the file."""
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, 'r') as f:
            return json.load(f)
    return {}

def write_last_prices(prices):
    """Writes the current prices to the file."""
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f)

def get_market_data():
    """Fetches DXY and USD/INR from Twelve Data in a single API call."""
    if not TWELVE_DATA_API_KEY:
        print("Error: TWELVE_DATA_API_KEY environment variable is not set.")
        return None, None
        
    try:
        # Get both symbols in one request to be efficient
        symbols = "DXY,USD/INR"
        url = f"https://api.twelvedata.com/price?symbol={symbols}&apikey={TWELVE_DATA_API_KEY}"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "code" in data and data["code"] != 200:
            print(f"Twelve Data API error: {data.get('message', 'Unknown error')}")
            return None, None

        dxy_price_str = data.get('DXY', {}).get('price')
        usdinr_price_str = data.get('USD/INR', {}).get('price')

        if not dxy_price_str or not usdinr_price_str:
            print("Error: Could not parse price data from Twelve Data response.")
            return None, None

        dxy_price = float(dxy_price_str)
        usdinr_price = float(usdinr_price_str)

        return dxy_price, usdinr_price

    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"Error processing data: {e}")
        return None, None

def send_telegram_message(bot_token, chat_id, message):
    """Sends a message to a specific Telegram chat via a specific bot."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        print(f"Message sent successfully to chat ID: {chat_id}!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {chat_id}: {e}")

if __name__ == "__main__":
    last_prices = read_last_prices()
    
    print("Fetching market data...")
    dxy, usdinr = get_market_data()

    if dxy and usdinr:
        message_lines = ["📈 *Market Update*\n"]
        
        dxy_change_str = ""
        last_dxy = last_prices.get('dxy')
        if last_dxy:
            change = dxy - last_dxy
            percent_change = (change / last_dxy) * 100
            emoji = "🔼" if change > 0 else "🔽"
            dxy_change_str = f"  `{emoji} Change: {change:+.2f} ({percent_change:+.2f}%)`"
        
        message_lines.append(f"💵 *US Dollar Index (DXY):* `{dxy:.2f}`{dxy_change_str}")

        usdinr_change_str = ""
        last_usdinr = last_prices.get('usdinr')
        if last_usdinr:
            change = usdinr - last_usdinr
            percent_change = (change / last_usdinr) * 100
            emoji = "🔼" if change > 0 else "🔽"
            usdinr_change_str = f"  `{emoji} Change: {change:+.4f} ({percent_change:+.2f}%)`"

        message_lines.append(f"🇮🇳 *USD/INR Exchange Rate:* `{usdinr:.4f}`{usdinr_change_str}")

        message_to_send = "\n".join(message_lines)

        bots = []
        bot_1_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        bot_1_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if bot_1_token and bot_1_chat_id:
            bots.append({"token": bot_1_token, "chat_id": bot_1_chat_id})

        if bots:
            print(f"Sending message to {len(bots)} bot(s)...")
            for bot in bots:
                send_telegram_message(bot['token'], bot['chat_id'], message_to_send)
        
        write_last_prices({'dxy': dxy, 'usdinr': usdinr})
    else:
        print("Could not fetch data. Message not sent.")

            

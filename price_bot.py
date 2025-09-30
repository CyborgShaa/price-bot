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
    """Fetches DXY and USD/INR from Twelve Data using two different endpoints."""
    if not TWELVE_DATA_API_KEY:
        print("Error: TWELVE_DATA_API_KEY environment variable is not set.")
        return None, None
        
    try:
        # --- Call 1: Get USD/INR using the /price endpoint ---
        usdinr_url = f"https://api.twelvedata.com/price?symbol=USD/INR&apikey={TWELVE_DATA_API_KEY}"
        usdinr_response = requests.get(usdinr_url)
        usdinr_response.raise_for_status()
        usdinr_data = usdinr_response.json()
        usdinr_price_str = usdinr_data.get('price')

        # --- Call 2: Get DXY using the /quote endpoint with the correct symbol ---
        # THIS IS THE LINE WE ARE FIXING
        dxy_url = f"https://api.twelvedata.com/quote?symbol=TVC:DXY&apikey={TWELVE_DATA_API_KEY}"
        dxy_response = requests.get(dxy_url)
        dxy_response.raise_for_status()
        dxy_data = dxy_response.json()
        dxy_price_str = dxy_data.get('close')

        if not dxy_price_str or not usdinr_price_str:
            print("--- RAW DXY RESPONSE ---")
            print(dxy_data)
            print("--- RAW USD/INR RESPONSE ---")
            print(usdinr_data)
            print("------------------------")
            print("Error: Could not parse price data from one of the Twelve Data responses.")
            return None, None

        dxy_price = float(dxy_price_str)
        usdinr_price = float(usdinr_price_str)

        return dxy_price, usdinr_price

    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"Error processing data: {e}")
        return None, None

# --- The rest of the script is unchanged ---
def send_telegram_message(bot_token, chat_id, message):
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
        

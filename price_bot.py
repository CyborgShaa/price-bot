import requests
import os

# --- Read Credentials from Environment Variables ---
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

def get_market_data():
    """Fetches Dollar Index ETF (UUP) and USD/INR from Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        print("Error: ALPHA_VANTAGE_API_KEY environment variable is not set.")
        return None, None
        
    try:
        usdinr_url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=INR&apikey={ALPHA_VANTAGE_API_KEY}"
        # Using UUP instead of DXY for the Dollar Index
        dxy_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=UUP&apikey={ALPHA_VANTAGE_API_KEY}"

        usdinr_response = requests.get(usdinr_url)
        dxy_response = requests.get(dxy_url)
        
        usdinr_response.raise_for_status()
        dxy_response.raise_for_status()

        usdinr_data = usdinr_response.json()
        dxy_data = dxy_response.json()

        if "Note" in usdinr_data or "Error Message" in usdinr_data:
             print(f"Alpha Vantage API error (USDINR): {usdinr_data}")
             return None, None
        if "Note" in dxy_data or "Error Message" in dxy_data:
             print(f"Alpha Vantage API error (UUP): {dxy_data}")
             return None, None

        usdinr_price_str = usdinr_data.get('Realtime Currency Exchange Rate', {}).get('5. Exchange Rate', 'N/A')
        dxy_price_str = dxy_data.get('Global Quote', {}).get('05. price', 'N/A')

        dxy_price = float(dxy_price_str) if dxy_price_str != 'N/A' else 'N/A'
        usdinr_price = float(usdinr_price_str) if usdinr_price_str != 'N/A' else 'N/A'

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
    bots = []
    bot_1_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    bot_1_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if bot_1_token and bot_1_chat_id:
        bots.append({"token": bot_1_token, "chat_id": bot_1_chat_id})

    bot_2_token = os.environ.get("TELEGRAM_BOT_TOKEN_2")
    bot_2_chat_id = os.environ.get("TELEGRAM_CHAT_ID_2")
    if bot_2_token and bot_2_chat_id:
        bots.append({"token": bot_2_token, "chat_id": bot_2_chat_id})
    
    if not bots:
        print("Error: No bot credentials found in environment variables.")
    else:
        print("Fetching market data...")
        dxy, usdinr = get_market_data()

        if dxy != 'N/A' and usdinr != 'N/A':
            message_to_send = (
                f"📈 *Market Update*\n\n"
                f"💵 *Dollar Index ETF (UUP):* `{dxy:.2f}`\n"
                f"🇮🇳 *USD/INR Exchange Rate:* `{usdinr:.4f}`"
            )
            print(f"Sending message to {len(bots)} bot(s)...")
            for bot in bots:
                send_telegram_message(bot['token'], bot['chat_id'], message_to_send)
        else:
            print("Could not fetch data. Message not sent.")
            

import argparse
import sys
import os
import requests
from dotenv import load_dotenv

def main():
    # Load env vars from .env file if it exists, otherwise rely on system env vars
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables must be set.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Send a message to Telegram.")
    parser.add_argument("--input", "-i", default="message_example.txt", help="Path to input file")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            message_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message_text,
    }

    try:
        response = requests.post(url, json=data, timeout=5)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get("ok"):
            print("Message sent successfully")
        else:
            print(f"Error sending message: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error sending message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

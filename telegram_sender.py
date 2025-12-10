"""
Telegram Notification Utility

This script handles the delivery of messages to a specified Telegram chat via the Bot API.
It strictly separates configuration (Environment Variables) from code, adhering to 
12-Factor App methodology for security and portability.
"""

import argparse
import sys
import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

def main() -> None:
    """
    Main execution flow:
    1. Load Configuration (Fail fast if missing).
    2. Read Payload.
    3. Execute API Request.
    4. Handle Response.
    """
    # Load env vars from .env file to support local development consistency
    load_dotenv()
    
    token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

    # Validation: Fail immediately if critical configuration is missing.
    # This prevents runtime errors later in the pipeline.
    if not token or not chat_id:
        print("Configuration Error: 'TELEGRAM_BOT_TOKEN' and 'TELEGRAM_CHAT_ID' must be set in environment.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Send a message to Telegram.")
    parser.add_argument("--input", "-i", default="message_example.txt", help="Path to input file")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            message_text: str = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    # Construct the API endpoint
    url: str = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": message_text,
    }

    try:
        # We enforce a timeout to prevent the script from hanging on network glitches.
        response = requests.post(url, json=payload, timeout=10)
        
        # Check for HTTP codes implying success (2xx) vs client/server errors
        if response.status_code == 200:
            # Additionally verify the API logic success flag
            if response.json().get("ok"):
                print("Message sent successfully")
            else:
                print(f"API Error: {response.text}")
                sys.exit(1)
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        # Catches DNS failures, connection refused, timeouts, etc.
        print(f"Network Error: Failed to send message. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
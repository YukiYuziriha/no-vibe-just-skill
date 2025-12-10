# Polza Test Task

## 1. Overview
This repository contains solutions for the Polza technical test task. It includes:
1.  **MX Checker:** A script to validate email domains and MX records.
2.  **Telegram Sender:** A script to send messages to a Telegram chat.
3.  **Architecture:** A proposed architecture for a cold outreach system (`ARCHITECTURE.md`).

## 2. Installation
Requires **Python 3.8+**.

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 3. Task 1 – MX Checker
Checks a list of emails for valid domains and MX records.

### Usage
```bash
python mx_checker.py --input emails_example.txt
```

### Output Statuses
*   `"домен валиден"`: The domain exists and has valid MX records.
*   `"домен отсутствует"`: The domain does not exist (NXDOMAIN).
*   `"MX-записи отсутствуют или некорректны"`: The domain exists, but has no valid MX records (or lookup failed).

## 4. Task 2 – Telegram Sender
Sends the content of a text file to a Telegram chat.

### Setup
1.  Create a bot with [BotFather](https://t.me/BotFather) to get a `TELEGRAM_BOT_TOKEN`.
2.  Get your `TELEGRAM_CHAT_ID` (e.g., via `@userinfobot`).
3.  Copy `.env.example` to `.env` and fill in your credentials:
    ```bash
    cp .env.example .env
    ```

### Usage
```bash
python telegram_sender.py --input message_example.txt
```

## 5. Task 3 – Architecture
Please verify the architectural proposal in [ARCHITECTURE.md](ARCHITECTURE.md).

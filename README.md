# Polza Test Task

## 1. Overview
This repository contains solutions for the Polza technical test task. It includes:
1.  **MX Checker:** A script to validate email domains and MX records.
2.  **Telegram Sender:** A script to send messages to a Telegram chat.
3.  **Architecture:** A proposed architecture for a cold outreach system (`ARCHITECTURE.md`).

## 2. Installation & Setup

You need **Python 3.8+** installed.

### Windows

1.  **Open the terminal in this folder:**
    *   Open the folder in File Explorer.
    *   Click the address bar at the top, type `cmd`, and press Enter.
    *   *Alternatively: Hold `Shift`, right-click empty space, and select "Open PowerShell window here".*

2.  **Create a virtual environment:**
    ```cmd
    python -m venv .venv
    ```

3.  **Activate it:**
    *   **Command Prompt (cmd):**
        ```cmd
        .venv\Scripts\activate
        ```
    *   **PowerShell:**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *(If you see a security error in PowerShell, run `Set-ExecutionPolicy Unrestricted -Scope Process` first)*

4.  **Install libraries:**
    ```cmd
    pip install -r requirements.txt
    ```

### Linux / macOS

1.  **Open Terminal** and `cd` to this project folder:
    ```bash
    cd /path/to/downloaded/folder
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate it:**
    ```bash
    source .venv/bin/activate
    ```

4.  **Install libraries:**
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

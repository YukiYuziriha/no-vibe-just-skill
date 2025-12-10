# Polza Outreach Technical Task

## 1. Overview
This repository contains a compact yet production-minded solution for the Polza technical task:

1. **MX Checker** — validates email domains and MX records for a list of addresses.
2. **Telegram Sender** — sends arbitrary text content to a Telegram chat via the Bot API.
3. **Architecture** — an outreach system design for ~1200 emails/day in `ARCHITECTURE.md`.

The implementation emphasises robustness, predictable error handling, and clarity over cleverness. 
Abstractions are intentionally kept minimal so that behaviour is easy to audit and operate.

## 2. Project Structure
```text
.
├── mx_checker.py        # Task 1: MX checker CLI
├── emails_example.txt   # Sample input for MX checker
├── telegram_sender.py   # Task 2: Telegram sender CLI
├── message_example.txt  # Sample input for Telegram sender
├── .env.example         # Example configuration for Telegram credentials
├── ARCHITECTURE.md      # Task 3: outreach system architecture
├── PLAN.md              # Original planning notes
├── README.md
└── requirements.txt     # dnspython, requests, python-dotenv
```

## 3. Requirements & Installation

- Python **3.8+**
- `pip` and the ability to create virtual environments.

### 3.1. Windows

1. **Open a terminal in this folder**
   - Open the project folder in Explorer.
   - Click the address bar, type `cmd`, press Enter  
     *(or: Shift + right click → “Open PowerShell window here”)*.
2. **Create a virtual environment**
   ```cmd
   python -m venv .venv
   ```
3. **Activate it**
   - Command Prompt:
     ```cmd
     .venv\Scripts\activate
     ```
   - PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
     *(If you see a security error, run `Set-ExecutionPolicy Unrestricted -Scope Process` once.)*
4. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

### 3.2. Linux / macOS

1. **Open Terminal** and move to the project folder:
   ```bash
   cd /path/to/no-vibe-just-skill
   ```
2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   ```
3. **Activate it**
   ```bash
   source .venv/bin/activate
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 4. Task 1 — MX Checker (`mx_checker.py`)

The MX checker consumes a text file with one email per line, validates the domain, and inspects MX records using `dnspython`.

### 4.1. Usage
```bash
python mx_checker.py --input emails_example.txt
```

Arguments:
- `--input` / `-i` — path to a file with one email per line (default: `emails_example.txt`).

### 4.2. Behaviour & Statuses
For each non-empty line, the script prints exactly one of the following statuses:

- `<email>: домен валиден` — the domain exists and has at least one MX record.
- `<email>: домен отсутствует` — the domain does not exist or has no reachable nameservers.
- `<email>: MX-записи отсутствуют или некорректны` — the domain exists but MX lookup fails or returns no usable records.

Malformed addresses (e.g. missing `@` or with multiple `@`) are treated as `"домен отсутствует"` to simplify downstream list-cleaning logic.

### 4.3. Error Handling
- If the input file does not exist, the script prints a clear error and exits with code `1`.
- DNS queries use a **5-second timeout** to avoid hanging on slow or misconfigured name servers, which is common in bulk outreach scenarios.
- Unexpected DNS/network errors are treated as `"MX-записи отсутствуют или некорректны"` and do not crash the process.

---

## 5. Task 2 — Telegram Sender (`telegram_sender.py`)

The Telegram sender reads the full contents of a text file and posts it to a configured Telegram chat using a bot token.
Configuration is provided exclusively via environment variables (12-factor style) and an optional `.env` file for local development.

### 5.1. Configuration

1. **Create a bot token**
   - In Telegram, search for **@BotFather**.
   - Send `/newbot` and follow the prompts.
   - Copy the token you receive (e.g. `123456:ABC-DEF...`).

2. **Obtain your chat ID**
   - In Telegram, search for **@userinfobot**.
   - Click “Start”.
   - Copy the number shown as `Id:` (e.g. `123456789`).

3. **Populate `.env`**
   - In this folder there is a file `.env.example`.
   - Make a copy named `.env` (or rename it to `.env`).
   - Open `.env` in a text editor and fill in your values:
     ```text
     TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
     TELEGRAM_CHAT_ID=123456789
     ```
   - Save the file. On startup, the script uses `python-dotenv` to load these values.

Alternatively, you can set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` directly in the environment without using `.env`.

### 5.2. Usage
```bash
python telegram_sender.py --input message_example.txt
```

Arguments:
- `--input` / `-i` — path to the text file whose contents should be sent (default: `message_example.txt`).

### 5.3. Behaviour & Error Handling

- On startup, the script validates that both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are present.
  If either is missing, it prints a configuration error and exits with code `1`.
- The message body is read as UTF‑8, so non-ASCII characters in `message_example.txt` are preserved.
- Requests to `https://api.telegram.org/bot<TOKEN>/sendMessage`:
  - Use a **10-second timeout** to avoid indefinite hangs on network glitches.
  - Treat non-`200` HTTP statuses as errors and print the response body.
  - Additionally verify the `"ok"` flag in the JSON response before reporting success.
- All `requests`-level network exceptions (DNS failure, timeout, connection reset, etc.) are caught and reported with a human-readable message.

---

## 6. Task 3 — Architecture (`ARCHITECTURE.md`)

High-level architecture for sending ~1200 emails/day is documented in `ARCHITECTURE.md`.  
It covers:

- Domain and mailbox strategy to protect reputation.
- Scheduling and routing logic across multiple senders.
- Bounce/complaint-driven health checks and automatic pausing.
- Monitoring, metrics, and an alerting channel (Telegram bot).
- A rough cost estimate for domains, infrastructure, and ESP usage.

---

## 7. Testing

The solution was exercised with a small but representative set of scenarios:

- **MX Checker**
  - `emails_example.txt` includes:
    - Valid consumer domains (`gmail.com`, `ya.ru`).
    - A placeholder domain (`example.com`).
    - A clearly non-existent domain (`nonexistentdomain12345.com`).
    - A malformed email (`brokenemail.com`).
  - Verified that each case maps to the expected of the three statuses.

- **Telegram Sender**
  - Successful path with a valid token/chat ID and a short UTF‑8 text message.
  - Failure modes:
    - Missing environment variables (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
    - Network-level failure (simulated) resulting in a clear error and non-zero exit code.

The focus is on deterministic behaviour and clear failure modes rather than exhaustive test coverage for every edge case.

---

## 8. Quality Notes

- The scripts are intentionally **small, linear, and explicit** so that future changes can be made without guessing hidden abstractions.
- External dependencies (`dnspython`, `requests`, `python-dotenv`) are limited to what is strictly necessary for DNS resolution, HTTP calls, and configuration loading.
- Timeouts and error handling are tuned for **bulk outreach** workloads: the system prefers to fail fast on slow or misconfigured infrastructure instead of blocking the entire job.
- All user-facing messages are designed to be copy-paste friendly for support logs and automation.

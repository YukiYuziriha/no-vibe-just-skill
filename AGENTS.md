# Repository Agent Guidelines

> **Role:** If you are an automated assistant (LLM or tool) maintaining this repository, follow these rules to keep the project coherent, predictable, and easy to operate.

## 1) Scope & Intent

- This repo is a **small, self-contained solution** for the Polza outreach technical task.
- Primary goals: **reliability**, **clarity**, and **minimalism** — not clever abstractions.
- Everything here should be easy to understand for a human operator skimming the code and docs in a few minutes.

## 2) Tech & Dependencies

- Runtime: **Python 3.8+**.
- Entry points: `mx_checker.py` and `telegram_sender.py` (both CLI tools).
- Allowed runtime dependencies are intentionally narrow:
  - `dnspython` — DNS / MX resolution.
  - `requests` — HTTP calls to Telegram Bot API.
  - `python-dotenv` — local configuration via `.env`.
- Do **not** introduce heavy frameworks or additional services unless a future task explicitly requires them.

## 3) Behavioural Contracts

### 3.1 MX Checker (`mx_checker.py`)

- Input: a text file with **one email per line** (UTF‑8).
- For every non-empty line, the script must print **exactly one** status line of the form:
  - `<email>: домен валиден`
  - `<email>: домен отсутствует`
  - `<email>: MX-записи отсутствуют или некорректны`
- Malformed addresses (no `@` or more than one `@`) are treated as `"домен отсутствует"` by design.
- DNS lookups **must** use a finite timeout; hanging indefinitely on slow name servers is unacceptable.
- If you need to change output wording or formatting, update `README.md` and any tests or tooling that rely on these strings.

### 3.2 Telegram Sender (`telegram_sender.py`)

- Configuration comes **only** from environment variables:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
- Local development may use `.env` loaded via `python-dotenv`, but production must be able to work with plain environment variables.
- Exit codes:
  - `0` on success.
  - Non-zero on configuration errors, input file errors, HTTP/API failures, or network exceptions.
- Network calls must have explicit timeouts and clear error messages that are suitable for copy‑pasting into support logs.

## 4) Error Handling & Logging

- Fail fast on **misconfiguration** (missing env vars, missing files, invalid arguments).
- Treat unexpected DNS or network issues as **data-quality problems** for the current email/message, not as reasons to crash the whole process.
- User-facing messages should be:
  - Short and actionable.
  - Sufficiently clear for non-expert operators.
  - Stable enough to be used in simple automation if needed.

## 5) Code Style & Structure

- Prefer **straight-line, explicit code** over deep call graphs or heavy indirection.
- Use type hints for public functions and key variables when it improves readability.
- Docstrings and comments should explain **why** a decision was made (timeouts, thresholds, contracts), not restate what a line of code obviously does.
- Keep modules small and focused; this repo does not need packages or complex module hierarchies.

## 6) Testing Guidelines

- If you add automated tests, use **pytest**.
- Tests should be **deterministic** and should not depend on external services:
  - Mock DNS resolution for MX checks.
  - Mock HTTP calls to the Telegram API.
- Focus tests on:
  - Output contracts (status strings, exit codes).
  - Behaviour under error conditions (missing files, missing env vars, timeouts).
- Do not overfit to implementation details; the contracts in this file and in `README.md` are the source of truth.

## 7) Documentation Discipline

- Treat `README.md` as the **canonical source of truth** for:
  - How to run each script.
  - Required environment variables and configuration.
  - Expected outputs and error modes.
- When you change CLIs, environment variables, or file paths, update `README.md` and example files (`emails_example.txt`, `message_example.txt`) in the same change.
- Keep `ARCHITECTURE.md` **dense and technical**, written in a neutral engineering tone.

## 8) Non-Goals

- No web UI, no large frameworks, no background workers or queues unless a future requirement clearly asks for them.
- Do not turn this into a general-purpose outreach platform; it is intentionally a **focused, well-engineered example**.

---

### Pocket Version

- Minimal, robust CLI tools with clear contracts.
- Preserve MX checker output strings exactly unless you also update docs/tests.
- Fail fast on configuration issues; always use timeouts for network and DNS.
- Comments and docs should emphasise motivation and trade-offs, not obvious mechanics.


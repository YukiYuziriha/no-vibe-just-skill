
## 0. Goal & Constraints

* Deliver **1 small project** that:

  * Solves all 3 tasks exactly as described.
  * Is **minimal**, readable, and obviously working.
  * Does **not** over-engineer anything.
* Tech stack: pure Python + a couple of small libs (`dnspython`, `requests`).
* Deliver as **one link** (GitHub / Drive / etc.).

---

## 1. Project Structure

Create a folder/repo:

```text
polza-test-task/
  README.md
  requirements.txt

  mx_checker.py
  emails_example.txt

  telegram_sender.py
  message_example.txt
  .env.example

  ARCHITECTURE.md
```

**Purpose of each:**

* `README.md` — how to run everything.
* `requirements.txt` — dependencies (`dnspython`, `requests`).
* `mx_checker.py` — Task 1 solution.
* `emails_example.txt` — sample input for Task 1.
* `telegram_sender.py` — Task 2 solution.
* `message_example.txt` — sample input for Task 2.
* `.env.example` — shows how to set Telegram credentials.
* `ARCHITECTURE.md` — Task 3 text.

---

## 2. Task 1 – `mx_checker.py` (Email MX Checker)

### 2.1. Functional behavior

Script responsibilities:

1. Accept a **text file** with one email per line.
2. For each email:

   * Ignore empty lines / whitespace.
   * If format is clearly broken (no `@` or more than one) → treat as “no domain”.
   * Otherwise extract domain (string after `@`).
   * Check if domain exists and whether MX records are present.
3. Print for each email:

```text
<email>: домен валиден
<email>: домен отсутствует
<email>: MX-записи отсутствуют или некорректны
```

Strings **must match exactly**.

### 2.2. CLI interface

* Use `argparse`:

  * `--input` / `-i` (optional), default: `emails_example.txt`.

Example:

```bash
python mx_checker.py --input emails_example.txt
```

### 2.3. Implementation details

* Use `dnspython`:

  ```python
  import dns.resolver
  ```

* Core logic:

  * Parse file into a list of email strings.
  * For each email:

    * `if email.count("@") != 1` → `"домен отсутствует"`.
    * `domain = email.split("@")[1].strip()`.
    * Try `dns.resolver.resolve(domain, "MX", lifetime=5)`.

      * If MX query returns records → `"домен валиден"`.
      * If `NXDOMAIN` / `NoNameservers` / similar → `"домен отсутствует"`.
      * If domain exists but MX lookup fails / no MX records → `"MX-записи отсутствуют или некорректны"`.

* Error handling:

  * If input file doesn’t exist → print clear error and `sys.exit(1)`.
  * For unexpected exceptions per-domain:

    * Catch and treat as `"MX-записи отсутствуют или некорректны"` with a short note to stdout or silently.

### 2.4. Test data – `emails_example.txt`

Put a small mix:

```text
user@gmail.com
user@ya.ru
user@example.com
user@nonexistentdomain12345.com
brokenemail.com
```

So you clearly produce all 3 statuses.

---

## 3. Task 2 – `telegram_sender.py` (Telegram Mini-Integration)

### 3.1. Functional behavior

Script responsibilities:

1. Read full text from `.txt` file.
2. Send that text to a private Telegram chat via a bot.
3. Print success or clear error.

### 3.2. Configuration

* Use **environment variables**:

  * `TELEGRAM_BOT_TOKEN`
  * `TELEGRAM_CHAT_ID`

* Provide `.env.example` with placeholders:

  ```env
  TELEGRAM_BOT_TOKEN=your_bot_token_here
  TELEGRAM_CHAT_ID=your_chat_id_here
  ```

* In `README.md`, explain:

  * How to create a bot (short).
  * How to get `chat_id` in the simplest way.
  * How to set env vars.

### 3.3. CLI interface

* Use `argparse`:

  * `--input` / `-i`, default: `message_example.txt`.

Example:

```bash
python telegram_sender.py --input message_example.txt
```

### 3.4. Implementation details

* Use `requests`:

  ```python
  import requests
  ```

* At start:

  * Read env vars; if missing → print clear error message (Russian or English is fine) and `sys.exit(1)`.

* Read file content fully into a string (UTF-8).

* Build request:

  ```python
  url = f"https://api.telegram.org/bot{token}/sendMessage"
  data = {
      "chat_id": chat_id,
      "text": message_text,
  }
  requests.post(url, json=data, timeout=5)
  ```

* Handle response:

  * If status code is 200 and `"ok": true` in JSON → print `"Message sent successfully"`.
  * Else:

    * Print error text / JSON.
    * `sys.exit(1)`.

### 3.5. Test data – `message_example.txt`

Example content:

```text
Тестовое сообщение для Polza. Если вы видите это в чате — скрипт работает.
```

---

## 4. Task 3 – `ARCHITECTURE.md` (Email Outreach Architecture for 1200 Addresses)

### 4.1. Format

* 0.5–1 page of **dense text** (no bullshit).
* Structured with a few headings, but not overformatted.

### 4.2. Content outline

1. **Goal / Context**

   * 1200 email addresses for cold outreach.
   * Multiple clients and campaigns.
   * Focus: low cost, good deliverability, fault tolerance.

2. **Core components**

   * Domains & DNS (e.g. Cloudflare).
   * Email providers / SMTP (e.g. AWS SES or similar low-cost provider).
   * Control service / scheduler:

     * stores accounts, domains, campaigns, limits;
     * queues sends and enforces rate limits.
   * Logging & monitoring:

     * store send results (success, bounce, spam, block codes);
     * simple dashboard or periodic export;
     * alerts to Telegram when metrics exceed thresholds.

3. **Domain & mailbox strategy**

   * Several root domains + subdomains per client.
   * E.g. 5–10 domains, each with multiple mailboxes.
   * Purpose:

     * isolate risk per client;
     * separate warmup/sending roles if needed.

4. **Warmup process**

   * Each new mailbox starts at low volume:

     * e.g. 5–10 emails/day first week,
     * ramp up to 40–50/day over 3–4 weeks.
   * Send warmup emails with higher likelihood of replies / opens (optionally using a warmup tool or internal loop).
   * Automatically reduce or freeze sending if:

     * bounce rate spikes,
     * spam complaints appear.

5. **Rotation & load distribution**

   * For each campaign:

     * define daily caps per mailbox and per domain.
   * Sending engine:

     * picks next “healthy” mailbox (within limits, not in cooldown, low recent bounces).
     * spreads load across domains and providers to avoid rate limit and reputation issues.

6. **Monitoring & risk handling**

   * Monitor per-domain / per-mailbox:

     * delivery rate,
     * bounces,
     * spam complaints,
     * provider errors.
   * If thresholds exceeded:

     * pause that mailbox/domain,
     * send alerts to Telegram,
     * optionally spin up replacement mailbox.

7. **Cost estimate (rough)**

   * Domains: ~10 domains × ~$10/year ≈ $100/year.
   * Provider: sending up to couple hundred thousand emails / month with low-cost provider ≈ tens of dollars / month.
   * Compute: 1–2 small VPS instances or serverless functions → cheap.
   * Conclusion: architecture is low-cost and scalable by adding domains/mailboxes as outreach volume grows.

---

## 5. `README.md` Content

Keep it short and practical.

Sections:

1. **Overview**

   * One paragraph: this repo contains solutions for 3 tasks (MX checking, Telegram sending, architecture description).

2. **Installation**

   * Python version requirement.
   * Commands:

     ```bash
     pip install -r requirements.txt
     ```

3. **Task 1 – MX Checker**

   * Input file format (one email per line).
   * Example:

     ```bash
     python mx_checker.py --input emails_example.txt
     ```
   * Explain statuses in Russian:

     * `"домен валиден"` — domain exists, MX records found.
     * `"домен отсутствует"` — domain does not exist.
     * `"MX-записи отсутствуют или некорректны"` — domain exists, but no valid MX.

4. **Task 2 – Telegram Sender**

   * Steps:

     1. Create bot via BotFather → get token.
     2. Get `chat_id` (brief explanation).
     3. Set env vars or `.env` based on `.env.example`.
   * Run:

     ```bash
     python telegram_sender.py --input message_example.txt
     ```

5. **Task 3 – Architecture**

   * Point to `ARCHITECTURE.md`.

---

## 6. Execution Order 

1. Create project structure & `requirements.txt`.
2. Implement `mx_checker.py` + `emails_example.txt`.
3. Test Task 1 on your machine.
4. Implement `telegram_sender.py` + `.env.example` + `message_example.txt`.
5. Test Task 2 by sending message to yourself.
6. Write `ARCHITECTURE.md`.
7. Write `README.md`.
8. Zip repo or push to GitHub and send link to them in Telegram with code phrase.


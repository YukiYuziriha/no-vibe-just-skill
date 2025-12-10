# Email Outreach Architecture for 1200 Addresses

## 1. Goal & Context
The objective is to establish a reliable, low-cost email outreach infrastructure for sending approximately 1200 emails per day across multiple campaigns. The system prioritizes high deliverability, fault tolerance, and cost-efficiency. It must handle sending limits, bounce management, and monitoring to prevent domain blacklisting.

## 2. Core Components
The architecture consists of four main layers:

1.  **Infrastructure & DNS:**
    *   **DNS Provider:** Cloudflare (for fast propagation and security).
    *   **Email Service Provider (ESP):** AWS SES (Amazon Simple Email Service) or a similar low-cost SMTP provider (e.g., Mailgun, SendGrid on tiered plans) to handle the actual transmission.
    *   **Hosting:** A small VPS (e.g., DigitalOcean Droplet, AWS t3.micro) or Serverless Functions (AWS Lambda) to run the control logic.

2.  **Control Plane (The Scheduler):**
    *   A custom script or lightweight service (Python/Node.js) that manages the queue.
    *   **Database:** Redis or a simple SQL database (PostgreSQL/SQLite) to store:
        *   Accounts/Domains config.
        *   Daily send limits and current usage counters.
        *   Campaign queues.

3.  **Sending Engine:**
    *   Enforces rate limiting per mailbox and per domain.
    *   Rotates between available healthy mailboxes.
    *   Handles "cool-down" periods for warm-up.

4.  **Logging & Monitoring:**
    *   Collects webhooks/events from the ESP (Deliveries, Bounces, Complaints).
    *   Alerting system (Telegram Bot) to notify admins of spikes in bounce rates (>5%) or spam complaints (>0.1%).

## 3. Domain & Mailbox Strategy
To isolate risk and ensure long-term sustainability, we will not rely on a single domain.

*   **Structure:** Purchase 5-10 separate root domains (e.g., `brand-news.com`, `brand-updates.com`) rather than subdomains of the main business domain. This protects the primary corporate domain's reputation.
*   **Mailboxes:** Create 2-3 distinct mailboxes per domain (e.g., `alex@...`, `hello@...`).
*   **Total Capacity:** 10 domains × 3 mailboxes = 30 sending nodes. This allows for very conservative sending limits per node.

## 4. Warmup Process
New domains and mailboxes must be warmed up to establish trust with ISPs (Gmail, Outlook).

*   **Phase 1 (Week 1):** Send 5-10 manual/highly targeted emails per day per mailbox.
*   **Phase 2 (Weeks 2-3):** Ramp up by 20% daily, aiming for 40-50 emails/day per mailbox.
*   **Automation:** Use an internal loop (sending to own seed accounts) or a dedicated warm-up tool to guarantee high open and reply rates during this phase.
*   **Safety Net:** If a domain triggers a spam block, it is immediately removed from the rotation and placed in "Cool-down" mode for 2 weeks.

## 5. Rotation & Load Distribution
We treat the 1200 emails/day target as a distributed workload.

*   **Load Balancing:** The Sending Engine does not blast from one address. It iterates through the pool of 30 mailboxes.
    *   Target: ~40 emails per mailbox/day.
    *   Calculation: 30 mailboxes × 40 emails = 1200 emails/day.
*   **Smart Selection:** The logic picks the next mailbox that:
    1.  Has not reached its daily limit.
    2.  Is not flagged or in cool-down.
    3.  Has the lowest recent bounce rate.

## 6. Monitoring & Risk Handling
Automated health checks are critical.

*   **Metrics:** Track Delivery Rate, Open Rate, and most importantly, Bounce Rate and Complaint Rate.
*   **Thresholds:**
    *   **Bounce Rate > 3%:** Warning.
    *   **Bounce Rate > 5%:** Auto-pause specific mailbox.
    *   **Spam Complaint:** Auto-pause specific mailbox and review content.
*   **Alerts:** Immediate notification via Telegram for any critical pauses or limit breaches.

## 7. Cost Estimate (Rough)
This architecture is designed to be extremely cost-effective.

*   **Domains:** 10 domains @ ~$12/year = $120/year.
*   **Email Sending (AWS SES):** $0.10 per 1,000 emails. For ~36,000 emails/month = ~$3.60/month.
*   **Server/Hosting:** ~$5 - $10/month for a small VPS.
*   **Total:** Approximately **$15 - $20 per month** + $120 annual domain costs.

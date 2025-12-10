# Email Outreach Architecture for 1200 Addresses

## 1. Goal & Context

The goal is to operate a reliable, low-cost cold outreach system that can send ~1200 emails per day across multiple campaigns without burning domain reputation.  
The system must:

- Maintain high deliverability and minimise spam complaints.
- Tolerate domain reputation degradation and individual provider outages.
- Enforce conservative sending limits per mailbox.
- Provide clear observability and fast feedback loops on bounces and complaints.

## 2. High-Level Design

At a high level, the system looks like this:

```text
[Campaigns] 
    ↓
[Scheduler / Control Plane] → [Sending Engine] → [ESP(s)] → [Recipient Mailboxes]
                                      ↓
                              [Events Collector]
                                      ↓
                              [Metrics Store]
                                      ↓
                               [Alerting Bot]
```

The architecture consists of four main layers:

1. **Infrastructure & DNS**
   - **DNS Provider:** Cloudflare (fast propagation, DNS-level protection).
   - **Email Service Provider (ESP):** AWS SES as the primary channel; optionally a secondary ESP (e.g. Mailgun/SendGrid) as a cold standby to mitigate provider outages.
   - **Hosting:** A small VPS (DigitalOcean Droplet, AWS t3.micro) or serverless functions (AWS Lambda) to host the scheduler and sending logic.

2. **Control Plane (Scheduler)**
   - A lightweight service (Python/Node.js) that:
     - Pulls pending messages from campaign queues.
     - Decides which mailbox should send each message.
     - Applies per-mailbox and per-domain quotas.
   - **State Storage:** Redis or a simple SQL database (PostgreSQL/SQLite) containing:
     - Domain and mailbox configuration.
     - Daily send counters and limits.
     - Campaign queues and message states (pending/sent/failed).

3. **Sending Engine**
   - Executes SMTP/API calls to the ESPs.
   - Applies rate limiting per mailbox and per domain.
   - Implements "cool-down" periods for warm-up and for mailboxes that show degraded metrics.

4. **Logging & Monitoring**
   - Collects events from ESP webhooks: deliveries, bounces, complaints, unsubscribes.
   - Persists events into a metrics store (relational DB, ClickHouse, or even a well-structured log index).
   - Exposes a minimal dashboard plus an alerting path (Telegram bot) for operational awareness.

This separation allows us to scale the control plane independently from the sending engine and to swap ESPs with minimal change.

## 3. Domain & Mailbox Strategy

To avoid tying the system to a single domain or sender identity, we distribute risk across multiple domains.

- **Domain Pool**
  - Acquire 5–10 independent root domains (e.g. `brand-news.com`, `brand-updates.com`), not subdomains of the primary corporate domain.
  - This protects the main brand domain from potential blacklisting.

- **Mailbox Pool**
  - Create 2–3 mailboxes per domain (`alex@…`, `hello@…`, `team@…`).
  - With 10 domains × 3 mailboxes each, we get ~30 independent sending identities.

- **Capacity Envelope**
  - Target ~40 emails per mailbox per day:
    - 30 mailboxes × 40 emails ≈ 1200 emails/day.
  - These limits are intentionally conservative and can be adjusted upward once we have stable reputation data.

## 4. Warm-Up & Reputation Management

New domains and mailboxes must be warmed up before they join the main sending pool.

- **Phase 1 (Week 1)**
  - 5–10 highly targeted, manual or semi-manual emails per mailbox per day.
  - Prioritise engaged recipients and short, personalised messages.

- **Phase 2 (Weeks 2–3)**
  - Increase send volume by ~20% per day until reaching 40–50 emails/day per mailbox.
  - Use seed accounts and friendly contacts to keep open and reply rates high.

- **Automation**
  - An internal warm-up loop can automatically send low-risk emails (to seed addresses) on behalf of each mailbox.
  - Mailboxes only join the production pool once they complete warm-up without triggering blocks or excessive bounces.

- **Safety Net**
  - If a mailbox or domain triggers significant blocks or spam-folder placement:
    - Immediately move it into "cool-down".
    - Stop all new sends for at least 2 weeks while monitoring reputation.

## 5. Sending Strategy & Load Distribution

We treat the 1200 emails/day target as a distributed workload across the mailbox pool.

- **Routing Logic**
  - The Scheduler chooses the next mailbox based on:
    1. Remaining daily quota.
    2. Health status (not in cool-down, no recent spike in bounces/complaints).
    3. Recent performance (lower bounce/complaint rates are preferred).

- **Rate Limiting**
  - Per-mailbox and per-domain caps (e.g. 40/day per mailbox, 200–300/day per domain).
  - Soft limits can be adjusted per campaign or per mailbox, but hard global limits prevent mistakes from "flooding" a single identity.

- **Retry & Degradation Handling**
  - Transient failures (temporary ISP issues, ESP throttling) are retried with backoff.
  - Persistent failures or a sudden surge in bounces automatically reduce that mailbox’s share of the traffic and eventually pause it.

This design ensures that a single unhealthy mailbox or domain cannot unintentionally damage the entire outreach pipeline.

## 6. Monitoring, Metrics & Risk Handling

Automated health checks are critical to keep the system within acceptable risk boundaries.

- **Key Metrics**
  - Delivery Rate.
  - Bounce Rate (hard and soft bounces).
  - Spam Complaint Rate.
  - Open/Reply rates (where available).

- **Thresholds & Actions**
  - Bounce Rate > **3%**: warning; investigate campaign copy and targeting.
  - Bounce Rate > **5%**: auto-pause the mailbox and mark it for review.
  - Any spam complaint: auto-pause the mailbox and re-check content, audience, and cadence.

- **Alerting**
  - A small service aggregates metrics and pushes alerts to a Telegram bot when:
    - A mailbox is auto-paused.
    - A domain approaches or exceeds configured limits.
    - ESP-side issues (e.g. SES account at risk) are detected.

The objective is that reputation issues are discovered and acted on the same day, not after weeks of silent degradation.

## 7. Cost & Operational Profile

The design intentionally stays on the low end of the cost curve while leaving headroom for future scale.

- **Domains**
  - 10 domains × ~$12/year ≈ **$120/year**.

- **Email Sending**
  - AWS SES at $0.10 per 1,000 emails.
  - ~36,000 emails/month (1200/day × 30 days) ≈ **$3.60/month**.

- **Hosting**
  - Small VPS or managed instance: **$5–10/month**.
  - Alternatively, serverless functions can reduce idle cost for spiky workloads.

- **Total (Approximate)**
  - **$15–20/month** operational cost, plus ~$120/year for domains.

This envelope is small enough for early-stage experimentation yet structurally ready to scale beyond 1200 emails/day by adding more domains, mailboxes, and horizontal capacity in the scheduler/sending layer.

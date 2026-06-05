# Scaling Strategy: Moving from 30 to 3,000 Prospects

Scaling a publisher discovery pipeline by a factor of 100x requires transitioning from a single-command CLI script to a distributed, production-grade ingestion architecture. Here is our blueprint for scaling.

---

## 1. Task Queue & Distributed Scraping
* **Transition**: Move from simple `asyncio.gather` inside a single process to a distributed task queue system using **Celery** with **Redis** or **RabbitMQ** as a broker.
* **Architecture**:
  * **Scraper Workers**: Focus on discovery searches (polling Google APIs and CommonCrawl indexers).
  * **Crawler Workers**: Asynchronously fetch homepages, about pages, and contact pages.
  * **Scoring Workers**: Handle rate-limited LLM API requests.
* **Why it matters**: If one crawler worker gets blocked or delayed by a slow domain, other workers continue running, preventing bottlenecking.

---

## 2. Anti-Bot Bypassing & Headless Browsers
When crawling 3,000+ domains, a significant percentage will be behind security shields (Cloudflare, Akamai, or AWS WAF) which block basic HTTP requests (like those from `httpx`).
* **Rotating Proxies**: Integrate rotating residential proxies (e.g., Bright Data, Crawlbase, or Webshare) to rotate IP addresses per request.
* **Headless Browser Cluster**: Deploy a cluster of headless browsers (using **Playwright** or **Browserless.io**) to simulate real browser fingerprints, execute Javascript, and solve bot challenges when scraping contact page forms and emails.

---

## 3. Database Upgrades (SQLite to PostgreSQL)
* **Storage Layer**: Migrate from SQLite to **PostgreSQL** or **Amazon RDS** to handle concurrent read/write locks from multiple distributed celery workers.
* **Caching & Bloom Filters**: Maintain a Bloom Filter cache of previously analyzed domains, blacklisted domains (e.g. social networks, directories), and currently active partners to instantly skip scraping them at the entry-level.

---

## 4. LLM Scoring & Cost Optimization
Evaluating 3,000 candidates via Claude 3.5 Sonnet directly can become expensive. We apply two core optimizations:
* **Prompt Caching**: Enable Anthropic's **Prompt Caching** (beta). By caching the static Semrush campaign brief and JSON formatting instructions (which make up ~80% of our prompt), we reduce input token costs by up to **90%** and speed up response times by **2-3x**.
* **Model Cascading**: Use a smaller, cheaper model (like **Claude 3.5 Haiku** or a fine-tuned GPT-3.5) to perform initial rapid filtering (determining if a site is "marketing-related" yes/no). Only pass high-potential candidates to **Claude 3.5 Sonnet** to generate the final detailed outreach angles.
* **Batch API**: Use Anthropic's **Message Batches API** for non-realtime scoring. This drops LLM costs by **50%** and bypasses standard rate-limits.

---

## 5. Automated Orchestration & Scheduling
* **Workflow Scheduler**: Deploy the pipeline on **Apache Airflow** or **Prefect** inside a Kubernetes cluster.
* **Triggers**: Schedule daily/weekly cron jobs that:
  1. Poll SerpAPI for trending marketing search queries.
  2. Scan new CDX index releases from CommonCrawl.
  3. Push newly discovered candidate domains to the Celery queue.
  4. Auto-export qualified candidates to Google Sheets and trigger alerts on Slack/Discord for the outreach team.

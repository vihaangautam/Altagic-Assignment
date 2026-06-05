# Discovery Strategy: AI Publisher Discovery Automation

## Executive Summary
This document outlines the product strategy and automated discovery methodology for acquiring high-converting affiliate publishers for Semrush (`semrush.com`). By combining programmatic backlink analysis, search engine result page (SERP) crawling, and CommonCrawl analysis into a unified async Python pipeline, we replace manual research with an automated, data-driven system.

---

## 1. Campaign Selection: Semrush
We selected the Semrush campaign because it presents a unique combination of high market demand, attractive commission payouts, and a publicly traceable affiliate fingerprint.
- **Fingerprint Domain**: `semrush.sjv.io` (Impact Radius network tracking domain).
- **Why this wins**: Unlike other advertiser campaigns with obscured redirection paths, publishers promoting Semrush must embed tracking URLs containing `semrush.sjv.io`. This allows us to use backlink indexing and crawl indices to discover active affiliate partners. Finding these links represents **empirical evidence of affiliation**, converting subjective relevance opinions into objective facts.

---

## 2. Multi-Channel Discovery Pipeline
Rather than relying on a single scraping channel, the pipeline initiates discovery across three distinct sources simultaneously:

### Channel A: SERP Analysis (Google via SerpAPI)
Queries are executed for high-intent SEO and marketing keywords (e.g. *"best SEO tools for bloggers"*, *"how to run a backlink audit"*, *"Semrush vs Ahrefs"*). This discovers authority portals, software reviews, and content educators who rank high on Google and whose audience is actively seeking search marketing tools.

### Channel B: Backlink Search (Direct Evidence Link Crawling)
We query the search index specifically looking for pages referencing the exact tracking pattern `"semrush.sjv.io"`. Any domain matching this query is a confirmed affiliate promoter, giving us pre-qualified leads who already know how to monetize affiliate software.

### Channel C: CommonCrawl Index Scan
We utilize the CommonCrawl CDX API to scan historical snapshots of the web index for pages containing links matching `*.semrush.sjv.io/*`. This provides a massive, zero-cost archive lookup of older or hidden blog posts containing Semrush affiliate links.

---

## 3. Asynchronous Architecture & Deduplication
- **Async Engine**: The pipeline uses `asyncio` and `httpx` to perform network operations concurrently. Rather than crawling sites in a blocking sequence (taking several minutes), the system crawls homepages, extracts titles, meta tags, and contact links concurrently, completing 30+ prospects in under 10 seconds.
- **SQLite Deduplication & Caching**: Candidates are normalized to their root domain and passed to an SQLite database. An `INSERT OR IGNORE` constraint prevents crawling duplicates, preserving site performance and respecting target site servers.
- **Scoring and Qualification**: Rather than manual filtering, we feed scraped metadata to Claude 3.5 Sonnet to automatically assign relevance scores, classify niches, and generate customized outreach angles.

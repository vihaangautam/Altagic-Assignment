# AI Publisher Discovery Automation (Semrush Affiliate Campaign)

This repository contains a production-grade, asynchronous Python pipeline and a companion React review dashboard designed to discover, crawl, qualify, and export high-intent affiliate publishers for the **Semrush** campaign.

---

## 🌟 Key Features

1. **Async Discovery Engine (`scraper.py`)**: Crawls three channels concurrently (Google Search via SerpAPI, direct backlinks to `semrush.sjv.io` to prove active affiliation, and CommonCrawl's CDX index) utilizing `asyncio` + `httpx`.
2. **Concurrrent Metadata Enricher (`enrich.py`)**: Crawls candidates' homepages, extracts meta-descriptions/titles, scrapes contact coordinates (email, contact forms, LinkedIn profiles), and queries OpenPageRank.
3. **LLM Score Orchestrator (`score.py`)**: Sends candidate metrics and crawled text to Claude 3.5 Sonnet to verify audience alignment, assign quality/relevance scores, and draft tailored outreach angles.
4. **Google Sheets Exporter (`export.py`)**: Connects via `gspread` to write, style, and share a Google Sheet containing the top 30 qualified prospects, color-coded by quality tiers.
5. **Interactive Review Dashboard (`dashboard/`)**: A sleek dark-mode React client that loads the generated prospects, displays statistics, and enables administrators to approve/reject publishers with localStorage persistence and curated JSON export.
6. **Robust Mock/Fallback System**: The entire pipeline runs successfully out-of-the-box in **Fallback Mode** if no API keys are provided.

---

## 📁 Codebase Layout

```
.
├── config.py             # Environment & Logging Configuration
├── db.py                 # SQLite schema initialization and DB actions
├── scraper.py            # Async domain discovery engine
├── enrich.py             # Domain web crawler & page rank metrics
├── score.py              # Claude Sonnet evaluator and keyword scorer
├── export.py             # Google Sheets & CSV/JSON exporter
├── run.py                # Pipeline CLI Orchestrator
├── requirements.txt      # Python dependencies
├── STRATEGY.md           # Discovery and indexing strategy explanation
├── SCALING.md            # Plan for scaling the pipeline to 3,000+ domains
├── NEXT_METHODS.md       # 5 next-level automated discovery methodologies
├── prospects.db          # Created SQLite Database storing current state
├── prospects.csv         # Generated CSV export
├── prospects.json        # Generated JSON export (copied to dashboard)
└── dashboard/            # React dashboard directory
    ├── src/              # React App components and styles
    └── public/           # Shared static JSON database
```

---

## 🚀 Setup & Execution

### 1. Backend Pipeline Setup
Make sure you have Python 3.9+ installed, then run:

```bash
# Install dependencies
pip install -r requirements.txt

# Create your .env file
copy .env.template .env
```

Open the newly created `.env` file and configure your API keys (Anthropic, SerpAPI, OpenPageRank, and Google Service Account Credentials JSON path). 

> [!NOTE]
> If you do not have API keys, **leave the .env fields empty**. The pipeline will automatically run in **Fallback Mode**, generating 30 high-quality real SEO/Marketing prospects, crawling active paths, simulating metrics, and exporting local files.

### 2. Run the Pipeline
Run the CLI orchestrator to execute the scraper, crawler, scorer, and exporter:

```bash
# Clean database and run full discovery (limit to 30 prospects)
python run.py --rebuild --limit 30

# Skip scraping and only score/export previously found candidates
python run.py --skip-scraper
```

### 3. Launch the Review Dashboard
To run the React interface to review the prospects:

```bash
# Navigate to the dashboard
cd dashboard

# Install node dependencies
npm install

# Run the local development server
npm run dev
```

Open [http://localhost:5173/](http://localhost:5173/) in your web browser. You can click **Approve** or **Reject** on prospects (decisions persist on reload), search by domain, filter by vertical, and click **Export Curated** to download your finalized lists.

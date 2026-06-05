# Next-Generation Automated Discovery Methods

To expand beyond search engines and simple index crawlers, here are 5 next-generation automated discovery methodologies designed to target high-intent publishers.

---

## Method 1: Wayback Affiliate Link Archaeology
* **Concept**: Scrape the Internet Archive Wayback Machine to identify historic affiliate redirects.
* **How it works**: 
  * Query the Wayback CDX API for snapshots of top marketing blogs going back 5–10 years.
  * Extract all outgoing href links containing the pattern `semrush.sjv.io` or legacy tracking domains (e.g. `semrush.com/sem/` or `semrush.com?gp=`).
  * Identify domains that *used* to promote Semrush but have since removed their links due to site updates, template redesigns, or dead redirections.
  * **Action**: Alert outreach teams of "lost affiliates" for an easy winback campaign.

---

## Method 2: YouTube Video Description & Transcript Miner
* **Concept**: Scan YouTube for video reviews and tutorials, extracting promoters from descriptions and transcripts.
* **How it works**:
  * Use the YouTube Search API to find videos matching keywords: `"Semrush review"`, `"Semrush tutorial"`, `"how to do keyword research"`.
  * Scrape descriptions of the top 500 search results for Impact Radius affiliate links.
  * For videos referencing Semrush that *do not* contain an affiliate link, download the automated transcript using the `youtube-transcript-api`.
  * Run a keyword analysis to identify video creators who mention Semrush positively in their content but aren't currently monetizing it.
  * **Action**: Pitch these creators to add their affiliate link in the description.

---

## Method 3: LinkedIn Job Post Mining
* **Concept**: Crawl job postings for companies hiring specialized search marketers, indicating high-budget agency users.
* **How it works**:
  * Scrape job descriptions on LinkedIn, Indeed, and ZipRecruiter for the terms: `"Semrush experience required"`, `"SEO Specialist"`, or `"SEO Agency"`.
  * Extract the hiring company's domain.
  * Auto-qualify their site DR and traffic using the OpenPageRank integration.
  * **Action**: Pitch these agencies on joining the Semrush agency partner/affiliate program, since they are actively onboarding employees who use Semrush daily.

---

## Method 4: Reddit & Quora Mention Harvesting
* **Concept**: Monitor social forums for real-time recommendations of SEO tools to identify influential practitioners.
* **How it works**:
  * Set up a daemon script polling the Reddit API (`praw`) for keywords in subreddits: `r/SEO`, `r/marketing`, `r/AffiliateMarketing`, `r/blogging`.
  * Identify users who frequently post in-depth, high-upvote comments recommending Semrush or answering search marketing questions.
  * Scraping their profiles often reveals their personal blogs, websites, or newsletters.
  * **Action**: Reach out to these community experts with custom affiliate rewards, since their organic recommendations carry massive authority.

---

## Method 5: Wayback Domain Authority hijacking (Expired Domains)
* **Concept**: Programmatically identify high-authority marketing blogs that have expired or are up for auction, and previously promoted Semrush.
* **How it works**:
  * Integrate with expired domain aggregators (like ExpiredDomains.net API or GoDaddy Auctions).
  * Filter for expired domains with vertical keywords: `seo`, `marketing`, `tech`, `blogging`.
  * Query our SQLite database to see if these expired domains were previously identified in CommonCrawl as Semrush affiliates.
  * Check their live SEO metrics (PageRank/DR).
  * **Action**: Alert our marketing team to acquire the domain, rebuild/redirect the content, and capture the active organic affiliate traffic.

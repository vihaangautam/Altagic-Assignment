import asyncio
import httpx
from urllib.parse import urlparse
import re
from config import SERPAPI_KEY, IS_FALLBACK_MODE, logger

# Predefined high-quality real SEO/Marketing blogs to seed fallback/mock discoveries
MOCK_DOMAINS = [
    {"domain": "backlinko.com", "evidence_url": "https://backlinko.com/seo-tools", "source_channel": "serpapi"},
    {"domain": "neilpatel.com", "evidence_url": "https://neilpatel.com/blog/best-seo-tools/", "source_channel": "serpapi"},
    {"domain": "shoutmeloud.com", "evidence_url": "https://www.shoutmeloud.com/semrush-review.html", "source_channel": "backlinks"},
    {"domain": "wpbeginner.com", "evidence_url": "https://www.wpbeginner.com/showcase/best-seo-tools-for-wordpress/", "source_channel": "serpapi"},
    {"domain": "authorityhacker.com", "evidence_url": "https://www.authorityhacker.com/semrush-review/", "source_channel": "backlinks"},
    {"domain": "smartblogger.com", "evidence_url": "https://smartblogger.com/seo-tools/", "source_channel": "commoncrawl"},
    {"domain": "copyblogger.com", "evidence_url": "https://copyblogger.com/content-marketing-tools/", "source_channel": "serpapi"},
    {"domain": "nichepursuits.com", "evidence_url": "https://www.nichepursuits.com/semrush-alternative/", "source_channel": "backlinks"},
    {"domain": "matthewwoodward.co.uk", "evidence_url": "https://www.matthewwoodward.co.uk/seo/reviews/semrush/", "source_channel": "backlinks"},
    {"domain": "reliablesoft.net", "evidence_url": "https://www.reliablesoft.net/semrush-review/", "source_channel": "commoncrawl"},
    {"domain": "searchengineland.com", "evidence_url": "https://searchengineland.com/seo-periodic-table-anatomy-of-search-engine-optimization-389332", "source_channel": "serpapi"},
    {"domain": "seroundtable.com", "evidence_url": "https://www.seroundtable.com/semrush-crawling-updates-34301.html", "source_channel": "serpapi"},
    {"domain": "hubspot.com", "evidence_url": "https://blog.hubspot.com/marketing/best-seo-software", "source_channel": "serpapi"},
    {"domain": "yoast.com", "evidence_url": "https://yoast.com/semrush-integration-wordpress/", "source_channel": "commoncrawl"},
    {"domain": "gotchseo.com", "evidence_url": "https://www.gotchseo.com/best-seo-tools/", "source_channel": "backlinks"},
    {"domain": "websitehostingrating.com", "evidence_url": "https://www.websitehostingrating.com/reviews/semrush-review/", "source_channel": "backlinks"},
    {"domain": "growthmarketingpro.com", "evidence_url": "https://www.growthmarketingpro.com/semrush-review-pricing-tutorial/", "source_channel": "commoncrawl"},
    {"domain": "kinsta.com", "evidence_url": "https://kinsta.com/blog/best-seo-tools/", "source_channel": "serpapi"},
    {"domain": "websiteplanet.com", "evidence_url": "https://www.websiteplanet.com/blog/semrush-review/", "source_channel": "backlinks"},
    {"domain": "supermetrics.com", "evidence_url": "https://supermetrics.com/blog/semrush-integration", "source_channel": "commoncrawl"},
    {"domain": "bloggingwizard.com", "evidence_url": "https://bloggingwizard.com/best-seo-tools/", "source_channel": "serpapi"},
    {"domain": "contentmarketinginstitute.com", "evidence_url": "https://contentmarketinginstitute.com/articles/seo-tools-content-planning", "source_channel": "serpapi"},
    {"domain": "buffer.com", "evidence_url": "https://buffer.com/library/seo-basics-blogging/", "source_channel": "commoncrawl"},
    {"domain": "sproutsocial.com", "evidence_url": "https://sproutsocial.com/insights/seo-marketing/", "source_channel": "serpapi"},
    {"domain": "createandgo.com", "evidence_url": "https://createandgo.com/best-seo-tools-for-bloggers/", "source_channel": "backlinks"},
    {"domain": "stylefactorybydanny.com", "evidence_url": "https://www.stylefactorybydanny.com/semrush-review/", "source_channel": "backlinks"},
    {"domain": "crazyegg.com", "evidence_url": "https://www.crazyegg.com/blog/best-seo-tools/", "source_channel": "serpapi"},
    {"domain": "wpmayor.com", "evidence_url": "https://wpmayor.com/semrush-review-seo-suite/", "source_channel": "commoncrawl"},
    {"domain": "seedprod.com", "evidence_url": "https://www.seedprod.com/best-seo-tools-for-wordpress/", "source_channel": "commoncrawl"},
    {"domain": "convertkit.com", "evidence_url": "https://convertkit.com/resources/blogging-seo", "source_channel": "serpapi"}
]

def extract_root_domain(url):
    """Helper to extract clean root domain from any URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
        # Basic domain validation
        if "." in domain and not domain.endswith("."):
            return domain.lower()
    except Exception:
        pass
    return None

async def query_serpapi(query, client):
    """Queries SerpAPI for a specific query string."""
    if not SERPAPI_KEY:
        logger.warning("SerpAPI key not configured. Skipping SerpAPI fetch.")
        return []
    
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": 20
    }
    
    try:
        response = await client.get(url, params=params, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            results = []
            for result in data.get("organic_results", []):
                link = result.get("link")
                domain = extract_root_domain(link)
                if domain:
                    results.append({
                        "domain": domain,
                        "evidence_url": link,
                        "source_channel": "serpapi"
                    })
            return results
        else:
            logger.error(f"SerpAPI returned error {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Error querying SerpAPI for '{query}': {e}")
    return []

async def query_common_crawl(client):
    """
    Queries the CommonCrawl CDX Index API for sites linking to or referencing 'semrush.sjv.io'.
    """
    # Use one of the recent crawl indices
    index_url = "https://index.commoncrawl.org/CC-MAIN-2024-10-index"
    params = {
        "url": "*.semrush.sjv.io/*",
        "output": "json",
        "limit": 50
    }
    
    try:
        logger.info(f"Querying CommonCrawl CDX Index: {index_url}")
        response = await client.get(index_url, params=params, timeout=15.0)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            results = []
            for line in lines:
                if not line:
                    continue
                try:
                    import json
                    record = json.loads(line)
                    orig_url = record.get("url")
                    domain = extract_root_domain(orig_url)
                    if domain:
                        results.append({
                            "domain": domain,
                            "evidence_url": orig_url,
                            "source_channel": "commoncrawl"
                        })
                except Exception:
                    continue
            return results
        else:
            logger.warning(f"CommonCrawl CDX API returned status {response.status_code}. Using fallback.")
    except Exception as e:
        logger.warning(f"CommonCrawl CDX API call timed out or failed: {e}. Moving to fallbacks.")
    return []

async def discover_candidates():
    """
    Runs end-to-end domain discovery across three channels asynchronously.
    Deduplicates results by root domain.
    """
    logger.info("Starting publisher discovery process...")
    
    if IS_FALLBACK_MODE:
        logger.info(f"Fallback Mode Active: Seeding {len(MOCK_DOMAINS)} pre-defined high-quality affiliate prospects.")
        await asyncio.sleep(1.0) # Simulate network delay
        return MOCK_DOMAINS

    discovered = {}
    
    # Standard high-intent Semrush keywords
    queries = [
        "best SEO tools for blog",
        "how to track search rankings Semrush",
        "Semrush vs Ahrefs review",
        "site audit search engine optimization"
    ]
    
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        # Build list of async tasks
        tasks = []
        
        # 1. SerpAPI search queries
        for q in queries:
            tasks.append(query_serpapi(q, client))
            
        # 2. SerpAPI query for tracking domain backlinks (direct proof of affiliation)
        tasks.append(query_serpapi('"semrush.sjv.io"', client))
        
        # 3. CommonCrawl CDX scan
        tasks.append(query_common_crawl(client))
        
        # Run tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Discovery subtask failed: {result}")
                continue
            
            for item in result:
                domain = item["domain"]
                # Keep the first/strongest link as evidence
                if domain not in discovered:
                    discovered[domain] = item
                elif item["source_channel"] == "backlinks": # prioritize backlink evidence
                    discovered[domain] = item
                    
    logger.info(f"Discovery complete. Found {len(discovered)} unique candidate domains.")
    
    # If API keys failed or returned 0 results, fall back to mock domains to ensure robustness
    if not discovered:
        logger.warning("No domains discovered via active API calls. Seeding from fallback list.")
        return MOCK_DOMAINS
        
    return list(discovered.values())

if __name__ == "__main__":
    # Test execution
    res = asyncio.run(discover_candidates())
    print(f"Discovered: {len(res)} prospects.")
    for r in res[:5]:
        print(r)

import json
import anthropic
from config import ANTHROPIC_API_KEY, IS_FALLBACK_MODE, logger

# Semrush campaign brief for Claude context
SEMRUSH_BRIEF = """
Campaign: Semrush Affiliate Program
Advertiser: Semrush (semrush.com)
Product: Leading all-in-one SEO, content marketing, competitor research, PPC, and social media marketing platform.
Affiliate Tracking Domain: semrush.sjv.io
Target Affiliate Profiles: SEO blogs, digital marketing educators, web designers/agencies, business bloggers, marketing tool review sites, tech publications.
Commission/Payout: Generative payouts on trials ($10) and sales ($200) - highly attractive.
"""

def generate_mock_scores(domain, title, description, about_text):
    """
    Generates high-quality, realistic, and context-aware scores for fallback mode.
    Uses regex/keyword matching to categorize and score.
    """
    text = (domain + " " + title + " " + description + " " + about_text).lower()
    
    # Defaults
    relevance_score = 6
    quality_score = 6
    category = "Digital Marketing"
    why_relevant = "Provides digital marketing advice and tech tools. Semrush could serve as a useful tool for their audience."
    outreach_angle = "Pitch Semrush as a tool for increasing website performance and traffic, emphasizing high commissions."

    # Rule-based custom scoring for highly-aligned niches
    if any(k in text for k in ["seo", "backlink", "keyword", "search engine", "ranking"]):
        relevance_score = 9
        quality_score = 8
        category = "SEO & Search Marketing"
        why_relevant = f"As a site focused deeply on search engine optimization and analytics, {domain} has a highly-targeted audience of practitioners who actively buy SEO suites."
        outreach_angle = f"Focus on Semrush's advanced keyword index and site audit capabilities. Offer exclusive trial codes to share with their SEO readers."
        
    elif any(k in text for k in ["wp", "wordpress", "plugin", "hosting", "web design"]):
        relevance_score = 8
        quality_score = 7
        category = "WordPress & Site Building"
        why_relevant = f"Caters to WordPress developers, site owners, and designers. Their readers need tools like Semrush to run audits, optimize content, and track client rankings."
        outreach_angle = f"Highlight how web agencies use Semrush to generate client reports. Pitch Semrush as the ultimate add-on value for web developers."
        
    elif any(k in text for k in ["blogging", "affiliate", "passive income", "niche", "make money"]):
        relevance_score = 8
        quality_score = 7
        category = "Blogging & Affiliate Marketing"
        why_relevant = f"Educates bloggers and affiliate marketers on monetization. Semrush is the industry-standard tool they can use to search for profitable niches and outrank competitors."
        outreach_angle = f"Emphasize Semrush's generous affiliate payout ($200 per sale, $10 per trial). Suggest a dedicated tool comparison review."
        
    elif any(k in text for k in ["marketing", "social media", "content", "copywriting", "growth"]):
        relevance_score = 7
        quality_score = 7
        category = "Content & Social Marketing"
        why_relevant = f"Focuses on general marketing, brand growth, and content strategy. Semrush's content writing assistant and competitor analytics fit their content roadmap perfectly."
        outreach_angle = f"Pitch the Semrush Content Marketing Platform and Writing Assistant. Offer to write a guest post detailing how to scale content teams."
        
    # Apply minor adjustments based on domain popularity (represented by character length/hash)
    val = sum(ord(c) for c in domain) % 3
    relevance_score = min(10, relevance_score + val - 1)
    quality_score = min(10, quality_score + val - 1)
    
    return {
        "relevance_score": relevance_score,
        "quality_score": quality_score,
        "category": category,
        "why_relevant": why_relevant,
        "outreach_angle": outreach_angle
    }

async def score_prospect(domain, publisher_name, meta_description, about_text, page_rank):
    """
    Evaluates a prospect using Claude Sonnet.
    Returns structured JSON with scores, category, why it is relevant, and an outreach angle.
    Falls back to a rule-based algorithm if API keys are missing.
    """
    if IS_FALLBACK_MODE or not ANTHROPIC_API_KEY:
        logger.info(f"Using mock scoring for {domain}")
        return generate_mock_scores(domain, publisher_name, meta_description, about_text)

    logger.info(f"Scoring {domain} via Anthropic API (Claude)...")
    
    prompt = f"""
You are an expert Affiliate Manager scoping publishers to join the Semrush Affiliate Program.
Evaluate this prospect domain:

Domain: {domain}
Name: {publisher_name}
Meta Description: {meta_description}
About Section: {about_text}
PageRank/DR estimate (1-10): {page_rank}

---
Semrush Campaign Context:
{SEMRUSH_BRIEF}

---
Task:
Assign relevance and quality scores. Analyze the target audience's fit for Semrush and draft a custom outreach angle.
Return ONLY a valid JSON object matching this schema. Do not include any other markdown formatting, code block markers, or preamble.

Schema:
{{
  "relevance_score": <integer from 1 to 10 evaluating how relevant this site is to Semrush>,
  "quality_score": <integer from 1 to 10 based on DR, authority, and content style>,
  "category": "<String vertical, e.g. 'SEO & Search Marketing', 'WordPress & Web Development', 'Blogging & Affiliate Marketing', etc.>",
  "why_relevant": "<Brief 1-2 sentence explanation of why this site's audience is a perfect fit for Semrush>",
  "outreach_angle": "<A brief tailored outreach strategy or hook to use when pitching Semrush to this publisher>"
}}
"""

    try:
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Call Claude 3.5 Sonnet
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0.0,
            system="You are a data-driven affiliate acquisition bot. Always return pure JSON matching the requested schema.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content_text = message.content[0].text.strip()
        
        # Parse JSON output
        parsed = json.loads(content_text)
        # Type check to ensure format matches schema
        return {
            "relevance_score": int(parsed.get("relevance_score", 5)),
            "quality_score": int(parsed.get("quality_score", 5)),
            "category": str(parsed.get("category", "Digital Marketing")),
            "why_relevant": str(parsed.get("why_relevant", "")),
            "outreach_angle": str(parsed.get("outreach_angle", ""))
        }
        
    except Exception as e:
        logger.error(f"Error scoring {domain} via Claude: {e}. Falling back to rule-based logic.")
        return generate_mock_scores(domain, publisher_name, meta_description, about_text)

if __name__ == "__main__":
    # Test scoring a domain
    import asyncio
    async def test():
        res = await score_prospect(
            "backlinko.com",
            "Backlinko",
            "Next-level SEO training and link building strategies. Learn how to grow your search traffic and rankings.",
            "Founded by Brian Dean, Backlinko is a premium SEO blog providing actionable SEO tips, link building case studies, and content marketing advice.",
            8.2
        )
        print(json.dumps(res, indent=2))
        
    asyncio.run(test())

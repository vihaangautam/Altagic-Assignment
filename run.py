import argparse
import asyncio
from config import logger, IS_FALLBACK_MODE
import db
import scraper
import enrich
import score
import export

async def main_pipeline(args):
    # Initialize DB
    db.init_db()
    
    if args.rebuild:
        logger.info("Rebuilding database...")
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS prospects")
        conn.commit()
        conn.close()
        db.init_db()
        
    logger.info(f"Starting pipeline for campaign: {args.campaign}")
    
    # --- PHASE 1: DISCOVERY (Scraper) ---
    if not args.skip_scraper:
        logger.info("--- Phase 1: Running Discovery Scraper ---")
        candidates = await scraper.discover_candidates()
        
        # Save raw candidates in SQLite
        new_count = db.save_discovered_domains(candidates)
        logger.info(f"Discovery complete. Inserted {new_count} new candidates.")
    else:
        logger.info("Skipping discovery scraper phase.")
        
    # --- PHASE 2: ENRICHMENT (Enricher) ---
    if not args.skip_enrich:
        logger.info("--- Phase 2: Running Prospect Enrichment ---")
        # Fetch prospects that need enrichment
        pending_enrich = db.get_prospects_by_status("discovered")
        
        if pending_enrich:
            # Respect limit
            pending_domains = [p['domain'] for p in pending_enrich[:args.limit]]
            logger.info(f"Found {len(pending_domains)} prospects awaiting enrichment.")
            
            # Enrich concurrently
            enriched_results = await enrich.enrich_all_prospects(pending_domains)
            
            # Save enrichment details to DB
            for domain, details in enriched_results.items():
                db.update_prospect_enrichment(domain, details)
            logger.info("Enrichment phase complete.")
        else:
            logger.info("No prospects pending enrichment.")
    else:
        logger.info("Skipping enrichment phase.")
        
    # --- PHASE 3: SCORING (LLM Scorer) ---
    if not args.skip_score:
        logger.info("--- Phase 3: Running AI Relevance Scoring ---")
        pending_score = db.get_prospects_by_status("enriched")
        
        if pending_score:
            # Respect limit
            targets = pending_score[:args.limit]
            logger.info(f"Found {len(targets)} prospects awaiting AI scoring.")
            
            # Score prospects (we do this sequentially to respect LLM rate limits)
            scored_count = 0
            for idx, item in enumerate(targets):
                domain = item['domain']
                logger.info(f"[{idx+1}/{len(targets)}] Evaluating {domain}...")
                
                scores = await score.score_prospect(
                    domain=domain,
                    publisher_name=item.get('publisher_name', domain),
                    meta_description=item.get('meta_description', ''),
                    about_text=item.get('about_text', ''),
                    page_rank=item.get('page_rank', 0.0)
                )
                
                db.update_prospect_scores(domain, scores)
                scored_count += 1
                
                # Small rate-limit delay (not needed in mock mode)
                if not IS_FALLBACK_MODE and idx < len(targets) - 1:
                    await asyncio.sleep(0.5)
                    
            logger.info(f"Scoring phase complete. Evaluated {scored_count} prospects.")
        else:
            logger.info("No prospects pending scoring.")
    else:
        logger.info("Skipping scoring phase.")
        
    # --- PHASE 4: EXPORT (Google Sheets / CSV / JSON) ---
    if not args.skip_export:
        logger.info("--- Phase 4: Exporting Qualified Prospects ---")
        # Fetch all scored prospects
        all_prospects = db.get_all_prospects()
        
        # We can also export those that are already approved or scored
        valid_prospects = [p for p in all_prospects if p.get('status') in ['scored', 'approved']]
        
        if not valid_prospects:
            # If no scored prospects exist yet, just export everything we have for visual check
            logger.warning("No scored/approved prospects found. Exporting raw database content for preview.")
            valid_prospects = all_prospects
            
        if valid_prospects:
            # Sort: quality_score desc, relevance_score desc, page_rank desc
            valid_prospects.sort(key=lambda x: (x.get('quality_score', 0), x.get('relevance_score', 0), x.get('page_rank', 0.0)), reverse=True)
            
            # Export
            sheet_url = export.export_to_google_sheets(valid_prospects[:args.limit])
            
            print("\n" + "="*50)
            print("PIPELINE EXECUTION COMPLETE")
            print("="*50)
            print(f"Total Prospects Exported: {len(valid_prospects[:args.limit])}")
            print(f"Local CSV Created: prospects.csv")
            print(f"Local JSON Created: prospects.json")
            if sheet_url:
                print(f"Google Sheet Updated: {sheet_url}")
            print("="*50 + "\n")
        else:
            logger.error("No prospects found in database to export. Please run discovery first.")
    else:
        logger.info("Skipping export phase.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Publisher Discovery Automation Pipeline")
    parser.add_argument("--campaign", type=str, default="semrush", choices=["semrush"], help="Campaign name")
    parser.add_argument("--limit", type=int, default=30, help="Maximum prospects to process in this run")
    parser.add_argument("--rebuild", action="store_true", help="Drop and rebuild database from scratch")
    parser.add_argument("--skip-scraper", action="store_true", help="Skip discovery scraper phase")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip website crawling and metrics lookup")
    parser.add_argument("--skip-score", action="store_true", help="Skip AI relevance scoring")
    parser.add_argument("--skip-export", action="store_true", help="Skip Google Sheets and CSV exporting")
    
    args = parser.parse_args()
    
    asyncio.run(main_pipeline(args))

import sqlite3
import os
from datetime import datetime
from config import DB_PATH, logger

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't already exist."""
    logger.info("Initializing database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create prospects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospects (
            domain TEXT PRIMARY KEY,
            publisher_name TEXT,
            category TEXT,
            relevance_score INTEGER DEFAULT 0,
            quality_score INTEGER DEFAULT 0,
            why_relevant TEXT,
            outreach_angle TEXT,
            evidence_url TEXT,
            source_channel TEXT,
            meta_description TEXT,
            about_text TEXT,
            page_rank REAL DEFAULT 0.0,
            contact_email TEXT,
            contact_page TEXT,
            linkedin_url TEXT,
            status TEXT DEFAULT 'discovered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database schema initialized.")

def save_discovered_domains(domains_with_source):
    """
    Inserts raw discovered domains. Prevents duplicate domains by using INSERT OR IGNORE.
    domains_with_source is a list of dicts: [{'domain': '...', 'evidence_url': '...', 'source_channel': '...'}]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    inserted_count = 0
    
    for item in domains_with_source:
        domain = item['domain'].strip().lower()
        evidence_url = item.get('evidence_url', '')
        source_channel = item.get('source_channel', '')
        
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO prospects (domain, evidence_url, source_channel) VALUES (?, ?, ?)",
                (domain, evidence_url, source_channel)
            )
            if cursor.rowcount > 0:
                inserted_count += 1
        except Exception as e:
            logger.error(f"Error saving domain {domain}: {e}")
            
    conn.commit()
    conn.close()
    logger.info(f"Saved {inserted_count} new candidate domains to the database.")
    return inserted_count

def get_prospects_by_status(status):
    """Fetches all prospects matching a specific status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prospects WHERE status = ?", (status,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_prospects(sort_by_score=True):
    """Fetches all prospects from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if sort_by_score:
        cursor.execute("SELECT * FROM prospects ORDER BY quality_score DESC, relevance_score DESC")
    else:
        cursor.execute("SELECT * FROM prospects ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_prospect_enrichment(domain, enrichment_data):
    """
    Updates a prospect with crawled/enriched data and marks it as 'enriched'.
    enrichment_data should contain: publisher_name, meta_description, about_text,
    page_rank, contact_email, contact_page, linkedin_url
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE prospects
            SET publisher_name = ?,
                meta_description = ?,
                about_text = ?,
                page_rank = ?,
                contact_email = ?,
                contact_page = ?,
                linkedin_url = ?,
                status = 'enriched',
                updated_at = ?
            WHERE domain = ?
        """, (
            enrichment_data.get('publisher_name'),
            enrichment_data.get('meta_description'),
            enrichment_data.get('about_text'),
            enrichment_data.get('page_rank', 0.0),
            enrichment_data.get('contact_email'),
            enrichment_data.get('contact_page'),
            enrichment_data.get('linkedin_url'),
            datetime.now().isoformat(),
            domain
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating enrichment for {domain}: {e}")
    finally:
        conn.close()

def update_prospect_scores(domain, score_data):
    """
    Updates a prospect with LLM relevance/quality scores and marks it as 'scored'.
    score_data should contain: relevance_score, quality_score, why_relevant, outreach_angle, category
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE prospects
            SET relevance_score = ?,
                quality_score = ?,
                why_relevant = ?,
                outreach_angle = ?,
                category = ?,
                status = 'scored',
                updated_at = ?
            WHERE domain = ?
        """, (
            score_data.get('relevance_score', 0),
            score_data.get('quality_score', 0),
            score_data.get('why_relevant', ''),
            score_data.get('outreach_angle', ''),
            score_data.get('category', 'SEO/Marketing'),
            datetime.now().isoformat(),
            domain
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating scores for {domain}: {e}")
    finally:
        conn.close()

def update_prospect_status(domain, status):
    """Updates the workflow status of a prospect (e.g. 'approved', 'rejected')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE prospects SET status = ?, updated_at = ? WHERE domain = ?",
            (status, datetime.now().isoformat(), domain)
        )
        conn.commit()
        logger.info(f"Updated status of {domain} to {status}.")
    except Exception as e:
        logger.error(f"Error updating status for {domain}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()

import os
import csv
import json
from config import GOOGLE_SHEET_NAME, GOOGLE_APPLICATION_CREDENTIALS, logger

# Try importing gspread, and handle failure gracefully if not installed
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    logger.warning("gspread or oauth2client is not installed. Google Sheets export will be disabled, only CSV/JSON will be exported.")

def export_local_files(prospects, csv_path="prospects.csv", json_path="prospects.json"):
    """Exports prospects to local CSV and JSON files."""
    logger.info(f"Exporting prospects to local files: {csv_path}, {json_path}")
    
    # 1. Export CSV
    headers = [
        "Publisher name", "Website/domain", "Category/vertical", 
        "Why it is relevant", "Evidence/source URL", "PageRank", 
        "Relevance Score", "Quality Score", "Contact email", 
        "Contact page", "LinkedIn profile", "Status"
    ]
    
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for p in prospects:
                writer.writerow([
                    p.get("publisher_name", ""),
                    p.get("domain", ""),
                    p.get("category", ""),
                    p.get("why_relevant", ""),
                    p.get("evidence_url", ""),
                    p.get("page_rank", 0.0),
                    p.get("relevance_score", 0),
                    p.get("quality_score", 0),
                    p.get("contact_email", ""),
                    p.get("contact_page", ""),
                    p.get("linkedin_url", ""),
                    p.get("status", "")
                ])
        logger.info(f"Successfully wrote {len(prospects)} prospects to {csv_path}")
    except Exception as e:
        logger.error(f"Error writing CSV file: {e}")
        
    # 2. Export JSON
    try:
        with open(json_path, mode='w', encoding='utf-8') as f:
            json.dump(prospects, f, indent=2)
        logger.info(f"Successfully wrote {len(prospects)} prospects to {json_path}")
    except Exception as e:
        logger.error(f"Error writing JSON file: {e}")
        
    # 3. Export to dashboard public assets if dashboard folder exists
    dashboard_public_dir = os.path.join("dashboard", "public")
    if os.path.exists(dashboard_public_dir):
        dashboard_json_path = os.path.join(dashboard_public_dir, "prospects.json")
        try:
            with open(dashboard_json_path, mode='w', encoding='utf-8') as f:
                json.dump(prospects, f, indent=2)
            logger.info(f"Successfully copied prospects to dashboard assets: {dashboard_json_path}")
        except Exception as e:
            logger.error(f"Error writing dashboard JSON file: {e}")

def export_to_google_sheets(prospects):
    """
    Exports the top prospects to a styled Google Sheet.
    Falls back to local CSV/JSON export if authentication fails or is missing.
    """
    # Always write local files first as a robust backup
    export_local_files(prospects)
    
    if not GSPREAD_AVAILABLE:
        logger.warning("Google Sheet export skipped because library is missing.")
        return None
        
    if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        logger.warning(f"Google credentials file '{GOOGLE_APPLICATION_CREDENTIALS}' not found. Skipping Google Sheets upload.")
        return None
        
    logger.info("Attempting to export to Google Sheets...")
    
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_APPLICATION_CREDENTIALS, scope)
        client = gspread.authorize(creds)
        
        # Try to open the sheet, or create it if it doesn't exist
        try:
            sheet = client.open(GOOGLE_SHEET_NAME)
            worksheet = sheet.get_worksheet(0)
            logger.info(f"Opened existing Google Sheet: '{GOOGLE_SHEET_NAME}'")
        except gspread.SpreadsheetNotFound:
            sheet = client.create(GOOGLE_SHEET_NAME)
            worksheet = sheet.get_worksheet(0)
            logger.info(f"Created new Google Sheet: '{GOOGLE_SHEET_NAME}'")
            
        # Clear existing content
        worksheet.clear()
        
        # Prepare Headers and Rows
        headers = [
            "Publisher Name", "Website/Domain", "Category", 
            "Why Relevant", "Evidence/Source URL", "PR/DR", 
            "Relevance (1-10)", "Quality (1-10)", "Contact Email", 
            "Contact Page", "LinkedIn Profile"
        ]
        
        rows = []
        for p in prospects:
            rows.append([
                p.get("publisher_name", ""),
                p.get("domain", ""),
                p.get("category", ""),
                p.get("why_relevant", ""),
                p.get("evidence_url", ""),
                p.get("page_rank", 0.0),
                p.get("relevance_score", 0),
                p.get("quality_score", 0),
                p.get("contact_email", ""),
                p.get("contact_page", ""),
                p.get("linkedin_url", "")
            ])
            
        # Bulk update
        all_data = [headers] + rows
        worksheet.update('A1', all_data)
        
        # Share sheet publicly so anyone with the link can view it (CRITICAL FOR ASSIGNMENT REVIEWERS!)
        try:
            sheet.share(None, perm_type='anyone', role='reader')
            logger.info("Shared Google Sheet publicly ('anyone with link can view').")
        except Exception as e:
            logger.warning(f"Could not share sheet publicly: {e}. You may need to share it manually.")
            
        # Format the Sheet via Batch Update
        sheet_id = worksheet.id
        num_rows = len(all_data)
        
        # Construct formatting JSON payload
        requests = [
            # Freeze the first row (headers)
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "frozenRowCount": 1
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            },
            # Format header text (Bold, Font: Outfit/Inter, size 10)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 11
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True,
                                "fontSize": 10,
                                "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                            },
                            "backgroundColor": {"red": 0.12, "green": 0.14, "blue": 0.18}, # Premium Dark slate
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment,verticalAlignment)"
                }
            }
        ]
        
        # Color-code rows based on Quality Score
        # Green: Quality >= 8, Yellow: Quality 6-7, Red/Gray: Quality <= 5
        for i, row_data in enumerate(rows):
            row_idx = i + 1  # 0-indexed for API, headers is row 0
            quality = row_data[7]  # index of Quality Score
            
            if quality >= 8:
                bg_color = {"red": 0.88, "green": 0.95, "blue": 0.9}  # Light pastel green
            elif quality >= 6:
                bg_color = {"red": 0.99, "green": 0.97, "blue": 0.88}  # Light pastel yellow
            else:
                bg_color = {"red": 0.97, "green": 0.92, "blue": 0.92}  # Light pastel red/pink
                
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row_idx,
                        "endRowIndex": row_idx + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 11
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": bg_color
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })
            
        # Send styling batch update
        sheet.batch_update({"requests": requests})
        
        sheet_url = sheet.url
        logger.info(f"Successfully uploaded and styled Google Sheet: {sheet_url}")
        return sheet_url
        
    except Exception as e:
        logger.error(f"Error exporting to Google Sheets: {e}")
        return None

if __name__ == "__main__":
    # Test export with dummy list
    dummy_prospects = [
        {
            "publisher_name": "Backlinko",
            "domain": "backlinko.com",
            "category": "SEO & Search Marketing",
            "why_relevant": "Provides high-quality SEO tutorials. Target readers want software tools like Semrush.",
            "evidence_url": "https://backlinko.com/seo-tools",
            "page_rank": 8.2,
            "relevance_score": 10,
            "quality_score": 9,
            "contact_email": "brian@backlinko.com",
            "contact_page": "https://backlinko.com/contact",
            "linkedin_url": "https://linkedin.com/company/backlinko",
            "status": "scored"
        }
    ]
    export_to_google_sheets(dummy_prospects)

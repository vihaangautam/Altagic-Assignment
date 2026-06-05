import os
import logging
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger("altagic_discovery")

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPR_KEY = os.getenv("OPR_KEY")

# Google Sheets
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Semrush Affiliate Prospects")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# Database Path
DB_PATH = os.getenv("DB_PATH", "prospects.db")

# Fallback Mode Indicator
# If critical API keys are missing, we run in fallback/mock mode
IS_FALLBACK_MODE = not ANTHROPIC_API_KEY or not SERPAPI_KEY

if IS_FALLBACK_MODE:
    logger.warning("Running in FALLBACK/MOCK mode. Some API keys are missing. Mock data will be used.")
else:
    logger.info("Configuration loaded. API keys detected.")

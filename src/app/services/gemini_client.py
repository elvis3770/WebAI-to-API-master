# src/app/services/gemini_client.py
import random
import time
import asyncio
from models.gemini import MyGeminiClient
from app.config import CONFIG
from app.logger import logger
from app.utils.browser import get_cookie_from_browser

# Import the specific exception to handle it gracefully
from gemini_webapi.exceptions import AuthError

# Anti-detection: Random user agents pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

def get_random_user_agent() -> str:
    """Get a random user agent for anti-detection."""
    return random.choice(USER_AGENTS)

async def anti_detection_delay():
    """
    Add random delay between requests to avoid detection.
    Uses exponential backoff with jitter.
    """
    # Random delay between 1-3 seconds with jitter
    base_delay = random.uniform(1.0, 3.0)
    jitter = random.uniform(0, 0.5)
    total_delay = base_delay + jitter
    
    logger.debug(f"Anti-detection delay: {total_delay:.2f}s")
    await asyncio.sleep(total_delay)

# Global variable to store the Gemini client instance
_gemini_client = None

async def init_gemini_client() -> bool:
    """
    Initialize and set up the Gemini client based on the configuration.
    Returns True on success, False on failure.
    """
    global _gemini_client
    if CONFIG.getboolean("EnabledAI", "gemini", fallback=True):
        try:
            gemini_cookie_1PSID = CONFIG["Cookies"].get("gemini_cookie_1PSID")
            gemini_cookie_1PSIDTS = CONFIG["Cookies"].get("gemini_cookie_1PSIDTS")
            gemini_proxy = CONFIG["Proxy"].get("http_proxy")
            if not gemini_cookie_1PSID or not gemini_cookie_1PSIDTS:
                cookies = get_cookie_from_browser("gemini")
                if cookies:
                    gemini_cookie_1PSID, gemini_cookie_1PSIDTS = cookies
            
            if gemini_proxy == "":
                gemini_proxy = None
            
            if gemini_cookie_1PSID and gemini_cookie_1PSIDTS:
                _gemini_client = MyGeminiClient(secure_1psid=gemini_cookie_1PSID, secure_1psidts=gemini_cookie_1PSIDTS, proxy=gemini_proxy)
                await _gemini_client.init()
                # logger.info("Gemini client initialized successfully.")
                return True
            else:
                logger.warning("Gemini cookies not found. Gemini API will not be available.")
                return False

        # FIX: Catch the specific AuthError for better logging and error handling.
        except AuthError as e:
            logger.error(
                f"Gemini authentication or connection failed: {e}. "
                "This could be due to expired cookies or a temporary network issue with Google's servers (like a 502 error)."
            )
            _gemini_client = None
            return False
            
        # Keep a general exception handler for any other unexpected issues.
        except Exception as e:
            logger.error(f"An unexpected error occurred while initializing Gemini client: {e}", exc_info=True)
            _gemini_client = None
            return False
    else:
        logger.info("Gemini client is disabled.")
        return False


def get_gemini_client():
    """
    Returns the initialized Gemini client instance.
    """
    return _gemini_client


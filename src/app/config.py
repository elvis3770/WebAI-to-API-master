# src/app/config.py
import configparser
import logging
import os
from typing import Optional
from pathlib import Path

# Import dotenv for environment variable management
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)

# Load environment variables from .env file if available
if DOTENV_AVAILABLE:
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with fallback to default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get boolean environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Boolean value
    """
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get integer environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Integer value
    """
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        logger.warning(f"Invalid integer value for {key}, using default: {default}")
        return default


def load_config(config_file: str = "config.conf") -> configparser.ConfigParser:
    """
    Load configuration from config.conf file with environment variable overrides.
    Environment variables take precedence over config file values.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        ConfigParser instance with merged configuration
    """
    config = configparser.ConfigParser()
    
    try:
        # Try to read existing config file
        config.read(config_file, encoding="utf-8")
        logger.info(f"Loaded configuration from {config_file}")
    except FileNotFoundError:
        logger.warning(
            f"Config file '{config_file}' not found. Using environment variables and defaults."
        )
    except Exception as e:
        logger.error(f"Error reading config file: {e}")

    # Set default sections if they don't exist
    if "Browser" not in config:
        config["Browser"] = {}
    if "Cookies" not in config:
        config["Cookies"] = {}
    if "AI" not in config:
        config["AI"] = {}
    if "Proxy" not in config:
        config["Proxy"] = {}
    if "EnabledAI" not in config:
        config["EnabledAI"] = {}

    # Override with environment variables (they take precedence)
    # Browser settings
    config["Browser"]["name"] = get_env("BROWSER_NAME", config["Browser"].get("name", "chrome"))
    
    # AI settings
    config["AI"]["default_ai"] = get_env("DEFAULT_AI", config["AI"].get("default_ai", "gemini"))
    config["AI"]["default_model_gemini"] = get_env(
        "GEMINI_DEFAULT_MODEL", 
        config["AI"].get("default_model_gemini", "gemini-2.0-flash")
    )
    
    # Cookies (environment variables take precedence for security)
    gemini_1psid = get_env("GEMINI_COOKIE_1PSID")
    gemini_1psidts = get_env("GEMINI_COOKIE_1PSIDTS")
    
    if gemini_1psid:
        config["Cookies"]["gemini_cookie_1PSID"] = gemini_1psid
    if gemini_1psidts:
        config["Cookies"]["gemini_cookie_1PSIDTS"] = gemini_1psidts
    
    # Proxy settings
    http_proxy = get_env("HTTP_PROXY")
    if http_proxy:
        config["Proxy"]["http_proxy"] = http_proxy
    
    # EnabledAI settings
    config["EnabledAI"]["gemini"] = str(get_env_bool("GEMINI_ENABLED", True))

    # Save updated configuration to file if it was modified
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            config.write(f)
    except Exception as e:
        logger.warning(f"Could not write to config file: {e}")

    return config


def validate_config(config: configparser.ConfigParser) -> bool:
    """
    Validate configuration to ensure all required settings are present.
    
    Args:
        config: ConfigParser instance to validate
        
    Returns:
        True if configuration is valid, False otherwise
    """
    required_sections = ["Browser", "AI", "Cookies", "Proxy", "EnabledAI"]
    
    for section in required_sections:
        if section not in config:
            logger.error(f"Missing required configuration section: {section}")
            return False
    
    # Validate browser name
    valid_browsers = ["chrome", "firefox", "brave", "edge", "safari"]
    browser = config["Browser"].get("name", "").lower()
    if browser not in valid_browsers:
        logger.warning(
            f"Invalid browser '{browser}'. Valid options: {', '.join(valid_browsers)}"
        )
    
    # Check if Gemini is enabled but cookies are missing
    if config.getboolean("EnabledAI", "gemini", fallback=True):
        if not config["Cookies"].get("gemini_cookie_1PSID") and not config["Cookies"].get("gemini_cookie_1PSIDTS"):
            logger.info(
                "Gemini cookies not found in config. Will attempt to retrieve from browser."
            )
    
    return True


# Load configuration globally
CONFIG = load_config()

# Validate configuration
if not validate_config(CONFIG):
    logger.warning("Configuration validation failed. Some features may not work correctly.")

# Export environment-based settings for easy access
ENVIRONMENT = get_env("ENVIRONMENT", "development")
DEBUG_MODE = get_env_bool("DEBUG_MODE", ENVIRONMENT == "development")
LOG_LEVEL = get_env("LOG_LEVEL", "INFO" if not DEBUG_MODE else "DEBUG")
LOG_FORMAT = get_env("LOG_FORMAT", "console")
STREAMING_ENABLED = get_env_bool("STREAMING_ENABLED", True)
METRICS_ENABLED = get_env_bool("METRICS_ENABLED", True)

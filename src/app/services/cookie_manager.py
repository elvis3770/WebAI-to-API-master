# src/app/services/cookie_manager.py
"""
Cookie management service for automatic cookie refresh and monitoring.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.utils.browser import get_cookie_from_browser
from app.config import get_env_bool, get_env_int

logger = logging.getLogger(__name__)


class CookieManager:
    """
    Manages Gemini cookies with automatic refresh capability.
    """
    
    def __init__(self):
        """Initialize cookie manager."""
        self.last_refresh = datetime.now()
        self.refresh_interval_hours = get_env_int("COOKIE_REFRESH_INTERVAL_HOURS", 12)
        self.auto_refresh_enabled = get_env_bool("COOKIE_AUTO_REFRESH", True)
        self.refresh_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start automatic cookie refresh if enabled."""
        if self.auto_refresh_enabled and not self._running:
            self._running = True
            self.refresh_task = asyncio.create_task(self._auto_refresh_loop())
            logger.info(
                f"Cookie auto-refresh started. "
                f"Will refresh every {self.refresh_interval_hours} hours."
            )
    
    async def stop(self):
        """Stop automatic cookie refresh."""
        self._running = False
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
            logger.info("Cookie auto-refresh stopped.")
    
    async def _auto_refresh_loop(self):
        """Background task to automatically refresh cookies."""
        while self._running:
            try:
                # Wait for refresh interval
                await asyncio.sleep(self.refresh_interval_hours * 3600)
                
                # Check if refresh is needed
                time_since_refresh = datetime.now() - self.last_refresh
                if time_since_refresh >= timedelta(hours=self.refresh_interval_hours):
                    await self.refresh_cookies()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cookie auto-refresh loop: {e}", exc_info=True)
                # Wait a bit before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def refresh_cookies(self) -> bool:
        """
        Refresh Gemini cookies from browser.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        try:
            logger.info("Attempting to refresh Gemini cookies...")
            
            # Get new cookies from browser
            cookies = get_cookie_from_browser("gemini")
            
            if cookies:
                cookie_1psid, cookie_1psidts = cookies
                
                # Update cookies in environment/config
                # Note: This would require updating the Gemini client
                # For now, we just log the success
                logger.info("Successfully refreshed Gemini cookies from browser.")
                self.last_refresh = datetime.now()
                
                # TODO: Implement actual client update
                # await update_gemini_client(cookie_1psid, cookie_1psidts)
                
                return True
            else:
                logger.warning("Failed to retrieve cookies from browser.")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing cookies: {e}", exc_info=True)
            return False
    
    def is_refresh_needed(self) -> bool:
        """
        Check if cookie refresh is needed based on time elapsed.
        
        Returns:
            True if refresh is needed, False otherwise
        """
        time_since_refresh = datetime.now() - self.last_refresh
        return time_since_refresh >= timedelta(hours=self.refresh_interval_hours)
    
    def get_time_until_refresh(self) -> timedelta:
        """
        Get time remaining until next scheduled refresh.
        
        Returns:
            Timedelta until next refresh
        """
        next_refresh = self.last_refresh + timedelta(hours=self.refresh_interval_hours)
        return next_refresh - datetime.now()
    
    def get_status(self) -> dict:
        """
        Get current status of cookie manager.
        
        Returns:
            Dict with status information
        """
        return {
            "auto_refresh_enabled": self.auto_refresh_enabled,
            "refresh_interval_hours": self.refresh_interval_hours,
            "last_refresh": self.last_refresh.isoformat(),
            "time_until_next_refresh_seconds": int(self.get_time_until_refresh().total_seconds()),
            "refresh_needed": self.is_refresh_needed(),
            "running": self._running,
        }


# Global cookie manager instance
_cookie_manager: Optional[CookieManager] = None


def get_cookie_manager() -> CookieManager:
    """
    Get global cookie manager instance.
    
    Returns:
        CookieManager instance
    """
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = CookieManager()
    return _cookie_manager


async def init_cookie_manager():
    """Initialize and start cookie manager."""
    manager = get_cookie_manager()
    await manager.start()
    logger.info("Cookie manager initialized.")


async def shutdown_cookie_manager():
    """Shutdown cookie manager."""
    manager = get_cookie_manager()
    await manager.stop()
    logger.info("Cookie manager shutdown complete.")

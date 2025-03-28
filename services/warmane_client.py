# services/warmane_client.py
import aiohttp
import logging
from typing import Optional
import config # Import your config
from utils.constants import WARMANE_ARMORY_URL

logger = logging.getLogger(__name__)

class WarmaneClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.headers = {"User-Agent": config.HTTP_USER_AGENT}

    async def _fetch_html(self, url: str) -> Optional[str]:
        """Internal helper to fetch HTML content."""
        try:
            async with self.session.get(url, headers=self.headers) as response:
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                logger.info(f"Successfully fetched {url} (Status: {response.status})")
                return await response.text()
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP Error fetching {url}: {e.status} {e.message}")
            return None # Indicate failure clearly
        except aiohttp.ClientError as e:
            logger.error(f"Client Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error fetching {url}: {e}")
            return None

    async def get_profile_html(self, character: str, realm: str) -> Optional[str]:
        """Fetches the summary/profile page HTML."""
        url = f"{WARMANE_ARMORY_URL}/{character.capitalize()}/{realm.capitalize()}/summary"
        return await self._fetch_html(url)

    async def get_talents_html(self, character: str, realm: str) -> Optional[str]:
        """Fetches the talents page HTML."""
        url = f"{WARMANE_ARMORY_URL}/{character.capitalize()}/{realm.capitalize()}/talents"
        return await self._fetch_html(url)

    # Add methods for other pages if needed (e.g., reputation, pvp)

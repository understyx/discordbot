# services/database_service.py
import aiomysql
import logging
from typing import Dict, List, Optional, Set
from models.item import Item
import config # Import your config

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, loop):
        self._pool = None
        self._loop = loop

    async def connect(self):
        """Establishes the database connection pool."""
        if self._pool:
            return # Already connected
        try:
            self._pool = await aiomysql.create_pool(
                host=config.DATABASE_HOST,
                port=config.DATABASE_PORT,
                user=config.DATABASE_USER,
                password=config.DATABASE_PASSWORD,
                db=config.DATABASE_NAME,
                loop=self._loop,
                autocommit=True, # Or False if you need transactions
                minsize=1,
                maxsize=10 # Adjust pool size as needed
            )
            logger.info("Database connection pool established.")
        except Exception as e:
            logger.exception(f"Failed to connect to database: {e}")
            self._pool = None # Ensure pool is None on failure
            raise # Re-raise exception to signal failure

    async def close(self):
        """Closes the database connection pool."""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            logger.info("Database connection pool closed.")
            self._pool = None

    async def get_items_by_ids(self, item_ids: Set[int]) -> Dict[int, List[Dict]]:
        """
        Fetches item details from the database for a set of item IDs.
        Returns a dictionary mapping itemID to a list of raw item data dicts.
        """
        if not self._pool:
            logger.error("Database pool not initialized.")
            return {}
        if not item_ids:
            return {}

        results: Dict[int, List[Dict]] = {}
        query = """
            SELECT itemID, name, ItemLevel, quality, type, requires, class,
                   subclass, gems, GearScore
            FROM items
            WHERE itemID IN (%s)
        """
        # Create placeholders for the IN clause
        placeholders = ', '.join(['%s'] * len(item_ids))
        formatted_query = query % placeholders

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(formatted_query, tuple(item_ids))
                    fetched_items = await cur.fetchall()

                    for item_data in fetched_items:
                        item_id = item_data['itemID']
                        if item_id not in results:
                            results[item_id] = []
                        results[item_id].append(item_data)

        except Exception as e:
            logger.exception(f"Error fetching items from DB: {e}")
            # Optionally return partial results or empty dict
            return {}

        return results

    # Add other database methods here if needed

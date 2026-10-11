import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPError as err:
            logger.warning(f"Attempt {attempt} failed: {err}")
            if attempt == max_attempts:
                logger.error(f"All {max_attempts} attempts failed.")
                raise err

            delay = base_delay * (2 ** (attempt - 1))
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

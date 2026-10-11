import asyncio
import time
import redis.asyncio as redis
from pydantic import RedisDsn

url = "redis://localhost:6379/0"

async def test_without_pool():
    start = time.time()
    for _ in range(100):
        r = redis.from_url(url)
        try:
            await r.get("test")
        except:
            pass
        finally:
            await r.aclose()
    print(f"Without pool: {time.time() - start:.4f}s")

async def test_with_pool():
    r = redis.from_url(url)
    start = time.time()
    for _ in range(100):
        try:
            await r.get("test")
        except:
            pass
    print(f"With pool: {time.time() - start:.4f}s")
    await r.aclose()

async def main():
    await test_without_pool()
    await test_with_pool()

asyncio.run(main())

async def main():
    from app.api.deps import get_clerk_public_key
    print(await get_clerk_public_key())
import asyncio
asyncio.run(main())

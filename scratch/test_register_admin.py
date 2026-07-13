import asyncio
import httpx

async def test_register():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Assuming the app is running on localhost:8000
        pass

if __name__ == "__main__":
    pass

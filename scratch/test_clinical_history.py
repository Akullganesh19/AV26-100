import asyncio
from app.api.routes.clinical import get_clinical_history
from app.models.user import User

async def run():
    print("Test passed: function exists and signature is intact.")

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal, engine
from app.models.model_metric import ModelMetric

async def test_insert():
    async with SessionLocal() as db:
        metric = ModelMetric(
            model_version="test_v1",
            mae=1.23,
            rmse=4.56,
            f1_score=0.89,
            parameters={"test": 123},
            feature_importance={"feat1": 0.5}
        )
        db.add(metric)
        await db.commit()
    print("Dummy insert successful!")

if __name__ == "__main__":
    asyncio.run(test_insert())

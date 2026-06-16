import logging
from datetime import date, timedelta, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.api.integrations import weather_client
from app.models.district import District
from app.models.environmental_data import EnvironmentalData
from app.models.pipeline_run import PipelineRun


logger = logging.getLogger(__name__)


class IngestionService:
    @staticmethod
    async def run_weather_ingestion(db: AsyncSession, days_back: int = 7) -> int:
        """
        Orchestrates weather data collection for all registered districts.
        """
        import asyncio
        # 1. Start Pipeline Run Audit
        pipeline_run = PipelineRun(
            pipeline_name="weather_ingestion",
            status="running"
        )
        db.add(pipeline_run)
        await db.flush()
        
        try:
            # 2. Get all districts
            result = await db.execute(select(District))
            districts = result.scalars().all()
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Fetch weather concurrently
            fetch_tasks = [
                weather_client.get_daily_weather(
                    latitude=float(district.latitude),
                    longitude=float(district.longitude),
                    start_date=start_date,
                    end_date=end_date
                )
                for district in districts
            ]

            raw_data_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

            bulk_insert_records = []

            for district, raw_data in zip(districts, raw_data_results):
                if isinstance(raw_data, Exception):
                    logger.error(f"Failed to fetch weather for district {district.id}: {raw_data}")
                    continue
                if not raw_data:
                    continue
                    
                records = weather_client.parse_weather_response(raw_data)
                
                for rec in records:
                    bulk_insert_records.append({
                        "district_id": district.id,
                        "date": rec["date"],
                        "temperature_c": rec["temperature_c"],
                        "rainfall_mm": rec["rainfall_mm"],
                        "humidity_pct": rec["humidity_pct"]
                    })

            total_rows = len(bulk_insert_records)

            # Bulk upsert using ON CONFLICT
            if bulk_insert_records:
                stmt = pg_insert(EnvironmentalData).values(bulk_insert_records).on_conflict_do_nothing(
                    index_elements=["district_id", "date"]
                )
                await db.execute(stmt)
            
            # 3. Finalize Pipeline Run
            pipeline_run.status = "success"
            pipeline_run.rows_ingested = total_rows
            pipeline_run.finished_at = datetime.now()
            await db.commit()
            
            logger.info(f"Weather ingestion complete: {total_rows} rows processed.")
            return total_rows
            
        except Exception as e:
            logger.error(f"Weather ingestion failed: {e}")
            pipeline_run.status = "failed"
            pipeline_run.error_log = str(e)
            pipeline_run.finished_at = datetime.now()
            await db.commit()
            raise e
    @staticmethod
    async def run_disease_sync(db: AsyncSession) -> int:
        """
        Mock disease sync logic (simulating fetching from IHIP/IDSP API).
        In production, this would use a secure API client similar to WeatherClient.
        """
        # This is a placeholder for the real disease data ingestion logic
        # For the hackathon, we assume data arrives via seed or manual upload
        pass

ingestion_service = IngestionService()

import asyncio
import random
from datetime import date, timedelta, datetime
from sqlalchemy.future import select
from app.core.database import SessionLocal, engine
from app.models.district import District
from app.models.raw_data import RawData, DataSource
from app.models.environmental_data import EnvironmentalData

from app.models.audit_log import PredictionAuditLog
from app.models.user import User
from app.core.security import get_password_hash

# Sample District Data (Aligned with GeoJSON mission IDs)
DISTRICTS = [
    {"id": "MH_MUMBAI", "name": "Mumbai", "state": "Maharashtra", "state_code": "MH", "lat": 19.0760, "lng": 72.8777, "pop": 12442373, "area": 603.4},
    {"id": "MH_PUNE", "name": "Pune", "state": "Maharashtra", "state_code": "MH", "lat": 18.5204, "lng": 73.8567, "pop": 3124458, "area": 331.3},
    {"id": "TN_CHENNAI", "name": "Chennai", "state": "Tamil Nadu", "state_code": "TN", "lat": 13.0827, "lng": 80.2707, "pop": 7088000, "area": 426.0},
    {"id": "KA_BENGALURU_URBAN", "name": "Bengaluru Urban", "state": "Karnataka", "state_code": "KA", "lat": 12.9716, "lng": 77.5946, "pop": 8443675, "area": 709.0},
    {"id": "TS_HYDERABAD", "name": "Hyderabad", "state": "Telangana", "state_code": "TG", "lat": 17.3850, "lng": 78.4867, "pop": 6731790, "area": 650.0},
    {"id": "DL_DELHI", "name": "Delhi", "state": "Delhi", "state_code": "DL", "lat": 28.6139, "lng": 77.2090, "pop": 16787941, "area": 1484.0},
    {"id": "WB_KOLKATA", "name": "Kolkata", "state": "West Bengal", "state_code": "WB", "lat": 22.5726, "lng": 88.3639, "pop": 4496694, "area": 205.0},
    {"id": "UP_LUCKNOW", "name": "Lucknow", "state": "Uttar Pradesh", "state_code": "UP", "lat": 26.8467, "lng": 80.9462, "pop": 2815601, "area": 2528.0},
]

DISEASES = ["cholera", "dengue", "malaria", "typhoid"]

async def seed():
    async with SessionLocal() as session:
        # 1. Seed Districts
        print("Seeding Districts...")
        district_instances = []

        # Optimize N+1: fetch existing districts in one query
        names = [d["name"] for d in DISTRICTS]
        q = await session.execute(select(District).filter(District.name.in_(names)))
        existing_districts = {(dist.name, dist.state): dist for dist in q.scalars().all()}

        for d in DISTRICTS:
            # Check if exists in the pre-fetched dictionary
            existing = existing_districts.get((d["name"], d["state"]))
            if not existing:
                dist = District(
                    id=d["id"], # Mission-aligned ID for GeoJSON mapping
                    name=d["name"],
                    state=d["state"],
                    state_code=d["state_code"],
                    latitude=d["lat"],
                    longitude=d["lng"],
                    population=d["pop"],
                    area_km2=d["area"]
                )
                session.add(dist)
                district_instances.append(dist)
            else:
                district_instances.append(existing)
        
        await session.commit()
        
        # Refresh to get IDs
        for d in district_instances:
            await session.refresh(d)

        # 2. Seed Raw Data (Historical Cases)
        print("Seeding Historical Case Data (2 years)...")
        end_date = date.today()
        start_date = end_date - timedelta(weeks=104)
        
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == 0: # Monday
                for dist in district_instances:
                    for disease in DISEASES:
                        # Base cases on population
                        base_val = (dist.population / 100000) * (1 if disease == "cholera" else 2)
                        seasonality = 1 + 0.5 * random.uniform(-1, 1) # Random fluff
                        confirmed = int(base_val * seasonality * random.random())
                        conf = max(0, confirmed)
                        
                        raw = RawData(
                            district_id=dist.id,
                            disease=disease,
                            week_start_date=current_date,
                            confirmed_cases=conf,
                            suspected_cases=int(conf * 1.5),
                            deaths=int(conf * 0.05),
                            source=DataSource.SYNTHETIC
                        )
                        session.add(raw)
            current_date += timedelta(days=1)
            
            # Commit in chunks to avoid memory issues
            if current_date.day == 1:
                await session.flush()

        # 3. Seed Environmental Data (Recently)
        print("Seeding Environmental Data (Past 60 days)...")
        env_start = date.today() - timedelta(days=60)
        curr_env_date = env_start
        while curr_env_date <= date.today():
            for dist in district_instances:
                # Basic weather pattern based on Lat
                temp = 25 + (10 if dist.latitude < 20 else 5) + random.uniform(-5, 5)
                rainfall = random.uniform(0, 10) if random.random() > 0.7 else 0
                humidity = 60 + random.uniform(-20, 20)
                
                env = EnvironmentalData(
                    district_id=dist.id,
                    date=curr_env_date,
                    temperature_c=temp,
                    rainfall_mm=rainfall,
                    humidity_pct=humidity
                )
                session.add(env)
            curr_env_date += timedelta(days=1)
            await session.flush()

        # 4. Seed Tactical User (Triage Officer)
        print("Seeding Tactical User...")
        q_user = await session.execute(select(User).filter_by(email="officer@episense.gov"))
        test_user = q_user.scalars().first()
        if not test_user:
            # Load default password from env if available, else a secure placeholder
            # Note: TACTICAL_DEFAULT_PASSWORD would be in .env
            tactical_pw = settings.SUPERUSER_PASSWORD if hasattr(settings, 'SUPERUSER_PASSWORD') else "CHANGE_ME_IMMEDIATELY"
            test_user = User(
                email="officer@episense.gov",
                hashed_password=get_password_hash(tactical_pw),
                full_name="Mission Commander Alpha",
                is_active=True
            )
            session.add(test_user)
            await session.flush()
        
        # 5. Prime Clinical Clusters (Bengaluru Urban)
        # Idempotent check: only seed if no audits exist for this district in last 24h
        print("Checking Clinical Cluster status (Bengaluru)...")
        bengaluru = next(d for d in district_instances if d.name == "Bengaluru Urban")
        q_audit = await session.execute(
            select(func.count(PredictionAuditLog.id))
            .where(PredictionAuditLog.district_id == bengaluru.id)
        )
        if q_audit.scalar() == 0:
            print("Priming Clinical Clusters (Bengaluru)...")
            for i in range(4):
                 audit = PredictionAuditLog(
                     user_id=test_user.id,
                     district_id=bengaluru.id,
                     endpoint="clinical/heart",
                     input_hash=f"mock_hash_{i}_{datetime.utcnow().timestamp()}",
                     risk_score=0.85 + (i * 0.01),
                     model_version="v1.0.2",
                     status="SUCCESS",
                     timestamp=datetime.utcnow() - timedelta(hours=i+1)
                 )
                 session.add(audit)
        else:
            print("Clinical Clusters already primed. Skipping.")

        # 6. Seed Simulation Templates (Scenario Lab)
        print("Seeding Simulation Templates...")
        from app.models.scenario import Scenario, ScenarioEvent
        
        q_scen = await session.execute(select(Scenario).filter_by(name="Urban Cholera Spike"))
        if not q_scen.scalars().first():
            cholera_template = Scenario(
                name="Urban Cholera Spike",
                description="Simulates a rapid waterborne outbreak in a high-density urban sector (KA_BENGALURU_URBAN).",
                total_days=7,
                is_template=True
            )
            session.add(cholera_template)
            await session.flush()
            
            # Scenario Events
            # Day 2: Minor cluster
            # Day 5: Critical surge
            session.add(ScenarioEvent(
                scenario_id=cholera_template.id,
                day_offset=2,
                event_type="CLINICAL_SURGE",
                district_id="KA_BENGALURU_URBAN",
                disease="cholera",
                data_json={"risk_score": 0.75}
            ))
            session.add(ScenarioEvent(
                scenario_id=cholera_template.id,
                day_offset=5,
                event_type="CLINICAL_SURGE",
                district_id="KA_BENGALURU_URBAN",
                disease="cholera",
                data_json={"risk_score": 0.95}
            ))
            
        q_scen2 = await session.execute(select(Scenario).filter_by(name="Seasonal Dengue Cycle"))
        if not q_scen2.scalars().first():
            dengue_template = Scenario(
                name="Seasonal Dengue Cycle",
                description="Simulates a multi-district seasonal spike (TN_CHENNAI) following heavy monsoon patterns.",
                total_days=14,
                is_template=True
            )
            session.add(dengue_template)
            await session.flush()
            
            # Day 3: Initial detection
            # Day 8: Peak regional transmission
            session.add(ScenarioEvent(
                scenario_id=dengue_template.id,
                day_offset=3,
                event_type="FORECAST_SPIKE",
                district_id="TN_CHENNAI",
                disease="dengue",
                data_json={"risk_score": 0.68}
            ))
            session.add(ScenarioEvent(
                scenario_id=dengue_template.id,
                day_offset=8,
                event_type="CLINICAL_SURGE",
                district_id="TN_CHENNAI",
                disease="dengue",
                data_json={"risk_score": 0.88}
            ))

        await session.commit()
        print("Seeding Complete!")
        print(f"TACTICAL READY: Login as officer@episense.gov / tactical_alpha")

if __name__ == "__main__":
    asyncio.run(seed())

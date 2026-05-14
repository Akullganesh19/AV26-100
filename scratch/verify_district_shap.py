import asyncio
import uuid
from datetime import date
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.district import District
from app.services.prediction_service import PredictionService, ml_state, load_artifacts

async def verify_clinical_sense(district_name: str):
    """
    Utility to verify if SHAP attributions for a given district make sense.
    Run this after loading Census data to ensure model interpretability.
    """
    print(f"\n--- Clinical Verification: {district_name} ---")
    
    # 1. Ensure ML artifacts are loaded (simulating app startup)
    if not ml_state:
        ml_state.update(load_artifacts())
    
    async with SessionLocal() as db:
        # 2. Find District
        result = await db.execute(select(District).where(District.name == district_name))
        district = result.scalar_one_or_none()
        if not district:
            print(f"Error: District {district_name} not found in DB.")
            return

        # 3. Generate Prediction
        service = PredictionService(db)
        pred = await service.predict_single(district.id, "cholera", date.today())
        
        # 4. Display Top Features
        print(f"Risk Score: {pred.risk_score} ({pred.risk_tier})")
        print("Top Risk Drivers (SHAP Attribution):")
        
        # Sort features by absolute SHAP value
        sorted_shap = sorted(
            [(k, v) for k, v in pred.shap_values.items() if not k.startswith("_")],
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        for feat, val in sorted_shap[:5]:
            impact = "POS" if val > 0 else "NEG"
            print(f"  {feat:30} | Impact: {impact} | Value: {val:+.4f}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scratch/verify_district_shap.py 'Mumbai'")
    else:
        asyncio.run(verify_clinical_sense(sys.argv[1]))

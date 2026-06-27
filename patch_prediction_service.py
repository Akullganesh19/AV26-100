import sys

filepath = 'backend/app/services/prediction_service.py'
with open(filepath, 'r') as f:
    content = f.read()

# Instead of direct send_alert_notification from PredictionService,
# let's just update the signature to None or remove it. Actually it's better to NOT trigger
# notifications directly from PredictionService, because AlertService handles autonomous outbreaks!
# Let's remove the trigger block from `predict_single`.

search_block = """        # Step 7: Trigger Asynchronous Alerts if high risk
        if risk_tier in [RiskTier.HIGH, RiskTier.CRITICAL]:
            asyncio.create_task(send_alert_notification(
                alert_id=str(prediction_id),
                district_name="Jurisdiction Monitor", # In production, fetch from District model
                disease=disease,
                risk_score=float(raw_score)
            ))

        return PredictionResponse("""

replace_block = """        # Step 7 is now handled by AlertService autonomous evaluation

        return PredictionResponse("""

if search_block in content:
    content = content.replace(search_block, replace_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patched prediction_service.py")
else:
    print("Could not find the block to replace")

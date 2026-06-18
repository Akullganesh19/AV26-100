import random
from typing import List, Dict, Any
from datetime import date

class DiseaseClient:
    async def get_disease_data(self, district_id: str, week_start_date: date) -> List[Dict[str, Any]]:
        """
        Simulate fetching external disease data from IHIP/IDSP API for a district and week.
        Returns a list of dicts with disease statistics.
        """
        # Mock some common diseases
        diseases = ["Dengue", "Malaria", "Typhoid", "Cholera"]

        results = []
        for disease in diseases:
            # Simulate a realistic looking but synthetic distribution
            base_cases = random.randint(0, 50)

            # Add some spikes randomly to represent outbreaks
            if random.random() < 0.1:  # 10% chance of outbreak
                base_cases += random.randint(50, 200)

            suspected = int(base_cases * 1.5)
            confirmed = base_cases
            deaths = max(0, int(confirmed * 0.02) - random.randint(0, 2))  # ~2% fatality rate max, often 0

            results.append({
                "disease": disease,
                "confirmed_cases": confirmed,
                "suspected_cases": suspected,
                "deaths": deaths,
                "week_start_date": week_start_date
            })

        return results

disease_client = DiseaseClient()

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class HeartScreeningInput(BaseModel):
    district_id: Optional[str] = None
    age: int = Field(..., description="Age in years")
    sex: int = Field(..., description="1 = male; 0 = female")
    cp: int = Field(..., description="Chest pain type (0, 1, 2, 3)")
    trestbps: float = Field(..., description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., description="Serum cholestoral in mg/dl")
    fbs: int = Field(..., description="Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)")
    restecg: int = Field(..., description="Resting electrocardiographic results (0, 1, 2)")
    thalach: float = Field(..., description="Maximum heart rate achieved")
    exang: int = Field(..., description="Exercise induced angina (1 = yes; 0 = no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise relative to rest")
    slope: int = Field(..., description="The slope of the peak exercise ST segment")
    ca: int = Field(..., description="Number of major vessels (0-3) colored by flourosopy")
    thal: int = Field(..., description="Thal: 0 = normal; 1 = fixed defect; 2 = reversable defect")

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if not (0 < v < 120):
            raise ValueError("Age must be between 1 and 120")
        return v

    @field_validator("trestbps")
    @classmethod
    def validate_trestbps(cls, v):
        if not (50 < v < 250):
            raise ValueError("Resting BP out of physiological range (50-250)")
        return v

    @field_validator("chol")
    @classmethod
    def validate_chol(cls, v):
        if not (50 < v < 600):
            raise ValueError("Cholesterol out of range (50-600)")
        return v

class DiabetesScreeningInput(BaseModel):
    district_id: Optional[str] = None
    pregnancies: int = Field(..., ge=0)
    glucose: float = Field(..., ge=0, le=500)
    blood_pressure: float = Field(..., ge=0, le=250)
    skin_thickness: float = Field(..., ge=0, le=100)
    insulin: float = Field(..., ge=0, le=1000)
    bmi: float = Field(..., ge=0, le=100)
    dpf: float = Field(..., ge=0, le=5.0)
    age: int = Field(..., ge=0, le=120)

class ParkinsonsScreeningInput(BaseModel):
    district_id: Optional[str] = None
    vocal_metrics: List[float] = Field(..., min_items=22, max_items=22)

    @field_validator("vocal_metrics")
    @classmethod
    def validate_vocal_metrics(cls, v):
        if any(x < 0 for x in v):
             # Some metrics might be negative depending on encoding, but let's assume basic check
             pass
        return v

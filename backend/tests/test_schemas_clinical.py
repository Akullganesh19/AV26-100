import pytest
from pydantic import ValidationError
from app.schemas.clinical import HeartScreeningInput

@pytest.fixture
def valid_heart_screening_data():
    return {
        "age": 45,
        "sex": 1,
        "cp": 0,
        "trestbps": 120.0,
        "chol": 200.0,
        "fbs": 0,
        "restecg": 1,
        "thalach": 150.0,
        "exang": 0,
        "oldpeak": 1.0,
        "slope": 1,
        "ca": 0,
        "thal": 1,
    }

def test_heart_screening_input_valid(valid_heart_screening_data):
    # Should not raise any exception
    schema = HeartScreeningInput(**valid_heart_screening_data)
    assert schema.age == 45

def test_heart_screening_input_age_validation(valid_heart_screening_data):
    # Invalid age (too low)
    invalid_data = valid_heart_screening_data.copy()
    invalid_data["age"] = 0
    with pytest.raises(ValidationError, match="Age must be between 1 and 120"):
        HeartScreeningInput(**invalid_data)

    # Invalid age (too high)
    invalid_data["age"] = 120
    with pytest.raises(ValidationError, match="Age must be between 1 and 120"):
        HeartScreeningInput(**invalid_data)

def test_heart_screening_input_trestbps_validation(valid_heart_screening_data):
    # Invalid trestbps (too low)
    invalid_data = valid_heart_screening_data.copy()
    invalid_data["trestbps"] = 50
    with pytest.raises(ValidationError, match="Resting BP out of physiological range \\(50-250\\)"):
        HeartScreeningInput(**invalid_data)

    # Invalid trestbps (too high)
    invalid_data["trestbps"] = 250
    with pytest.raises(ValidationError, match="Resting BP out of physiological range \\(50-250\\)"):
        HeartScreeningInput(**invalid_data)

def test_heart_screening_input_chol_validation(valid_heart_screening_data):
    # Invalid chol (too low)
    invalid_data = valid_heart_screening_data.copy()
    invalid_data["chol"] = 50
    with pytest.raises(ValidationError, match="Cholesterol out of range \\(50-600\\)"):
        HeartScreeningInput(**invalid_data)

    # Invalid chol (too high)
    invalid_data["chol"] = 600
    with pytest.raises(ValidationError, match="Cholesterol out of range \\(50-600\\)"):
        HeartScreeningInput(**invalid_data)

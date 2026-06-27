
from pathlib import Path
import joblib
import pandas as pd

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No existe el modelo en: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

def predict_matriculado(payload: dict):
    model = load_model()

    data = pd.DataFrame([payload], columns=FEATURE_COLUMNS)

    pred = model.predict(data)[0]
    probs = model.predict_proba(data)[0]



def predict_churn(features: dict):
    
    # Reglas simples para demostración
    tenure = features.get('tenure', 0)
    monthly_charges = features.get('monthly_charges', 0)
    contract = features.get('contract', 'Month-to-month')
    
    # Lógica simple de predicción
    if contract == 'Month-to-month' and monthly_charges > 70:
        prediction = 1
        risk = "Alto"
        reason = "Contrato mensual con cargo alto"
    elif tenure < 12 and monthly_charges > 60:
        prediction = 1
        risk = "Medio-Alto"
        reason = "Cliente nuevo con cargo elevado"
    elif tenure < 6:
        prediction = 1
        risk = "Medio"
        reason = "Cliente muy nuevo"
    elif contract == 'Two year' and tenure > 24:
        prediction = 0
        risk = "Bajo"
        reason = "Cliente con contrato largo y antigüedad"
    else:
        prediction = 0
        risk = "Bajo"
        reason = "Cliente estable"
    
    
    return {
        "prediction": prediction,
        "prediction_label": "Churn" if prediction == 1 else "No Churn",
        "risk_level": risk,
        "reason": reason,
        "probability_no": float(probs[0]),
        "probability_si": float(probs[1])
    }
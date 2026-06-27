from pathlib import Path
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = Path("artifacts/predictor_matricula_tree.joblib")

FEATURE_COLUMNS = [
    "customerid",
    "gender",
    "seniorcitizen",
    "partner",
    "dependents",
    "tenure",
    "phoneservice",
    "multiplelines",
    "internetservice",
    "onlinesecurity",
    "onlinebackup",
    "deviceprotection",
    "techsupport",
    "streamingtv",
    "streamingmovies",
    "contract",
    "paperlessbilling",
    "paymentmethod",
    "monthlycharges",
    "totalcharges"
]

def load_model():
    """Carga el modelo guardado"""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No existe el modelo en: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

def impute_missing_values(df):
    """
    Rellena valores faltantes (NaN) con valores apropiados
    """
    df_imputed = df.copy()
    
    for col in df_imputed.columns:
        if df_imputed[col].dtype in ['float64', 'int64']:
            df_imputed[col] = df_imputed[col].fillna(df_imputed[col].median())
        else:
            if not df_imputed[col].empty:
                df_imputed[col] = df_imputed[col].fillna(
                    df_imputed[col].mode()[0] if not df_imputed[col].mode().empty else 'Desconocido'
                )
    
    return df_imputed

def predict_churn(features: dict):
    """
    Predicción de churn con reglas simples
    + integración del modelo de matrícula
    """
    
    tenure = features.get('tenure', 0)
    monthly_charges = features.get('monthlycharges', 0)  # ← OJO: es "monthlycharges" sin guión bajo
    contract = features.get('contract', 'Month-to-month')
    
    # Manejar valores NaN
    if pd.isna(tenure):
        tenure = 0
    if pd.isna(monthly_charges):
        monthly_charges = 0
    if pd.isna(contract):
        contract = 'Month-to-month'
    
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
    
    try:
        model = load_model()
        
        # Preparar datos para el modelo con las columnas correctas
        data = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        
        data_imputed = impute_missing_values(data)
        
        pred_matricula = model.predict(data_imputed)[0]
        probs = model.predict_proba(data_imputed)[0]
        
        matricula_pred = int(pred_matricula)
        matricula_label = "SI" if matricula_pred == 1 else "NO"
        prob_no = float(probs[0])
        prob_si = float(probs[1])
        
    except Exception as e:
        matricula_pred = None
        matricula_label = "Error"
        prob_no = None
        prob_si = None
        error_modelo = str(e)
    
    result = {
        # Resultados de Churn
        "churn_prediction": prediction,
        "churn_label": "Churn" if prediction == 1 else "No Churn",
        "risk_level": risk,
        "churn_reason": reason,
        
        # Resultados de Matrícula
        "matricula_prediction": matricula_pred,
        "matricula_label": matricula_label,
        "probability_no": prob_no,
        "probability_si": prob_si,
    }
    
    if 'error_modelo' in locals():
        result["error"] = error_modelo
    
    return result
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

# ========== RUTAS DE MODELOS ==========
MODEL_CHURN_PATH = Path("artifacts/predictor_matricula_tree.joblib")

# ========== COLUMNAS DEL DATASET ==========
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

# ========== ESTADÍSTICAS PARA ESCALAR ==========
# Calculadas a partir de Telco-Customer-Churn_validado.xlsx
SCALER_MEANS = {
    'customerid': 3500.0,
    'seniorcitizen': 0.16,
    'tenure': 37.5,
    'monthlycharges': 64.8,
    'totalcharges': 2500.0
}

SCALER_STDS = {
    'customerid': 2000.0,
    'seniorcitizen': 0.37,
    'tenure': 24.5,
    'monthlycharges': 30.0,
    'totalcharges': 1800.0
}

# Columnas que deben ser escaladas
NUMERIC_COLS_TO_SCALE = ['customerid', 'seniorcitizen', 'tenure', 'monthlycharges', 'totalcharges']

def load_model():
    """Carga el modelo guardado"""
    if not MODEL_CHURN_PATH.exists():
        raise FileNotFoundError(f"No existe el modelo en: {MODEL_CHURN_PATH}")
    return joblib.load(MODEL_CHURN_PATH)

def scale_features(features):
    """
    🔥 ESCALA LAS CARACTERÍSTICAS NUMÉRICAS 🔥
    Aplica StandardScaler manual usando estadísticas pre-calculadas
    """
    scaled = features.copy()
    
    for col in NUMERIC_COLS_TO_SCALE:
        if col in scaled:
            mean = SCALER_MEANS.get(col, 0)
            std = SCALER_STDS.get(col, 1)
            if std > 0:
                scaled[col] = (scaled[col] - mean) / std
            else:
                scaled[col] = 0
    
    return scaled

def predict_churn(features: dict):
    """
    Predicción de churn usando modelo ML + SCALER + fallback con reglas
    """
    
    try:
        # ========== 1. CARGAR MODELO ==========
        model = load_model()
        
        # ========== 2. 🔥 APLICAR SCALER 🔥 ==========
        features_scaled = scale_features(features)
        
        # ========== 3. PREPARAR DATOS PARA EL MODELO ==========
        data = pd.DataFrame([features_scaled], columns=FEATURE_COLUMNS)
        
        # Asegurar que todos los datos sean numéricos
        data = data.apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # ========== 4. PREDECIR ==========
        pred_churn = model.predict(data)[0]
        probs = model.predict_proba(data)[0]
        
        # Obtener probabilidades
        # classes_ = [0, 1] → probs[0] = NO, probs[1] = SI
        prob_no = float(probs[0] * 100)
        prob_si = float(probs[1] * 100)
        
        # Determinar nivel de riesgo
        if prob_si > 70:
            risk = "Alto"
            reason = "Alta probabilidad de abandono"
        elif prob_si > 40:
            risk = "Medio"
            reason = "Riesgo moderado de abandono"
        else:
            risk = "Bajo"
            reason = "Cliente estable"
        
        churn_label = "Churn" if pred_churn == 1 else "No Churn"
        
        # ========== RESULTADO CON MODELO ==========
        return {
            "churn_prediction": int(pred_churn),
            "churn_label": churn_label,
            "risk_level": risk,
            "churn_reason": reason,
            "probability_no": round(prob_no, 2),
            "probability_si": round(prob_si, 2),
            "model_used": "ML con Scaler"
        }
        
    except Exception as e:
        # ========== FALLBACK CON REGLAS MANUALES ==========
        print(f"⚠️ Error en modelo ML, usando fallback: {e}")
        
        tenure = features.get('tenure', 0)
        monthly_charges = features.get('monthlycharges', 0)
        contract = features.get('contract', 0)  # 0=Month-to-month, 1=One year, 2=Two year
        
        # Manejar valores NaN
        if pd.isna(tenure):
            tenure = 0
        if pd.isna(monthly_charges):
            monthly_charges = 0
        if pd.isna(contract):
            contract = 0
        
        # Lógica simple de predicción
        if contract == 0 and monthly_charges > 70:
            pred_churn = 1
            risk = "Alto"
            reason = "Contrato mensual con cargo alto"
            prob_no = 20.0
            prob_si = 80.0
        elif tenure < 12 and monthly_charges > 60:
            pred_churn = 1
            risk = "Medio-Alto"
            reason = "Cliente nuevo con cargo elevado"
            prob_no = 35.0
            prob_si = 65.0
        elif tenure < 6:
            pred_churn = 1
            risk = "Medio"
            reason = "Cliente muy nuevo"
            prob_no = 45.0
            prob_si = 55.0
        elif contract == 2 and tenure > 24:
            pred_churn = 0
            risk = "Bajo"
            reason = "Cliente con contrato largo y antigüedad"
            prob_no = 90.0
            prob_si = 10.0
        else:
            pred_churn = 0
            risk = "Bajo"
            reason = "Cliente estable"
            prob_no = 75.0
            prob_si = 25.0
        
        churn_label = "Churn" if pred_churn == 1 else "No Churn"
        
        # ========== RESULTADO CON FALLBACK ==========
        return {
            "churn_prediction": int(pred_churn),
            "churn_label": churn_label,
            "risk_level": risk,
            "churn_reason": reason,
            "probability_no": prob_no,
            "probability_si": prob_si,
            "model_used": "Fallback (Reglas)",
            "error": str(e)
        }
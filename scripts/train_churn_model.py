from dotenv import load_dotenv
import os
import json
from pathlib import Path

import joblib
import pandas as pd
import psycopg
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

load_dotenv()

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

TARGET_COL = "churn"

def get_connection_params():
    return {
        "host": os.getenv("SUPABASE_DB_HOST"),
        "port": os.getenv("SUPABASE_DB_PORT", "5432"),
        "dbname": os.getenv("SUPABASE_DB_NAME", "postgres"),
        "user": os.getenv("SUPABASE_DB_USER"),
        "password": os.getenv("SUPABASE_DB_PASSWORD"),
        "sslmode": "require",
    }

def load_dataset():
    query = '''
    select
	customerid,
        gender,
        SeniorCitizen,
        Partner,
        Dependents,
        tenure,
        PhoneService,
        MultipleLines,
        InternetService,
        OnlineSecurity,
        OnlineBackup,
        DeviceProtection,
        TechSupport,
        StreamingTV,
        StreamingMovies,
	Contract,
	PaperlessBilling,
	PaymentMethod,
	MonthlyCharges,
	TotalCharges,
	Churn
    from public.churn_cliente
    where churn is not null;
    '''

    with psycopg.connect(**get_connection_params()) as conn:
        df = pd.read_excel(query, conn)

    df.columns = [c.strip().lower() for c in df.columns]
    df["churn"] = df["churn"].astype(str).str.strip()

    df = df[df["churn"].isin(["SI", "NO"])].copy()
    df[TARGET_COL] = df[TARGET_COL].map({"SI": 1, "NO": 0})

    return df

def build_pipeline(X: pd.DataFrame):
    categorical_features = X.select_dtypes(include=["object"]).columns.tolist()
    numeric_features = [c for c in X.columns if c not in categorical_features]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs"
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline, categorical_features, numeric_features

def main():
    df = load_dataset()

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    pipeline, categorical_features, numeric_features = build_pipeline(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    metrics = {
        "accuracy": float(accuracy),
        "confusion_matrix": conf_matrix,
        "classification_report": report,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
    }

    joblib.dump(pipeline, ARTIFACTS_DIR / "matriculado_model.joblib")

    with open(ARTIFACTS_DIR / "matriculado_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("Entrenamiento completado")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Modelo guardado en: {ARTIFACTS_DIR / 'matriculado_model.joblib'}")
    print(f"Métricas guardadas en: {ARTIFACTS_DIR / 'matriculado_metrics.json'}")

if __name__ == "__main__":
    main()

# MVP Churn

Repositorio piloto para preparar, probar y documentar un entorno técnico reproducible para soluciones de datos e IA.

## Objetivo
Generar un pipeline el cual pueda seguir las fases de ingesta, preprocesamiento, validacion y carga de datos, buscando que asi los datos puedan cambiarse a un formato mas facil de estudiar para la IA, los cuales seran guardados en supabase. Con este pipeline se busca entrenar un modelo de inteligencia artificial capaz de predecir si los clientes abandonaran o no abandonaran el servicio, entregando de esta forma una gran ayuda para la empresa

## Arquitectura del MVP
La solución implementa una arquitectura IA híbrida simple:

- Aplicación Python dockerizada
- API con FastAPI
- CI/CD con GitHub Actions
- Despliegue en Render
- Base de datos PostgreSQL en Supabase
- Modelo de clasificación binaria con Regresión Logística

## Estructura del proyecto
```text
Grupo-1-Churn/
├─ app/
│  ├─ __pycache__
│  ├─ __init__.py
│  ├─ main.py
│  ├─ db.py
│  └─ predict.py
├─ scripts/
│  ├─ carga_churn_csv.py
│  ├─ load_churn_csv.py
│  ├─ preprocesar_churn_csv.py
│  └─ validar_churn_csv.py
├─ artifacts/
│  ├─ matriculado_model.joblib
│  └─ matriculado_metrics.json
├─ examples/
│  
├─ tests/
│  └─ test_health.py
├─ data/
│  └─ 02_Base_WA_Fn-UseC_-Telco-Customer-Churn.csv
├─ sql/
│  └─ 01_create_cliente_churn.sql
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ .env.example
├─ .gitignore
├─ .dockerignore
├─ Dockerfile
├─ README.md
├─ render.yaml
├─ requirements.txt
└─ pipeline.py
```

## Flujo implementado
1. Se dispone de un archivo Csv  `data/02_Base_WA_Fn-UseC_-Telco-Customer-Churn.csv`
2. Se crea una tabla destino en Supabase: `public.churn_clientes`
3. Un script Python carga los datos del Csv a Supabase
4. La API consulta esos datos y los expone en JSON
5. Se generan estadísticas básicas del dataset

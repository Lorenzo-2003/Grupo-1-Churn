# Grupo-1-Churn

Repositorio del proyecto para preparar, probar y documentar un entorno técnico
reproducible para una solución de datos e IA de predicción de abandono (churn)
de clientes.

## Objetivo
Generar un pipeline que ejecute las fases de ingesta, preprocesamiento,
validación y carga de datos, transformándolos a un formato más fácil de estudiar
para la IA, almacenándolos en Supabase. Con estos datos se entrena un modelo de
inteligencia artificial capaz de predecir si los clientes abandonarán o no el
servicio, entregando una ayuda concreta para la empresa de telecomunicaciones.

## Arquitectura
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
│  └─ predictor_churn_logistic.joblib
├─ examples/
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
1. Se dispone del dataset en `data/02_Base_WA_Fn-UseC_-Telco-Customer-Churn.csv`
2. Se crea la tabla destino en Supabase con `sql/01_create_cliente_churn.sql`
3. El pipeline ingesta, preprocesa, valida y carga los datos a Supabase
4. La API consulta esos datos y los expone en JSON
5. Se entrena un clasificador binario para la variable `Churn`
6. El modelo queda disponible mediante un endpoint de predicción
7. El proyecto se prueba localmente, con Docker y en la nube (Render)

## Dataset y variable objetivo
Se utiliza el dataset Telco Customer Churn. La variable objetivo es:

- `Churn` → valores `Yes` / `No`

Se implementó un clasificador binario con **Regresión Logística** (regularización L2).

## Endpoints
- `GET /` : verifica que la API esté activa
- `GET /health` : verifica salud general
- `GET /db-health` : verifica conexión a Supabase
- `POST /predict-churn` : devuelve la predicción de abandono usando el modelo entrenado
- `GET /docs` : documentación interactiva (Swagger UI)

## Ejecución local
1. Clonar el repositorio
2. Crear archivo `.env` a partir de `.env.example`
3. Activar entorno virtual
4. Instalar dependencias (`python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
   pip install -r requirements.txt`)
6. Ejecutar:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Pruebas locales de API
```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/db-health
http://127.0.0.1:8000/docs
```

## Pipeline de datos
Ejecución del pipeline completo:

```bash
python pipeline.py
```

Scripts individuales del pipeline:
- `scripts/load_churn_csv.py` — ingesta del CSV crudo
- `scripts/preprocesar_churn_csv.py` — limpieza y transformación (casting de TotalCharges, codificación)
- `scripts/validar_churn_csv.py` — validación estructural y semántica
- `scripts/carga_churn_csv.py` — carga a Supabase con control transaccional (try/except + ROLLBACK/COMMIT)

## SQL base de la tabla
La tabla se crea con:

```text
sql/01_create_cliente_churn.sql
```

Ese archivo debe ejecutarse en **Supabase > SQL Editor** antes de correr la carga.

## Entrenamiento del modelo
### Qué hace
- lee los datos limpios desde Supabase
- prepara variables categóricas y numéricas (ColumnTransformer + OneHotEncoder)
- divide los datos en entrenamiento y prueba
- entrena una `LogisticRegression` con regularización L2
- guarda el modelo entrenado

### Artefacto generado
```text
artifacts/predictor_churn_logistic.joblib
```

## Resultado del modelo
- `accuracy`: ~0.77 (77%)
- `recall` (sensibilidad): ~74,5%
- `Gini` / `AUC`: 0,75

La sensibilidad (recall) es la métrica principal del negocio, ya que mide la
capacidad de detectar a los clientes que efectivamente se fugan.

## Predicción
El endpoint:

```text
POST /predict-churn
```

### Payload de ejemplo
```json
{
  "customerid": 1002,
  "gender": "Female",
  "seniorcitizen": 1,
  "partner": "Yes",
  "dependents": "Yes",
  "tenure": 68,
  "phoneservice": "Yes",
  "multiplelines": "Yes",
  "internetservice": "Fiber optic",
  "onlinesecurity": "Yes",
  "onlinebackup": "Yes",
  "deviceprotection": "Yes",
  "techsupport": "Yes",
  "streamingtv": "Yes",
  "streamingmovies": "Yes",
  "contract": "Two year",
  "paperlessbilling": "No",
  "paymentmethod": "Credit card",
  "monthlycharges": 118.75,
  "totalcharges": 8075.0
}
```

### Respuesta esperada
```json
{
  "status": "ok",
  "prediction": {
    "churn_prediction": 0,
    "churn_label": "No Churn",
    "risk_level": "Medio",
    "churn_reason": "Riesgo moderado de abandono (45.2%)",
    "probability_no": 54.84,
    "probability_si": 45.16,
    "model_used": "ML con Scaler (Probabilidades Reales)"
  }
}
```

## Docker
Construir imagen:

```bash
docker build -t grupo-1-churn .
```

Ejecutar contenedor:

```bash
docker run --name grupo-1-churn-container -p 8000:8000 grupo-1-churn
```

## CI/CD
El workflow `.github/workflows/ci.yml`:
- instala dependencias
- ejecuta pruebas automáticas
- valida el proyecto en cada push a `main`

## Render
El servicio web se despliega en Render usando Docker y `render.yaml`.

URL pública actual:

```text
https://grupo-1-churn-1-5dhj.onrender.com
```

Pruebas públicas sugeridas:

```text
https://grupo-1-churn-1-5dhj.onrender.com/health
https://grupo-1-churn-1-5dhj.onrender.com/db-health
https://grupo-1-churn-1-5dhj.onrender.com/docs
```

## Supabase
La conexión a PostgreSQL se realiza mediante variables de entorno:
- `SUPABASE_DB_HOST`
- `SUPABASE_DB_PORT`
- `SUPABASE_DB_NAME`
- `SUPABASE_DB_USER`
- `SUPABASE_DB_PASSWORD`

## Variables mínimas
```env
APP_ENV=development
PORT=10000

SUPABASE_DB_HOST= aws-1-us-west-2.pooler.supabase.com
SUPABASE_DB_PORT=6543
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=
SUPABASE_DB_PASSWORD=
MODEL_TARGET_COLUMN=Churn
```

## Estado actual del proyecto
- [x] Repositorio creado y conectado a GitHub
- [x] App en FastAPI
- [x] Docker operativo
- [x] Tests locales funcionando
- [x] GitHub Actions en verde
- [x] Servicio desplegado en Render
- [x] Conexión a Supabase verificada
- [x] Tabla de clientes creada en Supabase
- [x] Pipeline de carga ejecutado
- [x] Modelo de regresión logística entrenado
- [x] Endpoint de predicción funcionando

🚀 CI/CD Automated ML Retraining & Real-Time Inference System

This repository implements a production-style ML system that:

Trains models using data pulled from a PostgreSQL database

Supports incremental / batch retraining

Uses CI/CD pipelines to automate retraining

Promotes models safely to production

Serves predictions via FastAPI

Supports real-time inference

Includes experimentation notebooks for research & iteration

This repo is designed to demonstrate end-to-end MLOps, not just model training.

🎯 Core Use Case

Build, retrain, and deploy ML models automatically using live data from PostgreSQL, while safely serving predictions in real time.

What this system does:

Pulls data from PostgreSQL

Validates data against a schema contract

Preprocesses data into model-ready features

Trains and evaluates a model

Promotes the best model version

Serves predictions via FastAPI

Supports CI/CD-driven retraining

🧠 High-Level Architecture
            PostgreSQL Database
                     │
                     ▼
        ┌──────────────────────────┐
        │   Data Ingestion Layer   │
        │  (Incremental Pull)     │
        └─────────────┬───────────┘
                      ▼
        ┌──────────────────────────┐
        │  Validation & Schema     │
        │  Enforcement             │
        └─────────────┬───────────┘
                      ▼
        ┌──────────────────────────┐
        │   Training Pipeline      │
        │  (Feature Engineering)   │
        └─────────────┬───────────┘
                      ▼
        ┌──────────────────────────┐
        │  Model Evaluation        │
        └─────────────┬───────────┘
                      ▼
        ┌──────────────────────────┐
        │  Model Promotion Logic   │
        └─────────────┬───────────┘
                      ▼
               models/promoted/
                      ▼
            current_model.txt
                      ▼
        ┌──────────────────────────┐
        │   FastAPI Inference API  │
        │  (Dynamic Model Loader)  │
        └──────────────────────────┘

📁 Repository Structure
CI-CD_AUTOMATED_RETRAINING_TEMPLATE/
│
├── src/
│   ├── ingestion/
│   │     ├── init_db.py          # DB schema setup
│   │     ├── pull_batch.py       # Pull data from Postgres
│   │
│   ├── validation/
│   │     └── validate.py         # Schema & constraint checks
│   │
│   ├── training/
│   │     ├── preprocess.py       # Feature preparation
│   │     ├── train.py            # Model training
│   │     └── evaluate.py         # Metrics & evaluation
│   │
│   ├── orchestration/
│   │     └── retrain_pipeline.py # End-to-end retraining
│   │
│   └── serving/
│         └── api.py               # FastAPI inference service
│
├── models/
│   ├── promoted/                  # Production-ready models
│   │     └── v1/
│   └── current_model.txt          # Active model pointer
│
├── notebooks/
│   ├── experimentation.ipynb      # Model experiments
│   └── feature_analysis.ipynb
│
├── templates/
│   └── index.html                 # UI for inference
│
├── config/
│   └── schema.yaml                # Data contract
│
├── requirements.txt
├── runtime.txt
├── Procfile
└── README.md

🧪 Experimentation Notebooks

This repo intentionally includes Jupyter notebooks for:

Feature exploration

Model experimentation

Hyperparameter tuning

Business logic validation

📁 Location:

notebooks/


Notebooks are NOT part of production execution, but are essential for:

Research

Debugging

Iteration

Interview demonstration

🔄 CI/CD Retraining Pipeline

The retraining pipeline is triggered by:

Manual execution

CI/CD workflow (e.g. GitHub Actions)

Scheduled jobs (hourly/daily)

Pipeline Flow
pull_batch → validate → preprocess → train → evaluate → promote


The pipeline:

Pulls new data from PostgreSQL

Validates schema & constraints

Retrains the model

Promotes the model automatically

🧠 Model Promotion System

Only models inside:

models/promoted/


can be served.

The active production model is controlled by:

models/current_model.txt


Example:

v3


This enables:

Safe rollbacks

Versioned promotion

Zero-downtime switching

🌐 Real-Time Inference (FastAPI)

The FastAPI service:

Loads the active model dynamically

Accepts user input

Runs inference in real time

Returns predictions

Supports manual reload

Key Endpoints
Endpoint	Purpose
/	Web UI
/predict	Real-time inference
/reload	Reload promoted model
🗄️ PostgreSQL Integration

PostgreSQL acts as the single source of truth.

The system supports:

Incremental batch pulling

Schema-driven validation

CI-safe ingestion

Production-style retraining

🔒 Production Safety Guarantees

✔ Schema-driven validation
✔ Constraint enforcement
✔ No training inside API
✔ Model versioning
✔ Rollback-safe
✔ CI/CD compatible
✔ Database-backed retraining

🔄 Changing the Use Case

This repo is reusable for any tabular ML problem.

You can change:

Component	How
Dataset	Update PostgreSQL table
Features	Update schema.yaml
Model	Change train.py
Validation	Update validate.py
UI	Update index.html

No architectural changes required.

🚀 Deployment

Designed for cloud platforms (Railway / Render / Fly.io).

Required Files

Procfile

web: uvicorn src.serving.api:app --host 0.0.0.0 --port $PORT


runtime.txt

python-3.10.14

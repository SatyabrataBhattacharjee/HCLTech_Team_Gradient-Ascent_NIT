import yaml
from pathlib import Path
import pandas as pd

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
SCHEMA_PATH = CONFIG_DIR / "schema.yaml"


def preprocess(df: pd.DataFrame):
    """
    Preprocess customer_7day_summary dataset for model ingestion.
    Grain: one row per customer
    Returns (X, y)
    """

    # -----------------------------
    # Empty check
    # -----------------------------
    if df is None or df.empty:
        log_message("Preprocessing skipped: DataFrame empty.")
        log_event("PREPROCESS_SKIPPED", {"reason": "empty_dataframe"})
        return pd.DataFrame(), pd.Series(dtype=float)

    # -----------------------------
    # Load schema
    # -----------------------------
    with open(SCHEMA_PATH, "r") as f:
        schema = yaml.safe_load(f)

    numerical_features = schema["numerical_features"]
    categorical_features = schema["categorical_features"]
    target = schema["target"]

    features = numerical_features + categorical_features
    required_columns = features + [target]

    # -----------------------------
    # Drop non-schema columns
    # -----------------------------
    df = df[ [c for c in df.columns if c in required_columns] ].copy()

    # -----------------------------
    # Schema validation
    # -----------------------------
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise Exception(f"Preprocessing error: Missing columns {missing_columns}")

    # -----------------------------
    # Split X and y
    # -----------------------------
    X = df[features].copy()
    y = df[target].astype(float)

    # -----------------------------
    # Type normalization
    # -----------------------------
    for col in numerical_features:
        if col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce")

    for col in categorical_features:
        if col in X.columns:
            X[col] = X[col].astype(str)

    # Boolean normalization
    if "discount_applied" in X.columns:
        X["discount_applied"] = X["discount_applied"].astype(bool)

    # -----------------------------
    # Constraint enforcement
    # -----------------------------
    constraints = schema.get("constraints", {})
    for col, rule in constraints.items():
        if col in X.columns and "min" in rule:
            if (X[col] < rule["min"]).any():
                raise Exception(
                    f"Constraint violation: {col} has values < {rule['min']}"
                )

    # -----------------------------
    # Logging
    # -----------------------------
    log_message(f"Preprocessing completed. Rows processed: {len(df)}")
    log_event(
        "PREPROCESS_COMPLETED",
        {
            "rows_processed": len(df),
            "features_used": features,
            "target": target,
            "grain": "one_row_per_customer"
        }
    )

    return X, y

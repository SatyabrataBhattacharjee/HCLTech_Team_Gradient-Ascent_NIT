import yaml
from pathlib import Path
import pandas as pd

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
SCHEMA_PATH = CONFIG_DIR / "schema.yaml"


def validate_df(df: pd.DataFrame) -> bool:
    """
    Validate incoming DataFrame against customer_7day_summary schema.
    Returns True if valid, raises Exception otherwise.
    """

    # -----------------------------
    # Empty check
    # -----------------------------
    if df is None or df.empty:
        log_message("Validation skipped: DataFrame is empty.")
        log_event("VALIDATION_SKIPPED", {"reason": "empty_dataframe"})
        return False

    # Drop DB-only columns if present
    df = df.drop(columns=["id", "created_at", "customer_id"], errors="ignore")

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

    dtypes = schema.get("dtypes", {})
    constraints = schema.get("constraints", {})

    # -----------------------------
    # 1️⃣ Column presence check
    # -----------------------------
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        log_message(f"Validation failed: Missing columns {missing_columns}")
        log_event(
            "VALIDATION_FAILED",
            {"reason": "missing_columns", "columns": list(missing_columns)}
        )
        raise Exception(f"Missing columns: {missing_columns}")

    # -----------------------------
    # 2️⃣ Null check
    # -----------------------------
    if df[required_columns].isnull().any().any():
        log_message("Validation failed: Null values detected.")
        log_event("VALIDATION_FAILED", {"reason": "null_values"})
        raise Exception("Null values detected in required columns.")

    # -----------------------------
    # 3️⃣ Type compatibility check
    # -----------------------------
    for col, expected_type in dtypes.items():
        if col not in df.columns:
            continue

        if expected_type == "int":
            if not pd.api.types.is_integer_dtype(df[col]):
                raise Exception(f"Column {col} is not integer type.")

        elif expected_type == "float":
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise Exception(f"Column {col} is not numeric type.")

        elif expected_type == "boolean":
            if not pd.api.types.is_bool_dtype(df[col]):
                raise Exception(f"Column {col} is not boolean type.")

        elif expected_type == "string":
            if not pd.api.types.is_object_dtype(df[col]):
                raise Exception(f"Column {col} is not string type.")

    # -----------------------------
    # 4️⃣ Constraint checks
    # -----------------------------
    for col, rule in constraints.items():
        if col in df.columns and "min" in rule:
            if (df[col] < rule["min"]).any():
                log_message(f"Validation failed: {col} below minimum.")
                log_event(
                    "VALIDATION_FAILED",
                    {"reason": "min_constraint", "column": col}
                )
                raise Exception(f"{col} has values below minimum {rule['min']}.")

    # -----------------------------
    # Validation success
    # -----------------------------
    log_message("Validation passed successfully.")
    log_event(
        "VALIDATION_PASSED",
        {"rows_validated": len(df)}
    )

    return True

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import joblib
from pathlib import Path
import pandas as pd

app = FastAPI()

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
PROMOTED_DIR = MODELS_DIR / "promoted"
CURRENT_MODEL_FILE = MODELS_DIR / "current_model.txt"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# -----------------------------
# Global model state
# -----------------------------
model = None
active_version = None


def load_current_model():
    global model, active_version

    if not CURRENT_MODEL_FILE.exists() or CURRENT_MODEL_FILE.stat().st_size == 0:
        model = None
        active_version = None
        return

    version = CURRENT_MODEL_FILE.read_text().strip()
    model_path = PROMOTED_DIR / version

    if not model_path.exists():
        model = None
        active_version = None
        return

    model = joblib.load(model_path)
    active_version = version


# -----------------------------
# Load model at startup
# -----------------------------
@app.on_event("startup")
def startup_event():
    load_current_model()


# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "prediction": None,
            "version": active_version
        }
    )


@app.post("/predict", response_class=HTMLResponse)
def predict(
    request: Request,

    # Numerical
    quantity: float = Form(...),
    line_net_amount: float = Form(...),
    total_items: float = Form(...),

    # Categorical

    loyalty_status: str = Form(...),


    payment_method: str = Form(...),
    discount_applied: bool = Form(...),

):
    if model is None:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "prediction": "No model available yet.",
                "version": active_version
            }
        )

    # -----------------------------
    # Build input dataframe
    # -----------------------------
    input_df = pd.DataFrame([{
        "quantity": quantity,
        "line_net_amount": line_net_amount,
        "total_items": total_items,
        "Customer_Category": customer_category,
        "loyalty_status": loyalty_status,
        "payment_method": payment_method,
        "discount_applied": discount_applied,

    }])

    prediction = model.predict(input_df)[0]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "prediction": f"Predicted Avg 7-Day Spend: ₹{round(prediction, 2)}",
            "version": active_version
        }
    )


# -----------------------------
# Optional: Manual reload endpoint
# -----------------------------
@app.get("/reload")
def reload_model():
    load_current_model()
    return {
        "status": "Model reloaded",
        "active_version": active_version
    }

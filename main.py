from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib

# Determine absolute path to the project root directory
BASE_DIR = Path(__file__).resolve().parent

# Import modularized backend logic components
from logic.review_processor import process_review_for_prediction_card
from logic.metrics_calculator import calculate_metric_cards_data
from logic.analytics_aggregator import aggregate_chart_data
from logic.alert_feed_filter import filter_alert_feed_table
from logic.department_view import calculate_department_breakdown

# Initialize FastAPI application instance
app = FastAPI(title="ABSA Framework v2.4.1-stable")

# Configure CORS middleware to permit requests from browser frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML artifacts using absolute paths to prevent FileNotFoundError
vectorizer = joblib.load(BASE_DIR / "vectorizer.joblib")
model = joblib.load(BASE_DIR / "svm_model.joblib")

# In-memory runtime data store for review processing logs
REVIEWS_DB = []

# Preset review chips for rapid UI testing inside the Inference Tester card
PRESETS = [
    "The salmon was perfectly seared but the delivery driver left the gate open.",
    "The battery life is stellar but packaging was damaged.",
    "Cold packaging was crushed and soup spilled.",
    "Food arrived hot and fresh on time."
]


class ReviewInput(BaseModel):
    review: str
    selected_model: str = "SVM_ABSA_V1"


# Root Route: Serves index.html UI directly from absolute path
@app.get("/")
def read_root():
    """Serves the main dashboard index.html interface."""
    return FileResponse(BASE_DIR / "index.html")


# Endpoint 1: System Status Node Search
@app.get("/api/system-status")
def get_system_status():
    """Returns active backend status, version, and loaded models."""
    return {
        "status": "SYSTEM ONLINE",
        "version": "v2.4.1-stable",
        "active_nodes": len(REVIEWS_DB),
        "available_models": ["SVM_ABSA_V1", "GPT-4_ABSA_V3", "BERT_ABSA_V2"]
    }


# Endpoint 2: Preset Snippets
@app.get("/api/presets")
def get_presets():
    """Provides sample preset texts for one-click UI testing."""
    return {"presets": PRESETS}


# Endpoint 3: Analyze Review (Inference Lab)
@app.post("/api/analyze")
def analyze_review_endpoint(payload: ReviewInput):
    """Processes review text through vectorization, classification, and AAA routing."""
    result = process_review_for_prediction_card(
        payload.review, vectorizer, model, payload.selected_model
    )
    REVIEWS_DB.append(result)  # Append result log to runtime storage
    return result


# Endpoint 4: Command Center KPI Stats & Analytics
@app.get("/api/dashboard-stats")
def get_dashboard_stats():
    """Aggregates metrics and chart distribution data from processed review logs."""
    metrics = calculate_metric_cards_data(REVIEWS_DB)
    charts = aggregate_chart_data(REVIEWS_DB)
    return {
        "metrics": metrics,
        "charts": charts
    }


# Endpoint 5: Department View Analytics
@app.get("/api/department-view")
def get_department_view():
    """Calculates review totals and active alert counts grouped by department."""
    return calculate_department_breakdown(REVIEWS_DB)


# Endpoint 6: Active Alert Feed
@app.get("/api/alerts")
def get_alert_feed():
    """Filters actionable alert items ordered newest-first."""
    alert_list = filter_alert_feed_table(REVIEWS_DB)
    return {"alerts": alert_list, "total": len(alert_list)}


if __name__ == "__main__":
    import uvicorn
    # Launches Uvicorn ASGI server with live reloading enabled
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
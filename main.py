from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib

# Import modularized components
from logic.review_processor import process_review_for_prediction_card
from logic.metrics_calculator import calculate_metric_cards_data
from logic.analytics_aggregator import aggregate_chart_data
from logic.alert_feed_filter import filter_alert_feed_table
from logic.department_view import calculate_department_breakdown

# Initialize FastAPI App
app = FastAPI(title="ABSA Framework v2.4.1-stable")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load machine learning artifacts
vectorizer = joblib.load("vectorizer.joblib")
model = joblib.load("svm_model.joblib")

# In-memory database array for runtime review logs
REVIEWS_DB = []

# Preset chips for frontend Inference Tester card
PRESETS = [
    "The salmon was perfectly seared but the delivery driver left the gate open.",
    "The battery life is stellar but packaging was damaged.",
    "Cold packaging was crushed and soup spilled.",
    "Food arrived hot and fresh on time."
]


class ReviewInput(BaseModel):
    review: str
    selected_model: str = "SVM_ABSA_V1"


# Root Route: Serves index.html UI
@app.get("/")
def read_root():
    """Serves the dashboard index.html UI directly."""
    return FileResponse("index.html")


# Endpoint 1: System Status Node Search
@app.get("/api/system-status")
def get_system_status():
    """Returns active node status and model versions."""
    return {
        "status": "SYSTEM ONLINE",
        "version": "v2.4.1-stable",
        "active_nodes": len(REVIEWS_DB),
        "available_models": ["SVM_ABSA_V1", "GPT-4_ABSA_V3", "BERT_ABSA_V2"]
    }


# Endpoint 2: Preset Snippets
@app.get("/api/presets")
def get_presets():
    """Provides sample preset texts for rapid UI testing."""
    return {"presets": PRESETS}


# Endpoint 3: Analyze Review (Inference Lab)
@app.post("/api/analyze")
def analyze_review_endpoint(payload: ReviewInput):
    """Executes ABSA pipeline on input text and logs result."""
    result = process_review_for_prediction_card(
        payload.review, vectorizer, model, payload.selected_model
    )
    REVIEWS_DB.append(result)
    return result


# Endpoint 4: Command Center KPI Stats & Analytics
@app.get("/api/dashboard-stats")
def get_dashboard_stats():
    """Calculates KPI metrics and chart breakdown data."""
    metrics = calculate_metric_cards_data(REVIEWS_DB)
    charts = aggregate_chart_data(REVIEWS_DB)
    return {
        "metrics": metrics,
        "charts": charts
    }


# Endpoint 5: Department View Analytics
@app.get("/api/department-view")
def get_department_view():
    """Returns review counts and alert stats per department."""
    return calculate_department_breakdown(REVIEWS_DB)


# Endpoint 6: Active Alert Feed
@app.get("/api/alerts")
def get_alert_feed():
    """Fetches real-time actionable alert records."""
    alert_list = filter_alert_feed_table(REVIEWS_DB)
    return {"alerts": alert_list, "total": len(alert_list)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
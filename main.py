from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

# Import modularized component processors from your business logic layer
from logic.review_processor import process_review_for_prediction_card
from logic.metrics_calculator import calculate_metric_cards_data
from logic.analytics_aggregator import aggregate_chart_data
from logic.alert_feed_filter import filter_alert_feed_table

# Initialize the FastAPI application with a custom API title
app = FastAPI(title="Ghost Kitchen ABSA Framework")

# Enable CORS (Cross-Origin Resource Sharing) to allow requests from any frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains/origins (e.g., React/Vue running on localhost)
    allow_credentials=True,  # Allows cookies or authentication headers
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all standard request headers
)

# Load pre-trained machine learning artifacts into memory at server startup
vectorizer = joblib.load("vectorizer.joblib")
model = joblib.load("svm_model.joblib")

# In-memory database array to temporarily store review inference results during runtime
REVIEWS_DB = []


# Define Pydantic request schema for payload validation on incoming POST requests
class ReviewInput(BaseModel):
    review: str  # Expects a JSON payload like: {"review": "your text here"}


# --------------------------------------------------------------------------
# Endpoint 1: POST /api/analyze
# Serves ReviewInputForm & PredictionCard components
# --------------------------------------------------------------------------
@app.post("/api/analyze")
def analyze_review_endpoint(payload: ReviewInput):
    """Processes a single raw review, predicts aspect/confidence, updates memory store, and returns prediction details."""
    # 1. Run raw text through the ML model pipeline and AAA alert routing
    result = process_review_for_prediction_card(payload.review, vectorizer, model)

    # 2. Append processed result to the in-memory database store
    REVIEWS_DB.append(result)

    # 3. Return prediction result object directly to front-end PredictionCard UI
    return result


# --------------------------------------------------------------------------
# Endpoint 2: GET /api/dashboard-stats
# Serves MetricCards & AnalyticsCharts components for the dashboard
# --------------------------------------------------------------------------
@app.get("/api/dashboard-stats")
def get_dashboard_stats():
    """Computes and returns aggregated KPIs and chart visualization breakdowns from stored reviews."""
    # 1. Compute high-level KPI metric card values (total reviews, alert count, latency, etc.)
    metrics = calculate_metric_cards_data(REVIEWS_DB)

    # 2. Format failure distribution charts for aspect categories and target departments
    charts = aggregate_chart_data(REVIEWS_DB)

    # 3. Return combined payload expected by dashboard visual components
    return {
        "metrics": metrics,
        "charts": charts
    }


# --------------------------------------------------------------------------
# Endpoint 3: GET /api/alerts
# Serves AlertFeedTable component
# --------------------------------------------------------------------------
@app.get("/api/alerts")
def get_alert_feed():
    """Extracts actionable alerts from stored reviews ordered newest-first for real-time alert feed."""
    # 1. Filter stored reviews for actionable alerts and format them for display
    alert_list = filter_alert_feed_table(REVIEWS_DB)

    # 2. Return list of formatted actionable alert records along with total count
    return {"alerts": alert_list, "total": len(alert_list)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
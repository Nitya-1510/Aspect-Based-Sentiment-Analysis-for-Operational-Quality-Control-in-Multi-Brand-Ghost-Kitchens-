import time
import re
import unittest
from unittest.mock import MagicMock
import numpy as np


def clean_review_text(text: str) -> str:
    """Cleans raw text while preserving letters, numbers, and spaces."""
    if not text or not isinstance(text, str):
        return ""
    # 1. Convert text to lowercase
    text = text.lower()
    # 2. Strip URLs (http:// or www.)
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    # 3. Strip punctuation and special characters
    text = re.sub(r"[^\w\s]", "", text)
    # 4. Normalize multiple spaces to a single space
    return re.sub(r"\s+", " ", text).strip()


def predict_aspect_and_confidence(cleaned_text: str, vectorizer, model) -> dict:
    """Transforms cleaned text into features and computes aspect prediction with confidence score."""
    if not cleaned_text:
        return {"aspect": "Unknown", "confidence": 0.0}

    # 1. Transform text to numerical TF-IDF vector
    features = vectorizer.transform([cleaned_text])

    # 2. Predict primary aspect category
    prediction = model.predict(features)[0]

    # 3. Extract decision function distance scores
    decision_scores = model.decision_function(features)

    # 4. Calculate scalar confidence score (max score for multi-class, absolute score for binary)
    confidence = float(
        max(decision_scores[0]) if decision_scores.ndim > 1 else abs(decision_scores[0])
    )
    return {"aspect": str(prediction), "confidence": round(confidence, 3)}


def apply_aaa_routing(aspect: str, confidence: float, threshold: float = 0.5) -> dict:
    """Applies AAA routing rules to flag actionable alerts and assign departments."""
    # 1. Low confidence predictions are filtered out as noise
    if confidence < threshold:
        return {
            "actionable_alert": False,
            "target_department": "General Review / Unassigned",
            "urgency": "Low",
            "status": "NOISE_FILTERED"
        }

    # 2. Map valid predicted aspects to operational target departments
    department_map = {
        "Culinary_Execution": "Kitchen Operations / Head Chef",
        "Packaging_Integrity": "Packaging & Inventory Team",
        "Logistics_Distribution": "Dispatch & Delivery Manager"
    }

    # 3. Dispatch actionable alert with urgency rating
    return {
        "actionable_alert": True,
        "target_department": department_map.get(aspect, "Quality Assurance"),
        "urgency": "High" if confidence >= 1.0 else "Medium",
        "status": "ALERT_DISPATCHED"
    }


def process_review_for_prediction_card(raw_review: str, vectorizer, model, model_name: str = "SVM_ABSA_V1") -> dict:
    """Master pipeline function executing cleaning, prediction, alert routing, and latency tracking."""
    start_time = time.time()

    # Step-by-step pipeline execution
    cleaned = clean_review_text(raw_review)
    pred = predict_aspect_and_confidence(cleaned, vectorizer, model)
    aaa_result = apply_aaa_routing(pred["aspect"], pred["confidence"])

    # Measure execution latency in milliseconds
    latency = round((time.time() - start_time) * 1000, 2)

    return {
        "raw_review": raw_review,
        "cleaned_review": cleaned,
        "predicted_aspect": pred["aspect"],
        "confidence_score": pred["confidence"],
        "actionable_alert": aaa_result["actionable_alert"],
        "target_department": aaa_result["target_department"],
        "urgency": aaa_result["urgency"],
        "status": aaa_result["status"],
        "inference_latency_ms": latency,
        "active_model": model_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# # =====================================================================
# # MODULE TESTER FUNCTION
# # =====================================================================
# class TestReviewProcessor(unittest.TestCase):
#
#     def test_clean_review_text(self):
#         # Asserts URL removal and punctuation stripping
#         self.assertEqual(clean_review_text("Cold food! http://test.com"), "cold food")
#         # Asserts empty input safety
#         self.assertEqual(clean_review_text(""), "")
#
#     def test_predict_aspect_and_confidence(self):
#         mock_vec = MagicMock()
#         mock_vec.transform.return_value = "features"
#         mock_model = MagicMock()
#         mock_model.predict.return_value = ["Culinary_Execution"]
#         mock_model.decision_function.return_value = np.array([[1.234]])
#
#         res = predict_aspect_and_confidence("cold soup", mock_vec, mock_model)
#         self.assertEqual(res["aspect"], "Culinary_Execution")
#         self.assertEqual(res["confidence"], 1.234)
#
#     def test_apply_aaa_routing(self):
#         # High confidence test
#         high_res = apply_aaa_routing("Culinary_Execution", 1.2)
#         self.assertTrue(high_res["actionable_alert"])
#         self.assertEqual(high_res["urgency"], "High")
#
#         # Low confidence noise test
#         low_res = apply_aaa_routing("Culinary_Execution", 0.2)
#         self.assertFalse(low_res["actionable_alert"])
#         self.assertEqual(low_res["status"], "NOISE_FILTERED")
#
#
# def run_module_test():
#     """Runs module-level unit tests."""
#     print("--- Running Tests for review_processor.py ---")
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestReviewProcessor)
#     unittest.TextTestRunner(verbosity=2).run(suite)
#
#
# if __name__ == "__main__":
#     run_module_test()
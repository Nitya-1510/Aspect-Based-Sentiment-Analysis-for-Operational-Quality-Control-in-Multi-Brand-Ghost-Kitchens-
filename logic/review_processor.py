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


def extract_word_heat_scores(cleaned_text: str, vectorizer, model) -> list[dict]:
    """Extracts TF-IDF feature weights for each word to populate the frontend heatmap."""
    words = cleaned_text.split()
    if not words:
        return []

    # Get feature matrix and vocabulary mapping from vectorizer
    feature_matrix = vectorizer.transform([cleaned_text])
    feature_names = vectorizer.get_feature_names_out()
    feature_index_map = {name: idx for idx, name in enumerate(feature_names)}

    word_scores = []
    max_score = 0.001  # Safeguard against division by zero

    for word in words:
        if word in feature_index_map:
            idx = feature_index_map[word]
            tfidf_val = float(feature_matrix[0, idx])

            # If SVM model exposes feature coefficients, weight TF-IDF by model importance
            if hasattr(model, "coef_"):
                coef_weight = float(np.mean(np.abs(model.coef_[:, idx]))) if model.coef_.ndim > 1 else float(
                    abs(model.coef_[0, idx]))
                weight = tfidf_val * coef_weight
            else:
                weight = tfidf_val
        else:
            weight = 0.0

        if weight > max_score:
            max_score = weight

        word_scores.append({"word": word, "raw_weight": weight})

    # Normalize token weights between 0.0 and 1.0 for CSS background opacity shading
    for item in word_scores:
        item["norm_weight"] = round(item["raw_weight"] / max_score, 3)

    return word_scores


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


def apply_aaa_routing(aspect: str, confidence: float, cleaned_text: str = "", threshold: float = 0.5) -> dict:
    """Applies AAA routing rules with keyword severity overrides for robust urgency grading."""

    # 1. Low confidence predictions filtered out as noise
    if confidence < threshold:
        return {
            "actionable_alert": False,
            "target_department": "General Review / Unassigned",
            "urgency": "Low",
            "status": "NOISE_FILTERED"
        }

    department_map = {
        "Culinary_Execution": "Kitchen Operations / Head Chef",
        "Packaging_Integrity": "Packaging & Inventory Team",
        "Logistics_Distribution": "Dispatch & Delivery Manager"
    }

    # 2. High-severity triggers that immediately mandate a 'High' urgency alert
    critical_keywords = [
        "raw", "uncooked", "rotten", "spoiled", "poisoning", "sick", "hair",
        "crushed", "spilled", "burst", "exploded", "destroyed", "flooded",
        "missing", "stolen", "never arrived", "lost", "2 hours", "3 hours"
    ]

    # Check if cleaned review contains critical safety or severe operational failure terms
    is_critical = any(kw in cleaned_text for kw in critical_keywords)

    if is_critical or confidence >= 3.0:
        urgency_rating = "High"
    else:
        urgency_rating = "Medium"

    return {
        "actionable_alert": True,
        "target_department": department_map.get(aspect, "Quality Assurance"),
        "urgency": urgency_rating,
        "status": "ALERT_DISPATCHED"
    }


def process_review_for_prediction_card(raw_review: str, vectorizer, model, model_name: str = "SVM_ABSA_V1") -> dict:
    """Master pipeline function executing cleaning, prediction, heatmap weight extraction, alert routing, and latency tracking."""
    start_time = time.time()

    # Step-by-step pipeline execution
    cleaned = clean_review_text(raw_review)
    pred = predict_aspect_and_confidence(cleaned, vectorizer, model)

    # Pass cleaned text into routing logic to evaluate keyword rules
    aaa_result = apply_aaa_routing(pred["aspect"], pred["confidence"], cleaned_text=cleaned)

    # Extract token weights for heatmap rendering
    heatmap_tokens = extract_word_heat_scores(cleaned, vectorizer, model) if cleaned else []

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
        "heatmap_tokens": heatmap_tokens,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# =====================================================================
# MODULE TESTER FUNCTION
# =====================================================================
class TestReviewProcessor(unittest.TestCase):

    def test_clean_review_text(self):
        # Asserts URL removal and punctuation stripping
        self.assertEqual(clean_review_text("Cold food! http://test.com"), "cold food")
        # Asserts empty input safety
        self.assertEqual(clean_review_text(""), "")

    def test_predict_aspect_and_confidence(self):
        mock_vec = MagicMock()
        mock_vec.transform.return_value = "features"
        mock_model = MagicMock()
        mock_model.predict.return_value = ["Culinary_Execution"]
        mock_model.decision_function.return_value = np.array([[1.234]])

        res = predict_aspect_and_confidence("cold soup", mock_vec, mock_model)
        self.assertEqual(res["aspect"], "Culinary_Execution")
        self.assertEqual(res["confidence"], 1.234)

    def test_apply_aaa_routing(self):
        # Critical keyword test -> High Urgency
        high_res = apply_aaa_routing("Culinary_Execution", 1.2, cleaned_text="the chicken was raw")
        self.assertTrue(high_res["actionable_alert"])
        self.assertEqual(high_res["urgency"], "High")

        # Standard issue test -> Medium Urgency
        med_res = apply_aaa_routing("Culinary_Execution", 1.2, cleaned_text="the fries were soggy and lukewarm")
        self.assertTrue(med_res["actionable_alert"])
        self.assertEqual(med_res["urgency"], "Medium")

        # Low confidence noise test
        low_res = apply_aaa_routing("Culinary_Execution", 0.2, cleaned_text="everything was fine")
        self.assertFalse(low_res["actionable_alert"])
        self.assertEqual(low_res["status"], "NOISE_FILTERED")

    def test_extract_word_heat_scores(self):
        mock_vec = MagicMock()
        mock_vec.transform.return_value = np.array([[0.8, 0.2]])
        mock_vec.get_feature_names_out.return_value = np.array(["cold", "soup"])

        mock_model = MagicMock()
        mock_model.coef_ = np.array([[1.0, 0.5]])

        scores = extract_word_heat_scores("cold soup", mock_vec, mock_model)
        self.assertEqual(len(scores), 2)
        self.assertEqual(scores[0]["word"], "cold")
        self.assertEqual(scores[0]["norm_weight"], 1.0)


def run_module_test():
    """Runs module-level unit tests."""
    print("--- Running Tests for review_processor.py ---")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReviewProcessor)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    run_module_test()
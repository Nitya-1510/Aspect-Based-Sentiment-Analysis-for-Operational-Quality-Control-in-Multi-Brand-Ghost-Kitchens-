import unittest
from unittest.mock import MagicMock
import numpy as np

# Import business logic functions directly from your logic package
from logic.review_processor import (
    clean_review_text,
    predict_aspect_and_confidence,
    apply_aaa_routing,
    process_review_for_prediction_card,
)
from logic.metrics_calculator import calculate_metric_cards_data
from logic.analytics_aggregator import aggregate_chart_data
from logic.alert_feed_filter import filter_alert_feed_table


class TestReviewProcessingPipeline(unittest.TestCase):

    # -------------------------------------------------------------
    # 1. Tests for clean_review_text
    # -------------------------------------------------------------
    def test_clean_review_text_normal(self):
        raw = "The food was horrible! Check http://example.com for proof."
        expected = "the food was horrible check for proof"
        self.assertEqual(clean_review_text(raw), expected)  # Asserts lowercase, URL removal, and punctuation stripping

    def test_clean_review_text_empty_and_invalid(self):
        self.assertEqual(clean_review_text(""), "")  # Handles empty string input safely
        self.assertEqual(clean_review_text(None), "")  # Handles None input without crashing
        self.assertEqual(clean_review_text(12345), "")  # Handles non-string input safely

    def test_clean_review_text_extra_spaces(self):
        raw = "  Lots   of    spaces   here!  "
        expected = "lots of spaces here"
        self.assertEqual(clean_review_text(raw), expected)  # Asserts multiple spaces collapse into a single space

    # -------------------------------------------------------------
    # 2. Tests for predict_aspect_and_confidence
    # -------------------------------------------------------------
    def test_predict_aspect_empty_text(self):
        mock_vec = MagicMock()  # Dummy vectorizer mock
        mock_model = MagicMock()  # Dummy model mock
        res = predict_aspect_and_confidence("", mock_vec, mock_model)
        self.assertEqual(res, {"aspect": "Unknown", "confidence": 0.0})  # Asserts default return on empty text

    def test_predict_aspect_multiclass(self):
        mock_vec = MagicMock()
        mock_vec.transform.return_value = "fake_features"  # Mock vectorizer output

        mock_model = MagicMock()
        mock_model.predict.return_value = ["Culinary_Execution"]  # Mock aspect classification
        mock_model.decision_function.return_value = np.array([[0.2, 1.4567, -0.5]])  # Mock distance scores

        res = predict_aspect_and_confidence("cold pizza", mock_vec, mock_model)

        self.assertEqual(res["aspect"], "Culinary_Execution")  # Asserts target class extraction
        self.assertEqual(res["confidence"], 1.457)  # Asserts max distance score selection and 3-decimal rounding

    # -------------------------------------------------------------
    # 3. Tests for apply_aaa_routing
    # -------------------------------------------------------------
    def test_apply_aaa_routing_below_threshold(self):
        res = apply_aaa_routing("Culinary_Execution", confidence=0.3, threshold=0.5)
        self.assertFalse(res["actionable_alert"])  # Confidence < 0.5 must not trigger actionable alert
        self.assertEqual(res["status"], "NOISE_FILTERED")  # Status flag check
        self.assertEqual(res["urgency"], "Low")  # Low confidence sets urgency to Low

    def test_apply_aaa_routing_medium_urgency(self):
        res = apply_aaa_routing("Packaging_Integrity", confidence=0.7, threshold=0.5)
        self.assertTrue(res["actionable_alert"])  # Confidence >= 0.5 triggers alert
        self.assertEqual(res["target_department"], "Packaging & Inventory Team")  # Mapped department check
        self.assertEqual(res["urgency"], "Medium")  # Confidence between 0.5 and 1.0 sets Medium urgency

    def test_apply_aaa_routing_high_urgency(self):
        res = apply_aaa_routing("Logistics_Distribution", confidence=1.2, threshold=0.5)
        self.assertTrue(res["actionable_alert"])  # Actionable alert active
        self.assertEqual(res["target_department"], "Dispatch & Delivery Manager")  # Mapped department check
        self.assertEqual(res["urgency"], "High")  # Confidence >= 1.0 sets High urgency

    def test_apply_aaa_routing_fallback_department(self):
        res = apply_aaa_routing("Unknown_Aspect", confidence=0.8, threshold=0.5)
        self.assertEqual(res["target_department"], "Quality Assurance")  # Unmapped aspect defaults to QA

    # -------------------------------------------------------------
    # 4. Integration Test for process_review_for_prediction_card
    # -------------------------------------------------------------
    def test_process_review_full_pipeline(self):
        mock_vec = MagicMock()
        mock_vec.transform.return_value = "fake_features"

        mock_model = MagicMock()
        mock_model.predict.return_value = ["Culinary_Execution"]
        mock_model.decision_function.return_value = np.array([[1.1]])

        result = process_review_for_prediction_card("The soup was completely cold!", mock_vec, mock_model)

        self.assertEqual(result["raw_review"], "The soup was completely cold!")  # Retains original raw input
        self.assertEqual(result["cleaned_review"], "the soup was completely cold")  # Verifies clean text pipeline
        self.assertEqual(result["predicted_aspect"], "Culinary_Execution")  # Verifies predicted label
        self.assertTrue(result["actionable_alert"])  # Verifies alert flag
        self.assertIn("inference_latency_ms", result)  # Ensures runtime latency metric is present
        self.assertIn("timestamp", result)  # Ensures ISO-style timestamp is attached

    # -------------------------------------------------------------
    # 5. Tests for calculate_metric_cards_data
    # -------------------------------------------------------------
    def test_calculate_metric_cards_data_standard(self):
        sample_data = [
            {"actionable_alert": True, "inference_latency_ms": 10.0},
            {"actionable_alert": False, "inference_latency_ms": 20.0},
        ]
        metrics = calculate_metric_cards_data(sample_data)
        self.assertEqual(metrics["total_reviews"], 2)  # Verifies total record count
        self.assertEqual(metrics["actionable_alert_count"], 1)  # Verifies active alert count
        self.assertEqual(metrics["actionable_alert_rate_pct"], 50.0)  # Verifies alert percentage calculation
        self.assertEqual(metrics["avg_latency_ms"], 15.0)  # Verifies latency mean calculation

    def test_calculate_metric_cards_data_empty(self):
        metrics = calculate_metric_cards_data([])
        self.assertEqual(metrics["total_reviews"], 0)  # Guard clause check: total reviews
        self.assertEqual(metrics["actionable_alert_count"], 0)  # Guard clause check: alert count
        self.assertEqual(metrics["actionable_alert_rate_pct"], 0.0)  # Prevents ZeroDivisionError
        self.assertEqual(metrics["avg_latency_ms"], 0.0)  # Prevents ZeroDivisionError

    # -------------------------------------------------------------
    # 6. Tests for aggregate_chart_data
    # -------------------------------------------------------------
    def test_aggregate_chart_data(self):
        sample_data = [
            {"predicted_aspect": "Culinary_Execution", "target_department": "Kitchen Operations / Head Chef"},
            {"predicted_aspect": "Packaging_Integrity", "target_department": "Packaging & Inventory Team"},
            {"predicted_aspect": "Unknown_Aspect", "target_department": "Quality Assurance"},
        ]
        chart_data = aggregate_chart_data(sample_data)

        # Extract Culinary count from pillar list-of-dicts output
        culinary_count = next(item["count"] for item in chart_data["pillar_breakdown"] if item["pillar"] == "Culinary_Execution")
        self.assertEqual(culinary_count, 1)  # Asserts correct pillar aggregation

        # Extract dynamic Quality Assurance count from department list-of-dicts output
        qa_count = next(item["count"] for item in chart_data["department_breakdown"] if item["department"] == "Quality Assurance")
        self.assertEqual(qa_count, 1)  # Asserts dynamic department addition works

    # -------------------------------------------------------------
    # 7. Tests for filter_alert_feed_table
    # -------------------------------------------------------------
    def test_filter_alert_feed_table(self):
        sample_data = [
            {
                "raw_review": "First review",
                "predicted_aspect": "Culinary_Execution",
                "target_department": "Kitchen Operations / Head Chef",
                "urgency": "Medium",
                "actionable_alert": True,
                "confidence_score": 0.8,
                "timestamp": "2026-07-29 10:00:00"
            },
            {
                "raw_review": "Second review",
                "predicted_aspect": "Packaging_Integrity",
                "target_department": "Packaging & Inventory Team",
                "urgency": "High",
                "actionable_alert": True,
                "confidence_score": 1.2,
                "timestamp": "2026-07-29 10:05:00"
            }
        ]

        # Test reverse order (newest review should appear first at index 0)
        alerts = filter_alert_feed_table(sample_data)
        self.assertEqual(len(alerts), 2)  # Total alert count
        self.assertEqual(alerts[0]["review_snippet"], "Second review")  # Verifies reversed order (newest first)
        self.assertEqual(alerts[1]["review_snippet"], "First review")  # Verifies older items pushed down

        # Test min_urgency filter parameter
        high_urgency_alerts = filter_alert_feed_table(sample_data, min_urgency="High")
        self.assertEqual(len(high_urgency_alerts), 1)  # Asserts filtering excludes Medium urgency items
        self.assertEqual(high_urgency_alerts[0]["urgency"], "High")  # Asserts remaining record matches filter criteria


if __name__ == "__main__":
    unittest.main()  # Discovers and runs all test methods automatically
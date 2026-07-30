import unittest
from unittest.mock import MagicMock
import numpy as np

# Import all business logic modules from logic package
from logic.review_processor import (
    clean_review_text,
    predict_aspect_and_confidence,
    apply_aaa_routing,
    process_review_for_prediction_card,
)
from logic.metrics_calculator import calculate_metric_cards_data
from logic.analytics_aggregator import aggregate_chart_data
from logic.alert_feed_filter import filter_alert_feed_table
from logic.department_view import calculate_department_breakdown


class TestMasterSuite(unittest.TestCase):

    # 1. Tests for review_processor module
    def test_clean_review_text(self):
        self.assertEqual(clean_review_text("Cold food! http://test.com"), "cold food")
        self.assertEqual(clean_review_text(""), "")

    def test_predict_aspect_and_confidence(self):
        mock_vec = MagicMock()
        mock_vec.transform.return_value = "features"
        mock_model = MagicMock()
        mock_model.predict.return_value = ["Culinary_Execution"]
        mock_model.decision_function.return_value = np.array([[1.5]])

        res = predict_aspect_and_confidence("cold pizza", mock_vec, mock_model)
        self.assertEqual(res["aspect"], "Culinary_Execution")
        self.assertEqual(res["confidence"], 1.5)

    def test_apply_aaa_routing(self):
        res_high = apply_aaa_routing("Culinary_Execution", 1.2)
        self.assertTrue(res_high["actionable_alert"])
        self.assertEqual(res_high["urgency"], "High")

        res_low = apply_aaa_routing("Culinary_Execution", 0.2)
        self.assertFalse(res_low["actionable_alert"])
        self.assertEqual(res_low["status"], "NOISE_FILTERED")

    # 2. Tests for metrics_calculator module
    def test_calculate_metric_cards_data(self):
        logs = [{"actionable_alert": True, "inference_latency_ms": 10.0}]
        res = calculate_metric_cards_data(logs)
        self.assertEqual(res["total_reviews"], 1)
        self.assertEqual(res["actionable_alert_count"], 1)

    # 3. Tests for analytics_aggregator module
    def test_aggregate_chart_data(self):
        logs = [{"predicted_aspect": "Culinary_Execution", "target_department": "Kitchen Operations / Head Chef"}]
        res = aggregate_chart_data(logs)
        culinary = next(i["count"] for i in res["pillar_breakdown"] if i["pillar"] == "Culinary_Execution")
        self.assertEqual(culinary, 1)

    # 4. Tests for alert_feed_filter module
    def test_filter_alert_feed_table(self):
        logs = [
            {"raw_review": "First", "actionable_alert": True, "urgency": "Medium"},
            {"raw_review": "Second", "actionable_alert": True, "urgency": "High"}
        ]
        alerts = filter_alert_feed_table(logs)
        self.assertEqual(alerts[0]["review_snippet"], "Second")  # Newest first test

    # 5. Tests for department_view module
    def test_calculate_department_breakdown(self):
        logs = [{"target_department": "Kitchen Operations / Head Chef", "actionable_alert": True}]
        res = calculate_department_breakdown(logs)
        kitchen = next(d for d in res["departments"] if d["department"] == "Kitchen Operations / Head Chef")
        self.assertEqual(kitchen["total_reviews"], 1)


if __name__ == "__main__":
    print("--- Running Master Test Suite ---")
    unittest.main()
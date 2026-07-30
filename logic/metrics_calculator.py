import unittest


def calculate_metric_cards_data(processed_reviews_list: list[dict]) -> dict:
    """Aggregates review logs into high-level dashboard KPI metrics."""
    total_reviews = len(processed_reviews_list)

    # Guard clause: Return zero values if log store is empty
    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "actionable_alert_count": 0,
            "actionable_alert_rate_pct": 0.0,
            "avg_latency_ms": 0.0
        }

    # Count total actionable alerts
    alert_count = sum(1 for item in processed_reviews_list if item.get("actionable_alert"))
    # Calculate actionable alert rate percentage
    alert_rate = round((alert_count / total_reviews) * 100, 2)

    # Calculate sum and mean inference latency
    total_latency = sum(item.get("inference_latency_ms", 0.0) for item in processed_reviews_list)
    avg_latency = round(total_latency / total_reviews, 2)

    return {
        "total_reviews": total_reviews,
        "actionable_alert_count": alert_count,
        "actionable_alert_rate_pct": alert_rate,
        "avg_latency_ms": avg_latency
    }


# # =====================================================================
# # MODULE TESTER FUNCTION
# # =====================================================================
# class TestMetricsCalculator(unittest.TestCase):
#
#     def test_calculate_metric_cards_data_standard(self):
#         sample_logs = [
#             {"actionable_alert": True, "inference_latency_ms": 10.0},
#             {"actionable_alert": False, "inference_latency_ms": 20.0}
#         ]
#         res = calculate_metric_cards_data(sample_logs)
#         self.assertEqual(res["total_reviews"], 2)
#         self.assertEqual(res["actionable_alert_count"], 1)
#         self.assertEqual(res["actionable_alert_rate_pct"], 50.0)
#         self.assertEqual(res["avg_latency_ms"], 15.0)
#
#     def test_calculate_metric_cards_data_empty(self):
#         res = calculate_metric_cards_data([])
#         self.assertEqual(res["total_reviews"], 0)
#         self.assertEqual(res["actionable_alert_rate_pct"], 0.0)
#
#
# def run_module_test():
#     """Runs module-level unit tests."""
#     print("--- Running Tests for metrics_calculator.py ---")
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestMetricsCalculator)
#     unittest.TextTestRunner(verbosity=2).run(suite)
#
#
# if __name__ == "__main__":
#     run_module_test()
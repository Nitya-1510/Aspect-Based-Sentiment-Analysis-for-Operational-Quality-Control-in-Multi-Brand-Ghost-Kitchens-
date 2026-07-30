import unittest


def filter_alert_feed_table(processed_reviews_list: list[dict], min_urgency: str = None) -> list[dict]:
    """Filters processed reviews into an actionable alert feed ordered newest-first."""
    alerts = []

    # 1. Traverse reviews in reverse order to place newest alerts first
    for item in reversed(processed_reviews_list):
        # 2. Filter for actionable items only
        if item.get("actionable_alert"):
            # 3. Optional urgency level filtering
            if min_urgency and item.get("urgency") != min_urgency:
                continue

            # 4. Append structured alert item
            alerts.append({
                "id": len(alerts) + 1,  # Sequential ID assignment
                "timestamp": item.get("timestamp"),
                "review_snippet": item.get("raw_review"),
                "primary_aspect": item.get("predicted_aspect"),
                "target_department": item.get("target_department"),
                "urgency": item.get("urgency"),
                "confidence_score": item.get("confidence_score")
            })

    return alerts


# # =====================================================================
# # MODULE TESTER FUNCTION
# # =====================================================================
# class TestAlertFeedFilter(unittest.TestCase):
#
#     def test_filter_alert_feed_table(self):
#         sample_logs = [
#             {"raw_review": "First", "actionable_alert": True, "urgency": "Medium"},
#             {"raw_review": "Second", "actionable_alert": True, "urgency": "High"}
#         ]
#         alerts = filter_alert_feed_table(sample_logs)
#         self.assertEqual(len(alerts), 2)
#         # Asserts reverse order sorting (newest first)
#         self.assertEqual(alerts[0]["review_snippet"], "Second")
#
#     def test_filter_by_urgency(self):
#         sample_logs = [
#             {"raw_review": "First", "actionable_alert": True, "urgency": "Medium"},
#             {"raw_review": "Second", "actionable_alert": True, "urgency": "High"}
#         ]
#         alerts = filter_alert_feed_table(sample_logs, min_urgency="High")
#         self.assertEqual(len(alerts), 1)
#         self.assertEqual(alerts[0]["urgency"], "High")
#
#
# def run_module_test():
#     """Runs module-level unit tests."""
#     print("--- Running Tests for alert_feed_filter.py ---")
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestAlertFeedFilter)
#     unittest.TextTestRunner(verbosity=2).run(suite)
#
#
# if __name__ == "__main__":
#     run_module_test()
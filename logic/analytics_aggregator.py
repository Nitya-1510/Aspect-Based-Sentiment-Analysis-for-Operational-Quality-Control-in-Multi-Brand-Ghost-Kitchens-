import unittest


def aggregate_chart_data(processed_reviews_list: list[dict]) -> dict:
    """Groups aspect and department failure metrics into chart-friendly list formats."""
    # 1. Initialize fixed aspect pillar categories
    pillar_counts = {
        "Culinary_Execution": 0,
        "Packaging_Integrity": 0,
        "Logistics_Distribution": 0
    }

    # 2. Initialize default department categories
    department_counts = {
        "Kitchen Operations / Head Chef": 0,
        "Packaging & Inventory Team": 0,
        "Dispatch & Delivery Manager": 0,
        "General Review / Unassigned": 0
    }

    # 3. Iterate through log entries and accumulate counts
    for item in processed_reviews_list:
        aspect = item.get("predicted_aspect")
        dept = item.get("target_department")

        if aspect in pillar_counts:
            pillar_counts[aspect] += 1

        if dept in department_counts:
            department_counts[dept] += 1
        elif dept:  # Dynamically capture custom department mappings
            department_counts[dept] = 1

    # 4. Format objects into arrays expected by frontend chart libraries
    return {
        "pillar_breakdown": [
            {"pillar": key, "count": value} for key, value in pillar_counts.items()
        ],
        "department_breakdown": [
            {"department": key, "count": value} for key, value in department_counts.items()
        ]
    }


# # =====================================================================
# # MODULE TESTER FUNCTION
# # =====================================================================
# class TestAnalyticsAggregator(unittest.TestCase):
#
#     def test_aggregate_chart_data(self):
#         sample_logs = [
#             {"predicted_aspect": "Culinary_Execution", "target_department": "Kitchen Operations / Head Chef"},
#             {"predicted_aspect": "Packaging_Integrity", "target_department": "Packaging & Inventory Team"}
#         ]
#         res = aggregate_chart_data(sample_logs)
#
#         culinary_count = next(i["count"] for i in res["pillar_breakdown"] if i["pillar"] == "Culinary_Execution")
#         self.assertEqual(culinary_count, 1)
#
#
# def run_module_test():
#     """Runs module-level unit tests."""
#     print("--- Running Tests for analytics_aggregator.py ---")
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsAggregator)
#     unittest.TextTestRunner(verbosity=2).run(suite)
#
#
# if __name__ == "__main__":
#     run_module_test()
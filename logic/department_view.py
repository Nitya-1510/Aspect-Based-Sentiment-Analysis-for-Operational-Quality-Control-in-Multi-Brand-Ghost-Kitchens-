import unittest


def calculate_department_breakdown(processed_reviews_list: list[dict]) -> dict:
    """Calculates review counts and urgency alert matrix per operational department."""
    departments = {
        "Kitchen Operations / Head Chef": {"total_reviews": 0, "active_alerts": 0, "high_urgency": 0,
                                           "medium_urgency": 0},
        "Packaging & Inventory Team": {"total_reviews": 0, "active_alerts": 0, "high_urgency": 0, "medium_urgency": 0},
        "Dispatch & Delivery Manager": {"total_reviews": 0, "active_alerts": 0, "high_urgency": 0, "medium_urgency": 0},
        "General Review / Unassigned": {"total_reviews": 0, "active_alerts": 0, "high_urgency": 0, "medium_urgency": 0}
    }

    for item in processed_reviews_list:
        dept = item.get("target_department", "General Review / Unassigned")
        if dept not in departments:
            departments[dept] = {"total_reviews": 0, "active_alerts": 0, "high_urgency": 0, "medium_urgency": 0}

        departments[dept]["total_reviews"] += 1

        if item.get("actionable_alert"):
            departments[dept]["active_alerts"] += 1
            urgency = item.get("urgency")
            if urgency == "High":
                departments[dept]["high_urgency"] += 1
            elif urgency == "Medium":
                departments[dept]["medium_urgency"] += 1

    return {
        "departments": [
            {
                "department": dept,
                "total_reviews": stats["total_reviews"],
                "active_alerts": stats["active_alerts"],
                "high_urgency": stats["high_urgency"],
                "medium_urgency": stats["medium_urgency"]
            }
            for dept, stats in departments.items()
        ]
    }


# =====================================================================
# MODULE TESTER FUNCTION
# =====================================================================
# class TestDepartmentView(unittest.TestCase):
#
#     def test_calculate_department_breakdown(self):
#         sample_logs = [
#             {"target_department": "Kitchen Operations / Head Chef", "actionable_alert": True, "urgency": "High"},
#             {"target_department": "Kitchen Operations / Head Chef", "actionable_alert": True, "urgency": "Medium"}
#         ]
#         res = calculate_department_breakdown(sample_logs)
#         kitchen = next(d for d in res["departments"] if d["department"] == "Kitchen Operations / Head Chef")
#         self.assertEqual(kitchen["total_reviews"], 2)
#         self.assertEqual(kitchen["high_urgency"], 1)
#         self.assertEqual(kitchen["medium_urgency"], 1)
#
#
# def run_module_test():
#     """Runs module-level unit tests."""
#     print("--- Running Tests for department_view.py ---")
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestDepartmentView)
#     unittest.TextTestRunner(verbosity=2).run(suite)
#
#
# if __name__ == "__main__":
#     run_module_test()
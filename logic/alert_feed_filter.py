def filter_alert_feed_table(processed_reviews_list: list[dict], min_urgency: str = None) -> list[dict]:
    """Filters processed reviews to extract actionable alerts for the feed table."""
    # 1. Initialize an empty list to store matching alert records
    alerts = []

    # 2. Iterate through processed reviews in reverse order (newest items first)
    for item in reversed(processed_reviews_list):
        # 3. Only process items marked as actionable alerts (True)
        if item.get("actionable_alert"):
            # 4. Filter out items that do not match the specified urgency (if filter is applied)
            if min_urgency and item.get("urgency") != min_urgency:
                continue

            # 5. Build and append the formatted alert record for display
            alerts.append({
                "id": len(alerts) + 1,  # Generate sequential 1-based IDs
                "timestamp": item.get("timestamp"),
                "review_snippet": item.get("raw_review"),
                "primary_aspect": item.get("predicted_aspect"),
                "target_department": item.get("target_department"),
                "urgency": item.get("urgency"),
                "confidence_score": item.get("confidence_score")
            })

    # 6. Return the list of structured alert records
    return alerts

#test cases

# def run_tests():
#     sample_data = [
#         {
#             "raw_review": "Food was cold",
#             "predicted_aspect": "Culinary_Execution",
#             "target_department": "Kitchen Operations / Head Chef",
#             "urgency": "Medium",
#             "actionable_alert": True,
#             "confidence_score": 0.8,
#             "timestamp": "2026-07-29 10:00:00"
#         },
#         {
#             "raw_review": "It was ok",
#             "predicted_aspect": "Culinary_Execution",
#             "target_department": "General Review / Unassigned",
#             "urgency": "Low",
#             "actionable_alert": False,  # Should be ignored (not actionable)
#             "confidence_score": 0.3,
#             "timestamp": "2026-07-29 10:05:00"
#         },
#         {
#             "raw_review": "Packaging completely destroyed!",
#             "predicted_aspect": "Packaging_Integrity",
#             "target_department": "Packaging & Inventory Team",
#             "urgency": "High",
#             "actionable_alert": True,
#             "confidence_score": 1.2,
#             "timestamp": "2026-07-29 10:10:00"
#         }
#     ]
#
#     test_cases = [
#         # Test Case 1: All actionable alerts without filtering (Newest First order)
#         (
#             "All Actionable Alerts (Reverse Order)",
#             filter_alert_feed_table(sample_data),
#             [
#                 {
#                     "id": 1,
#                     "timestamp": "2026-07-29 10:10:00",
#                     "review_snippet": "Packaging completely destroyed!",
#                     "primary_aspect": "Packaging_Integrity",
#                     "target_department": "Packaging & Inventory Team",
#                     "urgency": "High",
#                     "confidence_score": 1.2
#                 },
#                 {
#                     "id": 2,
#                     "timestamp": "2026-07-29 10:00:00",
#                     "review_snippet": "Food was cold",
#                     "primary_aspect": "Culinary_Execution",
#                     "target_department": "Kitchen Operations / Head Chef",
#                     "urgency": "Medium",
#                     "confidence_score": 0.8
#                 }
#             ]
#         ),
#         # Test Case 2: Filter specifically for 'High' urgency alerts
#         (
#             "Filter by Urgency = 'High'",
#             filter_alert_feed_table(sample_data, min_urgency="High"),
#             [
#                 {
#                     "id": 1,
#                     "timestamp": "2026-07-29 10:10:00",
#                     "review_snippet": "Packaging completely destroyed!",
#                     "primary_aspect": "Packaging_Integrity",
#                     "target_department": "Packaging & Inventory Team",
#                     "urgency": "High",
#                     "confidence_score": 1.2
#                 }
#             ]
#         ),
#         # Test Case 3: Empty input list
#         (
#             "Empty Input List",
#             filter_alert_feed_table([]),
#             []
#         )
#     ]
#
#     print("--- Running Tests for filter_alert_feed_table ---")
#     for name, result, expected in test_cases:
#         if result == expected:
#             print(f"[PASSED] {name}")
#         else:
#             print(f"[FAILED] {name}")
#             print(f"   Expected: {expected}")
#             print(f"   Got:      {result}")
#
#
# if __name__ == "__main__":
#     run_tests()
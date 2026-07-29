def calculate_metric_cards_data(processed_reviews_list: list[dict]) -> dict:
    """Transforms raw stored review logs into high-level KPI cards data."""
    # 1. Get the total number of reviews in the list
    total_reviews = len(processed_reviews_list)

    # 2. Guard clause: Return zeroed-out KPIs if the list is empty to avoid DivisionByZero errors
    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "actionable_alert_count": 0,
            "actionable_alert_rate_pct": 0.0,
            "avg_latency_ms": 0.0
        }

    # 3. Count how many reviews triggered an actionable alert (boolean True)
    alert_count = sum(1 for item in processed_reviews_list if item.get("actionable_alert"))

    # 4. Calculate alert percentage rate rounded to 2 decimal places
    alert_rate = round((alert_count / total_reviews) * 100, 2)

    # 5. Sum all latency measurements (defaulting to 0.0 if key is missing)
    total_latency = sum(item.get("inference_latency_ms", 0.0) for item in processed_reviews_list)

    # 6. Calculate average latency per review in milliseconds
    avg_latency = round(total_latency / total_reviews, 2)

    # 7. Return aggregated KPI summary dictionary
    return {
        "total_reviews": total_reviews,
        "actionable_alert_count": alert_count,
        "actionable_alert_rate_pct": alert_rate,
        "avg_latency_ms": avg_latency
    }

#testing this file
# def run_tests():
#     test_cases = [
#         # Test Case 1: Standard populated list
#         (
#             "Standard multi-review list",
#             [
#                 {"actionable_alert": True, "inference_latency_ms": 12.5},
#                 {"actionable_alert": False, "inference_latency_ms": 8.0},
#                 {"actionable_alert": True, "inference_latency_ms": 15.1},
#                 {"actionable_alert": False, "inference_latency_ms": 9.4},
#             ],
#             {
#                 "total_reviews": 4,
#                 "actionable_alert_count": 2,
#                 "actionable_alert_rate_pct": 50.0,
#                 "avg_latency_ms": 11.25,
#             },
#         ),
#         # Test Case 2: Empty input list
#         (
#             "Empty list edge case",
#             [],
#             {
#                 "total_reviews": 0,
#                 "actionable_alert_count": 0,
#                 "actionable_alert_rate_pct": 0.0,
#                 "avg_latency_ms": 0.0,
#             },
#         ),
#         # Test Case 3: All actionable alerts (100% rate)
#         (
#             "100% alert rate",
#             [
#                 {"actionable_alert": True, "inference_latency_ms": 5.0},
#                 {"actionable_alert": True, "inference_latency_ms": 5.0},
#             ],
#             {
#                 "total_reviews": 2,
#                 "actionable_alert_count": 2,
#                 "actionable_alert_rate_pct": 100.0,
#                 "avg_latency_ms": 5.0,
#             },
#         ),
#         # Test Case 4: Missing keys fallback safety
#         (
#             "Missing optional keys fallback",
#             [
#                 {},  # No actionable_alert or latency keys provided
#                 {"actionable_alert": True, "inference_latency_ms": 10.0},
#             ],
#             {
#                 "total_reviews": 2,
#                 "actionable_alert_count": 1,
#                 "actionable_alert_rate_pct": 50.0,
#                 "avg_latency_ms": 5.0,
#             },
#         ),
#     ]
#
#     print("--- Running Tests for calculate_metric_cards_data ---")
#     for name, input_data, expected in test_cases:
#         result = calculate_metric_cards_data(input_data)
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
def aggregate_chart_data(processed_reviews_list: list[dict]) -> dict:
    """Formats pillar and department failure counts specifically for chart visualization."""
    # 1. Initialize predefined aspect/pillar categories with zero counts
    pillar_counts = {
        "Culinary_Execution": 0,
        "Packaging_Integrity": 0,
        "Logistics_Distribution": 0
    }

    # 2. Initialize default department categories with zero counts
    department_counts = {
        "Kitchen Operations / Head Chef": 0,
        "Packaging & Inventory Team": 0,
        "Dispatch & Delivery Manager": 0,
        "General Review / Unassigned": 0
    }

    # 3. Iterate through each processed review record
    for item in processed_reviews_list:
        aspect = item.get("predicted_aspect")
        dept = item.get("target_department")

        # Increment aspect count only if it matches known pillars
        if aspect in pillar_counts:
            pillar_counts[aspect] += 1

        # Increment department count, dynamically adding new departments if not present
        if dept in department_counts:
            department_counts[dept] += 1
        elif dept:  # Ensure dept is not None before adding
            department_counts[dept] = 1

    # 4. Format aggregated counts into list-of-dicts expected by UI chart libraries
    return {
        "pillar_breakdown": [
            {"pillar": key, "count": value} for key, value in pillar_counts.items()
        ],
        "department_breakdown": [
            {"department": key, "count": value} for key, value in department_counts.items()
        ]
    }

#test cases

# def run_tests():
#     test_cases = [
#         # Test Case 1: Standard populated list matching known categories
#         (
#             "Standard populated list",
#             [
#                 {
#                     "predicted_aspect": "Culinary_Execution",
#                     "target_department": "Kitchen Operations / Head Chef"
#                 },
#                 {
#                     "predicted_aspect": "Packaging_Integrity",
#                     "target_department": "Packaging & Inventory Team"
#                 },
#                 {
#                     "predicted_aspect": "Culinary_Execution",
#                     "target_department": "Kitchen Operations / Head Chef"
#                 },
#             ],
#             {
#                 "pillar_breakdown": [
#                     {"pillar": "Culinary_Execution", "count": 2},
#                     {"pillar": "Packaging_Integrity", "count": 1},
#                     {"pillar": "Logistics_Distribution", "count": 0},
#                 ],
#                 "department_breakdown": [
#                     {"department": "Kitchen Operations / Head Chef", "count": 2},
#                     {"department": "Packaging & Inventory Team", "count": 1},
#                     {"department": "Dispatch & Delivery Manager", "count": 0},
#                     {"department": "General Review / Unassigned", "count": 0},
#                 ],
#             },
#         ),
#         # Test Case 2: Empty input list
#         (
#             "Empty list edge case",
#             [],
#             {
#                 "pillar_breakdown": [
#                     {"pillar": "Culinary_Execution", "count": 0},
#                     {"pillar": "Packaging_Integrity", "count": 0},
#                     {"pillar": "Logistics_Distribution", "count": 0},
#                 ],
#                 "department_breakdown": [
#                     {"department": "Kitchen Operations / Head Chef", "count": 0},
#                     {"department": "Packaging & Inventory Team", "count": 0},
#                     {"department": "Dispatch & Delivery Manager", "count": 0},
#                     {"department": "General Review / Unassigned", "count": 0},
#                 ],
#             },
#         ),
#         # Test Case 3: Custom / Dynamic department fallback (e.g., Quality Assurance)
#         (
#             "Dynamic department insertion",
#             [
#                 {
#                     "predicted_aspect": "Unknown_Aspect",
#                     "target_department": "Quality Assurance"
#                 }
#             ],
#             {
#                 "pillar_breakdown": [
#                     {"pillar": "Culinary_Execution", "count": 0},
#                     {"pillar": "Packaging_Integrity", "count": 0},
#                     {"pillar": "Logistics_Distribution", "count": 0},
#                 ],
#                 "department_breakdown": [
#                     {"department": "Kitchen Operations / Head Chef", "count": 0},
#                     {"department": "Packaging & Inventory Team", "count": 0},
#                     {"department": "Dispatch & Delivery Manager", "count": 0},
#                     {"department": "General Review / Unassigned", "count": 0},
#                     {"department": "Quality Assurance", "count": 1},
#                 ],
#             },
#         ),
#         # Test Case 4: Missing or None fields handling
#         (
#             "Missing fields handling",
#             [
#                 {}  # Empty dict record
#             ],
#             {
#                 "pillar_breakdown": [
#                     {"pillar": "Culinary_Execution", "count": 0},
#                     {"pillar": "Packaging_Integrity", "count": 0},
#                     {"pillar": "Logistics_Distribution", "count": 0},
#                 ],
#                 "department_breakdown": [
#                     {"department": "Kitchen Operations / Head Chef", "count": 0},
#                     {"department": "Packaging & Inventory Team", "count": 0},
#                     {"department": "Dispatch & Delivery Manager", "count": 0},
#                     {"department": "General Review / Unassigned", "count": 0},
#                 ],
#             },
#         ),
#     ]
#
#     print("--- Running Tests for aggregate_chart_data ---")
#     for name, input_data, expected in test_cases:
#         result = aggregate_chart_data(input_data)
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
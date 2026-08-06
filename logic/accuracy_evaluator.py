import csv
from pathlib import Path
from logic.review_processor import process_review_for_prediction_card

def evaluate_test_dataset(csv_path: Path, vectorizer, model, selected_model: str = "SVM_ABSA_V1") -> dict:
    if not csv_path.exists():
        return {"error": "Test dataset CSV not found"}

    total_samples = 0
    correct_predictions = 0
    sample_trend = []
    detailed_results = []

    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            review = row.get("raw_review", "")
            true_aspect = row.get("true_aspect", "").strip()

            result = process_review_for_prediction_card(review, vectorizer, model, selected_model)
            predicted_aspect = result["predicted_aspect"]

            total_samples += 1
            is_correct = predicted_aspect.lower() == true_aspect.lower()
            if is_correct:
                correct_predictions += 1

            cumulative_accuracy = round((correct_predictions / total_samples) * 100, 2)

            sample_trend.append({
                "sample_id": total_samples,
                "cumulative_accuracy": cumulative_accuracy,
                "is_correct": is_correct
            })

            detailed_results.append({
                "id": total_samples,
                "review": review,
                "true_aspect": true_aspect,
                "predicted_aspect": predicted_aspect,
                "is_correct": is_correct
            })

    overall_accuracy = round((correct_predictions / total_samples) * 100, 2) if total_samples > 0 else 0.0

    return {
        "total_samples": total_samples,
        "correct_predictions": correct_predictions,
        "overall_accuracy_pct": overall_accuracy,
        "trend_data": sample_trend,
        "details": detailed_results
    }
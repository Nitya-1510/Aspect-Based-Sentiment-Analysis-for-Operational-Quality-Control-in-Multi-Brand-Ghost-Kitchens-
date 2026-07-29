import time
import re
import joblib


def clean_review_text(text: str) -> str:
    """Cleans raw text by removing URLs, punctuation, and extra spaces."""
    # Return empty string if input is empty or not a string
    if not text or not isinstance(text, str):
        return ""

    # 1. Convert text to lowercase
    text = text.lower()

    # 2. Remove web URLs (e.g., http:// or www. links)
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # 3. Remove punctuation and special characters (keeps letters, numbers, and spaces)
    text = re.sub(r"[^\w\s]", "", text)

    # 4. Collapse multiple spaces into a single space and strip leading/trailing spaces
    return re.sub(r"\s+", " ", text).strip()


def predict_aspect_and_confidence(cleaned_text: str, vectorizer, model) -> dict:
    """Vectorizes text, predicts the aspect category, and measures prediction confidence."""
    # If cleaned text is empty, return default 'Unknown' values
    if not cleaned_text:
        return {"aspect": "Unknown", "confidence": 0.0}

    # 1. Convert the cleaned text string into numerical TF-IDF or bag-of-words features
    features = vectorizer.transform([cleaned_text])

    # 2. Predict the target class label (e.g., 'Culinary_Execution')
    prediction = model.predict(features)[0]

    # 3. Get raw decision distance scores from the model (e.g., SVM / Logistic Regression)
    decision_scores = model.decision_function(features)

    # 4. Calculate confidence:
    # - If multi-class (>1 dim), take the highest score
    # - If binary class (1 dim), take the absolute distance from decision boundary
    confidence = float(
        max(decision_scores[0]) if decision_scores.ndim > 1 else abs(decision_scores[0])
    )

    return {"aspect": str(prediction), "confidence": round(confidence, 3)}


def apply_aaa_routing(aspect: str, confidence: float, threshold: float = 0.5) -> dict:
    """Routes alerts to specific teams based on confidence score and predicted aspect."""
    # 1. Filter out low-confidence predictions to reduce false alarms/noise
    if confidence < threshold:
        return {
            "actionable_alert": False,
            "target_department": "General Review / Unassigned",
            "urgency": "Low",
            "status": "NOISE_FILTERED"
        }

    # 2. Map predicted aspects to responsible departments
    department_map = {
        "Culinary_Execution": "Kitchen Operations / Head Chef",
        "Packaging_Integrity": "Packaging & Inventory Team",
        "Logistics_Distribution": "Dispatch & Delivery Manager"
    }

    # 3. Return high-confidence alert details with urgency level
    return {
        "actionable_alert": True,
        # Default to 'Quality Assurance' if aspect isn't in the mapping dictionary
        "target_department": department_map.get(aspect, "Quality Assurance"),
        "urgency": "High" if confidence >= 1.0 else "Medium",
        "status": "ALERT_DISPATCHED"
    }


def process_review_for_prediction_card(raw_review: str, vectorizer, model) -> dict:
    """Master function: Cleans input, predicts aspect, routes alerts, and measures runtime."""
    # 1. Record start time to measure execution speed
    start_time = time.time()

    # 2. Step-by-step processing pipeline
    cleaned = clean_review_text(raw_review)
    pred = predict_aspect_and_confidence(cleaned, vectorizer, model)
    aaa_result = apply_aaa_routing(pred["aspect"], pred["confidence"])

    # 3. Calculate processing speed (latency) in milliseconds
    latency = round((time.time() - start_time) * 1000, 2)

    # 4. Package all review metadata into a final result dictionary
    return {
        "raw_review": raw_review,
        "cleaned_review": cleaned,
        "predicted_aspect": pred["aspect"],
        "confidence_score": pred["confidence"],
        "actionable_alert": aaa_result["actionable_alert"],
        "target_department": aaa_result["target_department"],
        "urgency": aaa_result["urgency"],
        "status": aaa_result["status"],
        "inference_latency_ms": latency,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

#test the functions (uncomment them to test them)
# test_cases = [
#     ("URLs", "Great food! Check out https://example.com for more info.", "great food check out for more info"),
#     ("Punctuation & Caps", "VERY BAD packaging!!! Cold food...", "very bad packaging cold food"),
#     ("Extra Whitespace", "  Too   many    spaces   here.  ", "too many spaces here"),
#     ("Empty String", "", ""),
#     ("Non-string Input", None, ""),
# ]
#
# print("--- Testing clean_review_text ---")
# for name, sample_input, expected in test_cases:
#     result = clean_review_text(sample_input)
#     status = "PASSED" if result == expected else f"FAILED (Got: '{result}')"
#     print(f"[{status}] {name}")
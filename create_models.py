import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

# 1. Sample dataset representing your 3 core ghost kitchen aspects
reviews = [
    "The pizza was completely cold and cheese was hard",
    "Food taste was awful and soup was undercooked",
    "Chicken was raw and bad culinary quality",
    "Box was damaged and sauce leaked everywhere",
    "Packaging was torn open and spilled inside bag",
    "Container crushed and poorly wrapped",
    "Delivery took 2 hours and driver was lost",
    "Order arrived very late and missed items",
    "Logistics failed and food took forever"
]

labels = [
    "Culinary_Execution",
    "Culinary_Execution",
    "Culinary_Execution",
    "Packaging_Integrity",
    "Packaging_Integrity",
    "Packaging_Integrity",
    "Logistics_Distribution",
    "Logistics_Distribution",
    "Logistics_Distribution"
]

# 2. Train TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(reviews)

# 3. Train Linear SVM Model
model = SVC(kernel="linear", probability=True)
model.fit(X, labels)

# 4. Save both files directly into your project folder
joblib.dump(vectorizer, "vectorizer.joblib")
joblib.dump(model, "svm_model.joblib")

print("Successfully created vectorizer.joblib and svm_model.joblib!")
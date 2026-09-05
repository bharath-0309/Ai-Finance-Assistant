import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "expense_classifier.joblib")

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

def predict_category(description):
    model = load_model()
    if model is None:
        return "Other", 0.0

    probabilities = model.predict_proba([description])[0]
    classes = model.classes_
    index = probabilities.argmax()
    return str(classes[index]), float(probabilities[index])

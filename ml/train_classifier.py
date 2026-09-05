import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "transactions.csv")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "expense_classifier.joblib")

def main():
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates()
    df["description"] = df["description"].fillna("").str.lower().str.strip()
    df["category"] = df["category"].fillna("Other")

    x_train, x_test, y_train, y_test = train_test_split(
        df["description"], df["category"],
        test_size=0.25, random_state=42, stratify=df["category"]
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("classifier", LogisticRegression(max_iter=1000, solver="liblinear"))
    ])

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="weighted", zero_division=0
    )

    print("Expense Classification Model Evaluation")
    print("---------------------------------------")
    print(f"Accuracy : {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall   : {recall:.3f}")
    print(f"F1-score : {f1:.3f}")
    print("\nConfusion matrix:")
    print(confusion_matrix(y_test, predictions))

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")

if __name__ == "__main__":
    main()

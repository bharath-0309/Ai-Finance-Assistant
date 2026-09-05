# Model Training Notes

## Objective
Predict an expense category from a short transaction description.

## Preprocessing
1. Load the educational transaction CSV.
2. Remove duplicate rows.
3. Fill missing descriptions/categories.
4. Convert descriptions to lowercase.
5. Split the data into training and testing sets.

## Features
TF-IDF converts words and word pairs into numerical features.

## Model
Logistic Regression was selected because it is relatively simple to explain in a student viva and works well with sparse text features.

## Evaluation
The training script reports:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

## Example
Input: `swiggy dinner 450`
Expected category: `Food`

Input: `uber ride 300`
Expected category: `Transport`

## Forecasting
The application separately groups expense transactions by month and uses Linear Regression when at least three months of history are available. It intentionally reports the result as an estimate.

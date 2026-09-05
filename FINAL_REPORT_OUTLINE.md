# Final Major Project Report Outline

## Title
AI Finance Assistant

## Abstract
AI Finance Assistant is a beginner-friendly personal finance web application that combines normal expense tracking with machine learning. Users can record income and expenses, create budgets, view dashboards, and receive simple financial insights. A TF-IDF and Logistic Regression model predicts expense categories from transaction descriptions. A Linear Regression model provides a basic estimate of future spending when enough history is available.

## Problem Statement
Manual expense tracking requires users to enter and categorize transactions and then interpret their own spending patterns. This project reduces that effort through automatic categorization, summaries and simple predictions.

## Objectives
- Build a simple personal finance application.
- Automatically classify expense descriptions.
- Track income, expenses and balance.
- Create and monitor budgets.
- Analyze spending patterns.
- Estimate future spending.
- Provide understandable educational insights.

## Modules
1. Authentication
2. Transaction Management
3. ML Classification
4. Budget Management
5. Analytics Dashboard
6. Spending Prediction
7. AI Insights
8. Finance Chatbot

## Methodology
The web client sends data to Flask routes. Validated transaction data is stored in SQLite. For an expense without a selected category, the description is passed to the trained TF-IDF + Logistic Regression pipeline. Dashboard services aggregate the stored data. The forecasting service groups historical expenses by month and fits Linear Regression if at least three months exist.

## Result
The project provides a complete student-level demonstration of CRUD operations, database integration, visualization, machine learning classification, basic forecasting and responsible AI messaging.

## Limitations
The classifier is trained on a small educational dataset. Forecasting is basic and depends on historical data. The chatbot is rule-based. The system does not connect to real bank accounts and does not provide professional financial advice.

## Future Scope
OCR receipt scanning, voice entry, stronger time-series forecasting, anomaly detection, savings goals, mobile application and cloud deployment can be added later.

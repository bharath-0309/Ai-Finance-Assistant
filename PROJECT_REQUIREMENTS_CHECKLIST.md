# SRS Requirement Checklist

This checklist maps the supplied SRS to the implementation.

| SRS requirement | Implementation |
|---|---|
| Registration/login/logout | `app/routes.py` + Flask-Login |
| User-specific financial records | Queries filter by `current_user.id` |
| Add income/expense | Transactions page + API |
| Edit/delete/view | Transactions page + API |
| Search/filter | Transaction search and type filter |
| ML expense categorization | TF-IDF + Logistic Regression |
| Categories | Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other |
| User can correct category | Category can be manually selected and transaction can be edited |
| Monthly budget | Budgets page |
| Category-wise limits | Optional budget category |
| Budget usage/warnings | `budget_status()` |
| Dashboard totals | Income, expenses and balance cards |
| Category chart | Chart.js doughnut chart |
| Spending forecast | Linear Regression after 3+ months |
| Insufficient history handling | Friendly message |
| High-spending insights | `make_insights()` |
| Educational disclaimer | UI footer and chatbot response |
| Password hashing | Werkzeug password hashing |
| API authorization | Flask-Login and user filtering |
| Input validation | Forms/API checks |
| Database | SQLite + SQLAlchemy |
| Prediction table | `Prediction` model |
| Insights table | `Insight` model |
| Chatbot | Rule-based application finance chatbot |
| Testing | `tests/test_app.py` |
| ML metrics | Accuracy, precision, recall, F1 and confusion matrix |

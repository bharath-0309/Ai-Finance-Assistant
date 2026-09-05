# AI Finance Assistant

A beginner-friendly final major project built according to the supplied Software Requirements Specification (SRS).

## Main features
- User registration, login and logout
- Add, edit, delete and search transactions
- ML-based expense categorization using TF-IDF + Logistic Regression
- Monthly and category-wise budgets
- Dashboard with income, expenses, balance and charts
- Basic future spending forecast using Linear Regression
- Rule-based AI financial insights
- Simple finance chatbot for application/general finance questions
- SQLite database for easy student-level setup
- Password hashing and user-specific data access
- Basic automated tests

> This project is educational. It does not provide professional investment, tax, or financial advice.

## Tech stack
Python, Flask, SQLite, SQLAlchemy, scikit-learn, pandas, NumPy, Chart.js.

## How to run

### 1. Create and activate a virtual environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install packages
```bash
pip install -r requirements.txt
```

### 3. Train the ML model
```bash
python ml/train_classifier.py
```

This creates `ml/expense_classifier.joblib`.

### 4. Start the application
```bash
python run.py
```

Open:
`http://127.0.0.1:5000`

## Demo login
The project does not ship with a hard-coded password. Register a new user from the login page.

## Project structure

```text
AI_Finance_Assistant/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── ml_service.py
│   ├── services.py
│   ├── templates/
│   └── static/
├── data/
│   └── transactions.csv
├── ml/
│   └── train_classifier.py
├── notebooks/
│   └── model_training_notes.md
├── tests/
│   └── test_app.py
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

## API endpoints
- `POST /api/register`
- `POST /api/login`
- `POST /api/transactions`
- `GET /api/transactions`
- `PUT /api/transactions/<id>`
- `DELETE /api/transactions/<id>`
- `POST /api/predict-category`
- `GET /api/dashboard`
- `POST /api/budgets`
- `GET /api/insights`

The web pages use the same backend services.

## ML approach

### Expense classification
Transaction descriptions are converted into TF-IDF vectors and classified with Logistic Regression. The training data is a small educational dataset included in `data/transactions.csv`.

### Spending forecast
The forecast uses monthly expense totals. If at least three months are available, Linear Regression estimates the next month. If there is not enough history, the application shows a friendly message instead of pretending the estimate is reliable.

### Evaluation
Run:
```bash
python ml/train_classifier.py
```
The script prints accuracy, precision, recall, F1-score and a confusion matrix.

## Testing
```bash
python -m unittest discover -s tests -v
```

## Notes for academic demonstration
The UI is intentionally simple rather than production-heavy. The implementation separates authentication, transactions, ML, budgets, analytics and insights so the modules can be explained easily during a viva.

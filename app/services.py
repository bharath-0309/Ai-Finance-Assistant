from collections import defaultdict
from datetime import date
import calendar
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from .models import Transaction, Budget

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Education", "Other"
]

def current_month():
    return date.today().strftime("%Y-%m")

def user_transactions(user_id):
    return Transaction.query.filter_by(user_id=user_id).all()

def dashboard_data(user_id, month=None):
    month = month or current_month()
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date.like(f"{month}%")
    ).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expenses = sum(t.amount for t in transactions if t.type == "expense")
    by_category = defaultdict(float)

    for t in transactions:
        if t.type == "expense":
            by_category[t.category or "Other"] += t.amount

    return {
        "month": month,
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "balance": round(income - expenses, 2),
        "categories": {k: round(v, 2) for k, v in sorted(by_category.items())}
    }

def budget_status(user_id, month=None):
    month = month or current_month()
    budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
    result = []

    for b in budgets:
        query = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date.like(f"{month}%")
        )
        if b.category:
            query = query.filter_by(category=b.category)
        spent = sum(t.amount for t in query.all())
        percent = (spent / b.limit_amount * 100) if b.limit_amount else 0
        result.append({
            "id": b.id,
            "category": b.category or "Overall",
            "limit": round(b.limit_amount, 2),
            "spent": round(spent, 2),
            "remaining": round(b.limit_amount - spent, 2),
            "percent": round(percent, 1),
            "warning": percent >= 80
        })
    return result

def forecast_next_month(user_id):
    transactions = Transaction.query.filter_by(
        user_id=user_id, type="expense"
    ).all()

    if not transactions:
        return {"available": False, "message": "Add some expenses before using the forecast."}

    df = pd.DataFrame([
        {"date": t.date, "amount": t.amount} for t in transactions
    ])
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().sort_index()

    if len(monthly) < 3:
        return {
            "available": False,
            "message": "At least 3 months of expense history are needed for a basic forecast."
        }

    x = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly.values
    model = LinearRegression()
    model.fit(x, y)
    prediction = max(0, float(model.predict([[len(monthly)]])[0]))

    return {
        "available": True,
        "next_month_estimate": round(prediction, 2),
        "months_used": len(monthly)
    }

def make_insights(user_id, month=None):
    data = dashboard_data(user_id, month)
    insights = []

    if data["expenses"] == 0:
        insights.append("No expenses are recorded for this month yet. Add transactions to see spending patterns.")
        return insights

    if data["income"] > 0:
        ratio = data["expenses"] / data["income"] * 100
        if ratio > 90:
            insights.append("Your expenses are above 90% of your income this month. Consider reviewing non-essential spending.")
        elif ratio > 70:
            insights.append("Your expenses are above 70% of your income this month. Keeping an eye on your budget may help.")

    if data["categories"]:
        top = max(data["categories"], key=data["categories"].get)
        top_value = data["categories"][top]
        insights.append(f"{top} is your highest spending category this month at ₹{top_value:.2f}.")

    for item in budget_status(user_id, month):
        if item["percent"] >= 100:
            insights.append(f"You have exceeded the {item['category']} budget for {month}.")
        elif item["percent"] >= 80:
            insights.append(f"You are close to the {item['category']} budget limit ({item['percent']:.0f}% used).")

    return insights[:5]

def chatbot_reply(message):
    text = message.lower().strip()

    if "budget" in text:
        return "A budget is a spending limit for a month. You can create an overall or category-wise budget from the Budgets page."
    if "category" in text or "categorize" in text:
        return "The app uses a TF-IDF + Logistic Regression model to predict categories from expense descriptions. You can correct a prediction before saving."
    if "forecast" in text or "predict" in text:
        return "The spending forecast uses previous monthly expenses. It is only an estimate and needs at least three months of history."
    if "balance" in text:
        return "Current balance is calculated as total income minus total expenses for the selected month."
    if "advice" in text or "invest" in text or "tax" in text:
        return "This student project provides educational insights only. It does not provide professional investment, tax, or financial advice."
    if "hello" in text or "hi" in text:
        return "Hello! I can explain budgets, categories, forecasts, dashboard calculations, and other app features."
    return "I can help with budgets, expense categories, forecasts, balance calculations, and how to use this finance assistant."

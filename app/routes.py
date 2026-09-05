from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from . import db, login_manager
from .models import User, Transaction, Budget, Prediction
from .services import dashboard_data, budget_status, forecast_next_month, make_insights, chatbot_reply, CATEGORIES
from .ml_service import predict_category

main = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:
            flash("Please enter all details. Password should be at least 6 characters.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return render_template("register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main.route("/dashboard")
@login_required
def dashboard():
    month = request.args.get("month") or datetime.now().strftime("%Y-%m")
    data = dashboard_data(current_user.id, month)
    budgets = budget_status(current_user.id, month)
    forecast = forecast_next_month(current_user.id)
    insights = make_insights(current_user.id, month)

    recent = Transaction.query.filter_by(user_id=current_user.id).order_by(
        Transaction.date.desc(), Transaction.id.desc()
    ).limit(8).all()

    return render_template(
        "dashboard.html",
        data=data, budgets=budgets, forecast=forecast,
        insights=insights, recent=recent, month=month
    )

@main.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            tx_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
            description = request.form.get("description", "").strip()
            tx_type = request.form.get("type", "expense")
            category = request.form.get("category") or None

            if amount <= 0 or not description or tx_type not in ["income", "expense"]:
                raise ValueError

            if tx_type == "expense" and not category:
                category, confidence = predict_category(description)
                category = category if category in CATEGORIES else "Other"
            elif tx_type == "income":
                confidence = None
                category = "Income"

            tx = Transaction(
                user_id=current_user.id, date=tx_date,
                description=description, amount=amount,
                type=tx_type, category=category
            )
            db.session.add(tx)
            db.session.flush()

            if tx_type == "expense":
                db.session.add(Prediction(
                    transaction_id=tx.id,
                    predicted_category=category,
                    confidence=confidence
                ))

            db.session.commit()
            flash("Transaction added successfully.", "success")
        except (ValueError, TypeError):
            flash("Please enter valid transaction details.", "danger")

        return redirect(url_for("main.transactions"))

    q = request.args.get("q", "").strip()
    tx_type = request.args.get("type", "")
    query = Transaction.query.filter_by(user_id=current_user.id)

    if q:
        query = query.filter(or_(
            Transaction.description.ilike(f"%{q}%"),
            Transaction.category.ilike(f"%{q}%")
        ))
    if tx_type in ["income", "expense"]:
        query = query.filter_by(type=tx_type)

    txs = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    return render_template("transactions.html", transactions=txs, categories=CATEGORIES)

@main.route("/transactions/delete/<int:tx_id>", methods=["POST"])
@login_required
def delete_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    Prediction.query.filter_by(transaction_id=tx.id).delete()
    db.session.delete(tx)
    db.session.commit()
    flash("Transaction deleted.", "success")
    return redirect(url_for("main.transactions"))

@main.route("/transactions/edit/<int:tx_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        try:
            tx.amount = float(request.form["amount"])
            tx.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
            tx.description = request.form["description"].strip()
            tx.type = request.form["type"]
            tx.category = request.form.get("category") or ("Income" if tx.type == "income" else "Other")
            db.session.commit()
            flash("Transaction updated.", "success")
            return redirect(url_for("main.transactions"))
        except (ValueError, KeyError):
            flash("Invalid transaction details.", "danger")

    return render_template("edit_transaction.html", tx=tx, categories=CATEGORIES)

@main.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    month = request.args.get("month") or datetime.now().strftime("%Y-%m")
    if request.method == "POST":
        try:
            amount = float(request.form["limit_amount"])
            category = request.form.get("category") or None
            bmonth = request.form.get("month") or month
            if amount <= 0:
                raise ValueError
            db.session.add(Budget(
                user_id=current_user.id, month=bmonth,
                category=category, limit_amount=amount
            ))
            db.session.commit()
            flash("Budget created.", "success")
        except (ValueError, KeyError):
            flash("Please enter a valid budget.", "danger")
        return redirect(url_for("main.budgets", month=month))

    return render_template(
        "budgets.html",
        budgets=budget_status(current_user.id, month),
        categories=CATEGORIES, month=month
    )

@main.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():
    answer = None
    if request.method == "POST":
        answer = chatbot_reply(request.form.get("message", ""))
    return render_template("chatbot.html", answer=answer)

# ---------------- API ----------------

@main.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    name, email, password = data.get("name", "").strip(), data.get("email", "").strip().lower(), data.get("password", "")
    if not name or not email or len(password) < 6:
        return jsonify({"error": "Invalid registration data"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered", "user_id": user.id}), 201

@main.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email", "").strip().lower()).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401
    login_user(user)
    return jsonify({"message": "Login successful"})

@main.route("/api/transactions", methods=["GET", "POST"])
@login_required
def api_transactions():
    if request.method == "GET":
        txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        return jsonify([{
            "id": t.id, "date": t.date.isoformat(), "description": t.description,
            "amount": t.amount, "type": t.type, "category": t.category
        } for t in txs])

    data = request.get_json() or {}
    try:
        tx_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        amount = float(data["amount"])
        tx_type = data["type"]
        description = data["description"].strip()
        if amount <= 0 or tx_type not in ["income", "expense"] or not description:
            raise ValueError
        category = data.get("category")
        confidence = None
        if tx_type == "expense" and not category:
            category, confidence = predict_category(description)
        elif tx_type == "income":
            category = "Income"

        tx = Transaction(
            user_id=current_user.id, date=tx_date, description=description,
            amount=amount, type=tx_type, category=category or "Other"
        )
        db.session.add(tx)
        db.session.flush()
        if tx_type == "expense":
            db.session.add(Prediction(transaction_id=tx.id, predicted_category=tx.category, confidence=confidence))
        db.session.commit()
        return jsonify({"message": "Transaction added", "id": tx.id}), 201
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Invalid transaction data"}), 400

@main.route("/api/transactions/<int:tx_id>", methods=["PUT", "DELETE"])
@login_required
def api_transaction_item(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    if request.method == "DELETE":
        Prediction.query.filter_by(transaction_id=tx.id).delete()
        db.session.delete(tx)
        db.session.commit()
        return jsonify({"message": "Transaction deleted"})

    data = request.get_json() or {}
    try:
        tx.amount = float(data.get("amount", tx.amount))
        tx.description = data.get("description", tx.description).strip()
        tx.type = data.get("type", tx.type)
        if "date" in data:
            tx.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        tx.category = data.get("category", tx.category)
        db.session.commit()
        return jsonify({"message": "Transaction updated"})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid transaction data"}), 400

@main.route("/api/predict-category", methods=["POST"])
@login_required
def api_predict_category():
    data = request.get_json() or {}
    description = data.get("description", "").strip()
    if not description:
        return jsonify({"error": "Description is required"}), 400
    category, confidence = predict_category(description)
    return jsonify({"category": category, "confidence": round(confidence, 3)})

@main.route("/api/dashboard")
@login_required
def api_dashboard():
    return jsonify(dashboard_data(current_user.id, request.args.get("month")))

@main.route("/api/budgets", methods=["POST"])
@login_required
def api_budget():
    data = request.get_json() or {}
    try:
        amount = float(data["limit_amount"])
        month = data.get("month") or datetime.now().strftime("%Y-%m")
        if amount <= 0:
            raise ValueError
        b = Budget(
            user_id=current_user.id, month=month,
            category=data.get("category") or None, limit_amount=amount
        )
        db.session.add(b)
        db.session.commit()
        return jsonify({"message": "Budget created", "id": b.id}), 201
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Invalid budget data"}), 400

@main.route("/api/insights")
@login_required
def api_insights():
    return jsonify({"insights": make_insights(current_user.id, request.args.get("month"))})

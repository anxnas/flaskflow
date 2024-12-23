from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import func
import datetime

from . import admin_bp
from ..extensions import db, logger
from ..forms import UserForm, TransactionForm, UpdateTransactionForm, AutoRefreshForm
from ..models import User, Transaction
from config import Config
from ..utils import hash_password, verify_password, calculate_commission

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and verify_password(user.password_hash, password) and user.role == "admin":
            login_user(user)
            logger.info(f"Админ {user.username} вошёл в систему")
            flash("Вы успешно вошли в систему", "success")
            return redirect(url_for("admin_bp.dashboard"))
        else:
            flash("Неверные учётные данные или вы не админ", "danger")
            return redirect(url_for("admin_bp.admin_login"))

    return render_template("admin_login.html")


@admin_bp.route("/logout")
@login_required
def admin_logout():
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))
    logger.info(f"Админ {current_user.username} вышел")
    logout_user()
    flash("Вы вышли из системы", "success")
    return redirect(url_for("admin_bp.admin_login"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    total_users = User.query.count()
    total_transactions = Transaction.query.count()

    today = datetime.date.today()
    start_of_day = datetime.datetime.combine(today, datetime.time.min)
    end_of_day = datetime.datetime.combine(today, datetime.time.max)
    sum_of_today_transactions = db.session.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.created_at >= start_of_day,
        Transaction.created_at <= end_of_day
    ).scalar()

    latest_transactions = Transaction.query.order_by(Transaction.id.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_transactions=total_transactions,
        sum_of_today_transactions=sum_of_today_transactions,
        latest_transactions=latest_transactions
    )


@admin_bp.route("/users", methods=["GET"])
@login_required
def users_list():
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    users = User.query.all()
    return render_template("user_list.html", users=users)

@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def user_create():
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    form = UserForm()
    if form.validate_on_submit():
        is_admin = (form.role.data == "Администратор")
        new_user = User(
            username=form.username.data,
            password_hash=hash_password(form.password.data if form.password.data else "12345"),
            balance=form.balance.data,
            commission_rate=form.commission_rate.data,
            webhook_url=form.webhook_url.data,
            role="admin" if is_admin else "user",
            usdt_wallet=form.usdt_wallet.data or None
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Пользователь успешно создан", "success")
        return redirect(url_for("admin_bp.users_list"))
    return render_template("user_form.html", form=form)

@admin_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_edit(user_id: int):
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.password_hash = hash_password(form.password.data)
        user.balance = form.balance.data
        user.commission_rate = form.commission_rate.data
        user.webhook_url = form.webhook_url.data
        user.role = "admin" if (form.role.data == "Администратор") else "user"
        user.usdt_wallet = form.usdt_wallet.data
        db.session.commit()
        flash("Пользователь успешно обновлён", "success")
        return redirect(url_for("admin_bp.users_list"))

    return render_template("user_form.html", form=form)

@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
def user_delete(user_id: int):
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Пользователь удалён", "success")
    return redirect(url_for("admin_bp.users_list"))

@admin_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions_list():
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    user_id = request.args.get("user_id")
    status = request.args.get("status")

    query = Transaction.query
    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    if status:
        query = query.filter(Transaction.status == status)

    transactions = query.order_by(Transaction.id.desc()).all()
    form = AutoRefreshForm()
    form.auto_refresh.choices = [(k, v) for k, v in Config.AUTO_REFRESH_OPTIONS.items()]

    if form.validate_on_submit():
        pass

    return render_template("transaction_list.html", transactions=transactions, form=form)

@admin_bp.route("/transactions/<int:tx_id>", methods=["GET", "POST"])
@login_required
def transaction_detail(tx_id: int):
    if current_user.role != "admin":
        return redirect(url_for("user_bp.transactions"))

    tx = Transaction.query.get_or_404(tx_id)
    form = UpdateTransactionForm(obj=tx)

    if form.validate_on_submit():
        if tx.status == "pending":
            mapping = {
                "Ожидание": "pending",
                "Подтверждена": "confirmed",
                "Отменена": "canceled",
                "Истекла": "expired"
            }
            new_status = mapping.get(form.status.data, "pending")
            if new_status in ["confirmed", "canceled"]:
                tx.status = new_status
                db.session.commit()
                flash("Статус транзакции изменён", "success")
        return redirect(url_for("admin_bp.transactions_list"))

    return render_template("transaction_detail.html", transaction=tx, form=form)

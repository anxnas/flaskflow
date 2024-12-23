from flask import request, jsonify
from typing import Callable, Any
from . import api_bp
from app.extensions import db, logger
from app.models import User, Transaction
from app.utils import calculate_commission, create_jwt_token, decode_jwt_token, verify_password
from config import Config

def jwt_required(func: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Требуется JWT-токен в заголовке Authorization"}), 401

        token = auth_header.split(" ")[1]
        payload = decode_jwt_token(token, Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM)
        if not payload:
            return jsonify({"error": "Невалидный или истёкший токен"}), 401

        user_id = payload["sub"]
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404

        request.current_user = user
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Необходимо указать username и password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Неверные учётные данные"}), 401

    token = create_jwt_token(user.id, Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM, expires_minutes=60)
    return jsonify({"access_token": token}), 200

@api_bp.route("/create_transaction", methods=["POST"])
@jwt_required
def create_transaction():
    data = request.json or {}
    amount = data.get("amount")
    if not amount:
        return jsonify({"error": "Поле 'amount' обязательно"}), 400

    user = request.current_user
    commission = calculate_commission(user, amount)

    tx = Transaction(
        user_id=user.id,
        amount=amount,
        commission=commission,
        status="pending"
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({"message": "Транзакция создана", "transaction_id": tx.id}), 200

@api_bp.route("/cancel_transaction", methods=["POST"])
@jwt_required
def cancel_transaction():
    data = request.json or {}
    tx_id = data.get("transaction_id")
    if not tx_id:
        return jsonify({"error": "Укажите 'transaction_id'"}), 400

    tx = Transaction.query.get(tx_id)
    if not tx or tx.user_id != request.current_user.id:
        return jsonify({"error": "Транзакция не найдена или не принадлежит вам"}), 404

    if tx.status == "pending":
        tx.status = "canceled"
        db.session.commit()
        return jsonify({"message": "Транзакция отменена"}), 200
    else:
        return jsonify({"error": f"Нельзя отменить транзакцию в статусе {tx.status}"}), 400

@api_bp.route("/check_transaction", methods=["GET"])
@jwt_required
def check_transaction():
    tx_id = request.args.get("transaction_id")
    if not tx_id:
        return jsonify({"error": "Необходимо передать 'transaction_id' как query-параметр"}), 400

    tx = Transaction.query.get(tx_id)
    if not tx or tx.user_id != request.current_user.id:
        return jsonify({"error": "Транзакция не найдена или не принадлежит вам"}), 404

    return jsonify({"transaction_id": tx.id, "status": tx.status}), 200

import json
import pytest
from app.models import User, Transaction
from app.utils import hash_password, verify_password
from app.extensions import db

@pytest.fixture
def setup_user(test_app):
    """
    Создаёт пользователя (role=user) в БД для тестов.
    """
    with test_app.app_context():
        user = User(
            username="tester",
            password_hash=hash_password("secret"),
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        yield user
        Transaction.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()


def test_login_success(client, setup_user):
    """
    Проверяем успешный логин (JWT).
    """
    resp = client.post("/api/auth/login", json={
        "username": "tester",
        "password": "secret"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data


def test_login_fail(client, setup_user):
    """
    Проверяем неверный пароль.
    """
    resp = client.post("/api/auth/login", json={
        "username": "tester",
        "password": "wrong-pass"
    })
    assert resp.status_code == 401
    data = resp.get_json()
    assert "error" in data

def test_create_transaction(client, setup_user):
    """
    Проверяем создание транзакции (JWT Required).
    """
    # Сначала логинимся
    login_resp = client.post("/api/auth/login", json={
        "username": "tester",
        "password": "secret"
    })
    token = login_resp.get_json()["access_token"]

    # Создаём транзакцию
    headers = {"Authorization": f"Bearer {token}"}
    create_resp = client.post("/api/create_transaction",
                              json={"amount": 123.45},
                              headers=headers)
    assert create_resp.status_code == 200
    data = create_resp.get_json()
    assert data["message"] == "Транзакция создана"
    tx_id = data["transaction_id"]
    assert tx_id is not None

def test_cancel_transaction(client, setup_user):
    """
    Создаём транзакцию, отменяем её.
    """
    # Логин
    token = client.post("/api/auth/login", json={
        "username": "tester",
        "password": "secret"
    }).get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 1) Создаём
    resp_create = client.post("/api/create_transaction",
                              json={"amount": 200},
                              headers=headers)
    tx_id = resp_create.get_json()["transaction_id"]

    # 2) Отменяем
    resp_cancel = client.post("/api/cancel_transaction",
                              json={"transaction_id": tx_id},
                              headers=headers)
    assert resp_cancel.status_code == 200
    data = resp_cancel.get_json()
    assert data["message"] == "Транзакция отменена"

def test_check_transaction(client, setup_user):
    """
    Проверяем эндпоинт /api/check_transaction
    """
    token = client.post("/api/auth/login", json={
        "username": "tester",
        "password": "secret"
    }).get_json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    # Создаём транзакцию
    create_data = client.post("/api/create_transaction",
                              json={"amount": 250},
                              headers=headers).get_json()
    tx_id = create_data["transaction_id"]

    # /api/check_transaction?transaction_id=<id>
    resp_check = client.get(f"/api/check_transaction?transaction_id={tx_id}",
                            headers=headers)
    assert resp_check.status_code == 200
    data = resp_check.get_json()
    assert data["transaction_id"] == tx_id
    assert data["status"] == "pending"

def test_create_transaction_no_token(client):
    """
    Попытка создать транзакцию без токена.
    """
    resp = client.post("/api/create_transaction", json={"amount": 300})
    assert resp.status_code == 401
    data = resp.get_json()
    assert "error" in data

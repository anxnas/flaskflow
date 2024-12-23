import pytest
from app.models import User
from app.utils import hash_password
from app.extensions import db

@pytest.fixture
def setup_admin(test_app):
    """
    Создаёт пользователя-админа в БД.
    """
    with test_app.app_context():
        admin = User(
            username="admin",
            password_hash=hash_password("adminpass"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        yield admin
        db.session.delete(admin)
        db.session.commit()

def admin_login(client, username, password):
    return client.post("/admin/login", data={
        "username": username,
        "password": password
    }, follow_redirects=True)

def test_admin_login_success(client, setup_admin):
    resp = admin_login(client, "admin", "adminpass")
    assert resp.status_code == 200
    assert "Вы успешно вошли в систему".encode("utf-8") in resp.data \
           or "Дашборд".encode("utf-8") in resp.data

def test_admin_login_fail(client, setup_admin):
    resp = admin_login(client, "admin", "wrongpass")
    assert resp.status_code == 200
    assert "Неверные учётные данные".encode("utf-8") in resp.data \
           or "не админ".encode("utf-8") in resp.data


def test_admin_users_crud(client, setup_admin):
    """
    Тест CRUD пользователей через админку (на минимальном уровне).
    """
    # 1) Логин админом
    admin_login(client, "admin", "adminpass")

    # 2) Переходим на /admin/users
    resp_users = client.get("/admin/users")
    assert resp_users.status_code == 200

    # 3) Создаём нового пользователя (формой POST)
    resp_create = client.post("/admin/users/create", data={
        "username": "new_user",
        "password": "secret123",
        "balance": "100.0",
        "commission_rate": "2.5",
        "webhook_url": "",
        "role": "Пользователь",
        "usdt_wallet": ""
    }, follow_redirects=True)
    assert resp_create.status_code == 200

    with client.application.app_context():
        user_in_db = User.query.filter_by(username="new_user").first()
        assert user_in_db is not None
        assert user_in_db.role == "user"
        assert user_in_db.balance == 100

    # 4) Редактируем пользователя
    resp_edit = client.post(f"/admin/users/edit/{user_in_db.id}", data={
        "username": "renamed_user",
        "password": "",   # пустой -> не меняем пароль
        "balance": "200",
        "commission_rate": "3.0",
        "webhook_url": "",
        "role": "Администратор",  # меняем роль
        "usdt_wallet": ""
    }, follow_redirects=True)
    assert resp_edit.status_code == 200
    with client.application.app_context():
        user_in_db = User.query.get(user_in_db.id)
        assert user_in_db.username == "renamed_user"
        assert user_in_db.role == "admin"
        assert user_in_db.balance == 200

    # 5) Удаляем пользователя
    resp_delete = client.post(f"/admin/users/delete/{user_in_db.id}", follow_redirects=True)
    assert resp_delete.status_code == 200
    with client.application.app_context():
        must_none = User.query.filter_by(id=user_in_db.id).first()
        assert must_none is None

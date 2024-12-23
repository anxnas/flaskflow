import pytest
from app import create_app, db
from config import Config

class TestConfig(Config):
    # Переопределяем строку подключения на SQLite in-memory
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope="session")
def test_app():
    """
    Создаёт Flask-приложение для тестов (c in-memory SQLite).
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()  # создаём таблицы в памяти
        yield app
        db.drop_all()

@pytest.fixture
def client(test_app):
    """
    Возвращает test client (имитация HTTP-клиента).
    """
    return test_app.test_client()

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Thread
from datetime import datetime
from backend.auth import create_access_token

# Фикстура для клиента FastAPI
@pytest.fixture
def client():
    return TestClient(app)

# Фикстура для базы данных
@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Откатываем изменения после теста
        db.close()

# Фикстура для создания тестового треда
@pytest.fixture
def test_thread(db):
    thread = Thread(title="Test Thread", created_at=datetime.now())
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread

# Функция для получения тестового токена
def get_test_token(user):
    return create_access_token(data={"sub": user["email"]})

# Тест создания треда
def test_create_thread(client, db):
    test_user = {"email": "test@example.com"}  # Моковый пользователь
    response = client.post(
        "/threads",
        json={"title": "New Thread"},
        headers={"Authorization": f"Bearer {get_test_token(test_user)}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Thread"

# Тест получения всех тредов
def test_get_threads(client, test_thread):
    response = client.get("/threads")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert any(thread["id"] == test_thread.id for thread in response.json())
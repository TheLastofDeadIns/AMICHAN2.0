import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Message, Thread
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

# Фикстура для создания тестового сообщения
@pytest.fixture
def test_message(db, test_thread):
    message = Message(thread_id=test_thread.id, content="Test message", created_at=datetime.now())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

# Функция для получения тестового токена
def get_test_token(user):
    return create_access_token(data={"sub": user["email"]})

# Тест создания сообщения
def test_create_message(client, test_thread, db):
    test_user = {"email": "test@example.com"}  # Моковый пользователь
    response = client.post(
        f"/threads/{test_thread.id}/messages",
        json={"content": "New Message"},
        headers={"Authorization": f"Bearer {get_test_token(test_user)}"}
    )
    assert response.status_code == 200
    assert response.json()["content"] == "New Message"

# Тест получения сообщений
def test_get_messages(client, test_thread, test_message):
    response = client.get(f"/threads/{test_thread.id}/messages")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert any(msg["id"] == test_message.id for msg in response.json())
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import authenticate_user, get_password_hash
from backend.database import SessionLocal, User

# Фикстура для клиента FastAPI
@pytest.fixture
def client():
    return TestClient(app)

# Фикстура для базы данных
@pytest.fixture
def db():
    from backend.database import get_test_db
    db = next(get_test_db())
    try:
        yield db
    finally:
        db.rollback()  # Откатываем изменения после теста
        db.close()

# Фикстура для создания тестового пользователя
@pytest.fixture
def test_user(db):
    email = "test@edu.hse.ru"
    password = "password123"
    hashed_password = get_password_hash(password)
    user = User(email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"email": email, "password": password}

# Тест регистрации
def test_register(client):
    response = client.post(
        "/register",
        json={"email": "newuser@edu.hse.ru", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Пользователь зарегистрирован"}

# Тест входа
def test_login(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

# Тест неверного входа
def test_invalid_login(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверная почта или пароль"
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .database import SessionLocal, User
from .schemas import UserLogin

# Настройки для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка логгера
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Настройки для JWT
SECRET_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGVkdS5oc2UucnUiLCJleHAiOjE2OTkxMjM0NTZ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # Замените на случайный секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Схема для аутентификации через OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Функция для хэширования пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Функция для создания JWT-токена
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Создан токен: {encoded_jwt}")  # Логируем созданный токен
    return encoded_jwt

# Функция для получения текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.debug(f"Токен: {token}")  # Логируем токен
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Payload: {payload}")  # Логируем декодированный payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Ошибка декодирования JWT: {e}")
        raise credentials_exception
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.error(f"Пользователь с email {email} не найден")
        raise credentials_exception
    return user

# Функция для аутентификации пользователя
def authenticate_user(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
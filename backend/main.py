from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .database import SessionLocal, User, Thread, Message
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    authenticate_user,
)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Укажите адрес фронтенда
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Модели Pydantic
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class ThreadCreate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    content: str

# Регистрация пользователя
@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    if not str(user.email).endswith("@edu.hse.ru"):  # Преобразуем EmailStr в строку
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Только почты @edu.hse.ru разрешены",
        )
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Почта уже зарегистрирована",
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Пользователь зарегистрирован"}

# Вход пользователя
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная почта или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Создание треда (только для аутентифицированных пользователей)
@app.post("/threads")
def create_thread(thread: ThreadCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    db_thread = Thread(title=thread.title, created_at=datetime.now())
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread

# Получение всех тредов
@app.get("/threads")
def get_threads():
    db = SessionLocal()
    threads = db.query(Thread).all()
    return threads

# Создание сообщения (только для аутентифицированных пользователей)
@app.post("/threads/{thread_id}/messages")
def create_message(thread_id: int, message: MessageCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    db_thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден",
        )
    db_message = Message(thread_id=thread_id, content=message.content, created_at=datetime.now())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Получение сообщений в треде
@app.get("/threads/{thread_id}/messages")
def get_messages(thread_id: int):
    db = SessionLocal()
    db_thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден",
        )
    messages = db.query(Message).filter(Message.thread_id == thread_id).all()
    return messages
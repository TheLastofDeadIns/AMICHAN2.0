from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка подключения к базе данных (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./hse_forum.db"

# Создание движка базы данных
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создание сессии для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    email = Column(String, unique=True, index=True)  # Почта пользователя (уникальная)
    password_hash = Column(String)  # Хэш пароля
    is_verified = Column(Integer, default=0)  # Флаг подтверждения почты (0 или 1)

# Модель треда
class Thread(Base):
    __tablename__ = "threads"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    title = Column(String, index=True)  # Название треда
    created_at = Column(DateTime)  # Дата и время создания треда

# Модель сообщения
class Message(Base):
    __tablename__ = "messages"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    thread_id = Column(Integer, ForeignKey("threads.id"))  # Ссылка на тред
    content = Column(String)  # Текст сообщения
    created_at = Column(DateTime)  # Дата и время создания сообщения

# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Модель для регистрации пользователя
class UserCreate(BaseModel):
    email: EmailStr  # Проверка, что email валиден
    password: str    # Пароль

# Модель для ответа с данными пользователя
class UserResponse(BaseModel):
    id: int
    email: str
    is_verified: bool

    class Config:
        from_attributes = True  # Для совместимости с ORM (ранее `orm_mode = True`)

# Модель для входа пользователя
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Модель для создания треда
class ThreadCreate(BaseModel):
    title: str

# Модель для ответа с данными треда
class ThreadResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

# Модель для создания сообщения
class MessageCreate(BaseModel):
    content: str

# Модель для ответа с данными сообщения
class MessageResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
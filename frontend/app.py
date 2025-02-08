import streamlit as st
import requests
import logging
from datetime import datetime

# Логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8000"

def register(email: str, password: str):
    try:
        response = requests.post(
            f"{API_URL}/register",
            json={"email": email, "password": password},
        )
        if response.status_code == 200:
            st.success("Пользователь успешно зарегистрирован!")
            return True
        else:
            st.error(response.json().get("detail", "Ошибка регистрации"))
            return False
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return False

def login(email: str, password: str):
    try:
        response = requests.post(
            f"{API_URL}/login",
            data={"username": email, "password": password},
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                st.session_state["access_token"] = token
                st.success("Вход выполнен успешно!")
                return True
            else:
                st.error("Не удалось получить токен.")
                return False
        else:
            st.error(response.json().get("detail", "Ошибка входа"))
            return False
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return False

def logout():
    """Очищает данные сессии для выхода из аккаунта."""
    st.session_state.pop("access_token", None)
    st.session_state.pop("selected_thread_id", None)
    st.success("Вы успешно вышли из аккаунта!")
    st.rerun()

def create_thread(title: str):
    token = st.session_state.get("access_token")
    if not token:
        st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
        return None
    try:
        response = requests.post(
            f"{API_URL}/threads",
            json={"title": title},
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            thread_id = response.json().get("id")  # Получаем ID созданного треда
            st.success("Тред успешно создан!")
            return thread_id
        else:
            st.error(response.json().get("detail", "Ошибка создания треда"))
            return None
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return None

def get_threads():
    try:
        response = requests.get(f"{API_URL}/threads")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(response.json().get("detail", "Ошибка получения тредов"))
            return []
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return []

def search_threads(query: str):
    try:
        # Если запрос пустой, возвращаем все треды
        if not query.strip():
            return get_threads()

        # Фильтруем треды по названию (поиск по подстроке)
        threads = get_threads()
        filtered_threads = [
            thread for thread in threads
            if query.lower() in thread["title"].lower()
        ]

        if not filtered_threads:
            st.error("Треды с таким названием не найдены.")
            return []

        return filtered_threads
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return []

def get_messages(thread_id: int):
    try:
        response = requests.get(f"{API_URL}/threads/{thread_id}/messages")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(response.json().get("detail", "Ошибка получения сообщений"))
            return []
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return []

def create_message(thread_id: int, content: str):
    token = st.session_state.get("access_token")
    if not token:
        st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
        return False
    try:
        response = requests.post(
            f"{API_URL}/threads/{thread_id}/messages",
            json={"content": content},
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            st.success("Сообщение успешно отправлено!")
            return True
        else:
            st.error(response.json().get("detail", "Ошибка отправки сообщения"))
            return False
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        st.error(f"Ошибка: {e}")
        return False

def format_date(created_at: str):
    """Форматирует дату и время в нужный формат."""
    if created_at.endswith("Z"):
        created_at = created_at[:-1]
    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
    formatted_date = dt.strftime("%y/%m/%d %a %H:%M:%S")
    return formatted_date

def display_chat(messages):
    for index, message in enumerate(messages, start=1):
        formatted_date = format_date(message["created_at"])
        st.markdown(
            f"""
            <div style="
                border: 1px solid lightgray;
                background-color: #f9f9f9;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
            ">
                <p style="color: orange !important;"><b>Аноним</b> {formatted_date} №{index}</p>
                <p style="color: black !important;">{message['content']}</p>
                <button 
                    style="
                        background-color: white; 
                        border: 1px solid orange; 
                        color: orange; 
                        cursor: pointer; 
                        padding: 5px 10px; 
                        border-radius: 5px;
                    " 
                    onclick="document.getElementById('reply_to_{index}').click()"
                >
                    Ответить
                </button>
                <button id="reply_to_{index}" style="display: none;" 
                    onclick="document.getElementById('new_message').value += '>>{index}\\n';">
                </button>
            </div>
            """,
            unsafe_allow_html=True,
        )

def main():
    # Настройка пользовательских стилей
    st.markdown(
        """
        <style>
        .stApp {
            background-color: white !important;
        }
        h1, h2, h3, h4, h5, h6, p, div, span, label {
            color: orange !important;
        }
        /* Изменение стиля кнопок */
        .stButton > button {
            border: 2px solid orange !important;
            background-color: white !important;
            color: orange !important;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer !important;
        }
        /* Стиль для текстовых полей */
        .stTextInput input, .stTextArea textarea {
            cursor: text !important;
        }
        /* Скрыть боковое меню */
        [data-testid="stSidebar"] {
            background-color: #f9f9f9 !important;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Инициализация состояния сессии
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    if "selected_thread_id" not in st.session_state:
        st.session_state["selected_thread_id"] = None

    # Боковая панель (sidebar)
    with st.sidebar:
        st.markdown("### Меню")
        if st.session_state["access_token"]:
            st.write("Вы вошли в систему.")
            if st.button("Выйти", key="logout_button"):
                logout()

            # Создание нового треда
            st.subheader("Создать новый тред")
            thread_title = st.text_input("Введите название треда", key="create_thread_title_sidebar")
            if st.button("Создать тред", disabled=not thread_title.strip(), key="create_thread_button_sidebar"):
                thread_id = create_thread(thread_title)
                if thread_id:
                    st.session_state["selected_thread_id"] = thread_id
                    st.rerun()

            # Поиск тредов
            st.subheader("Поиск треда")
            search_query = st.text_input("Введите название треда или часть названия", key="search_query_sidebar")
            if st.button("Поиск", key="search_button_sidebar"):
                threads = search_threads(search_query)
            else:
                threads = get_threads()
        else:
            st.write("Вы не вошли в систему.")

    # Если пользователь уже авторизован, показываем главную страницу
    if st.session_state["access_token"]:
        # Если выбран тред, показываем его страницу
        if st.session_state["selected_thread_id"]:
            thread_id = st.session_state["selected_thread_id"]
            threads = get_threads()
            thread = next((t for t in threads if t["id"] == thread_id), None)
            if thread:
                st.title(f"{thread['title']} (ID: {thread['id']})")
            else:
                st.title(f"Тред ID: {thread_id}")

            if st.button("Вернуться к списку тредов", key="back_to_threads_top"):
                st.session_state["selected_thread_id"] = None
                st.rerun()

            messages = get_messages(thread_id)
            display_chat(messages)

            st.header("Новое сообщение")
            new_message = st.text_area("Введите текст сообщения", key="new_message")
            if st.button("Отправить", disabled=not new_message.strip(), key="send_message_button"):
                if create_message(thread_id, new_message):
                    st.rerun()

            if st.button("Вернуться к списку тредов", key="back_to_threads_bottom"):
                st.session_state["selected_thread_id"] = None
                st.rerun()

            return

        # Главная страница (список тредов)
        st.title("AMI Forum")

        # Список тредов
        st.header("Треды")
        for thread in threads:
            if st.button(f"{thread['title']} (ID: {thread['id']})", key=f"thread_{thread['id']}"):
                st.session_state["selected_thread_id"] = thread["id"]
                st.rerun()

    else:
        # Страница входа/регистрации
        st.title("AMI Forum")

        menu = st.selectbox("Выберите действие", ["Вход", "Регистрация"], key="menu_selectbox")

        if menu == "Регистрация":
            st.header("Регистрация")
            email = st.text_input("Почта (@edu.hse.ru)", key="register_email")
            password = st.text_input("Пароль", type="password", key="register_password")
            if st.button("Зарегистрироваться", key="register_button"):
                if email.endswith("@edu.hse.ru"):
                    if register(email, password):
                        st.session_state["access_token"] = "dummy_token"
                        st.rerun()
                else:
                    st.error("Только почты @edu.hse.ru разрешены")

        elif menu == "Вход":
            st.header("Вход")
            email = st.text_input("Почта", key="login_email")
            password = st.text_input("Пароль", type="password", key="login_password")
            if st.button("Войти", key="login_button"):
                if login(email, password):
                    st.rerun()

if __name__ == "__main__":
    main()
import time
import streamlit as st
import httpx
from decouple import config
from streamlit_cookies_controller import CookieController

from auth.jwt_handler import verify_access_token
from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar

# Настройка страницы
make_sidebar()
st.title("This is yours operations")

# --- ЛОГИКА АВТОРИЗАЦИИ (FIXED) ---
cookie_manager = CookieController()
access_token = None

# 1. Сначала ищем в Session State (мгновенно)
if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]

# 2. Если нет в сессии, ищем в куках с задержкой
if not access_token:
    time.sleep(0.2)
    access_token = cookie_manager.get("access_token")

    # Если нашли — восстанавливаем в сессию
    if access_token:
        st.session_state["access_token"] = access_token

# 3. Если токена нет нигде — редирект
if not access_token:
    st.warning("Please log in first.")
    time.sleep(1)
    st.switch_page("webui.py")
# ----------------------------------

# Верификация токена
try:
    user_id = verify_access_token(access_token)["user"]
except Exception:
    st.error("Invalid token")
    st.stop()

header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def get_user_history():
    try:
        # Добавил timeout, чтобы не висело вечно
        history = httpx.get(
            url=f"{config(BACKEND_HOST)}/api/history/all/", headers=header, timeout=5.0
        )
        return history
    except httpx.RequestError:
        return None


# Получение данных
data_response = get_user_history()

if data_response is None:
    st.error("Failed to connect to backend.")
elif data_response.status_code != 200:
    st.error(f"Error loading history: {data_response.text}")
else:
    history_data = data_response.json()

    if len(history_data) == 0:
        st.info("No operations found.")
    else:
        # Рисуем заголовки таблицы
        c_id, c_operation, c_datetime = st.columns([0.5, 1, 1], gap="small")
        c_id.markdown("**ID**")
        c_operation.markdown("**Operation**")
        c_datetime.markdown("**Date/Time**")

        st.divider()

        # Рисуем строки
        for i in history_data:
            # Создаем новые колонки для каждой строки, чтобы верстка была ровной
            col1, col2, col3 = st.columns([0.5, 1, 1], gap="small")

            col1.write(i["id"])
            col2.write(i["operation"])
            col3.write(i["datetime"])
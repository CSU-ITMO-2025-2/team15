import time
import httpx
import streamlit as st
from decouple import config
from streamlit_cookies_controller import CookieController

from auth.jwt_handler import verify_access_token
from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar

# Настройка страницы
make_sidebar()
st.title("Tasks")

# --- ЛОГИКА АВТОРИЗАЦИИ (ИСПРАВЛЕННАЯ) ---
# Инициализируем контроллер локально, чтобы не зависеть от webui.py
cookie_manager = CookieController()

access_token = None

# 1. Сначала ищем в Session State (мгновенный доступ после перехода)
if "access_token" in st.session_state:
    access_token = st.session_state["access_token"]

# 2. Если в сессии пусто, пробуем достать из кук с небольшой задержкой
if not access_token:
    time.sleep(0.2) # Даем компоненту время прогрузиться
    access_token = cookie_manager.get("access_token")

    # Если нашли в куках - сохраняем обратно в сессию
    if access_token:
        st.session_state["access_token"] = access_token

# 3. Если токена все еще нет — редирект
if not access_token:
    st.warning("Please log in first.")
    time.sleep(1)
    st.switch_page("webui.py")
# ----------------------------------------

# Получаем ID пользователя из токена
try:
    user_id = verify_access_token(access_token)["user"]
except Exception:
    st.error("Invalid token")
    st.stop()

header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def download_tasks():
    try:
        res = httpx.get(url=f"{config(BACKEND_HOST)}/api/task/all/", headers=header, timeout=10.0)
        return res
    except httpx.RequestError:
        return None


def run_task(task_id: int):
    try:
        res = httpx.post(url=f"{config(BACKEND_HOST)}/api/task/execute/{task_id}/", headers=header, timeout=10.0)
        return res
    except httpx.RequestError:
        return None


# Загрузка и отображение данных
data_response = download_tasks()

if data_response is None:
    st.error("Failed to connect to backend.")
elif data_response.status_code != 200:
    st.write(data_response.json())
else:
    # Заголовки таблицы
    c_id, c_task_status, c_task_data, c_run = st.columns([0.5, 1, 3, 1], gap="small")

    c_id.markdown("**ID**")
    c_task_data.markdown("**Data name**")
    c_task_status.markdown("**Status**")
    c_run.markdown("**Prediction result**")

    st.divider()

    for i in data_response.json():
        task_id = i["id"]

        # Создаем новую строку колонок для каждой записи
        col1, col2, col3, col4 = st.columns([0.5, 1, 3, 1], gap="small")

        col1.write(task_id)
        col3.write(i["datapath"])
        col2.write(i["status"])

        is_finished = i["predicted_value"] is not None

        with col4:
            if is_finished:
                st.write(f"Result: {i['predicted_value']}")
            else:
                # Кнопка запуска
                if st.button("Run Task", key=f"execute_task_id_{task_id}"):
                    response = run_task(task_id)
                    if response and response.status_code == 200:
                        st.success("Task started!")
                        time.sleep(0.5)
                        st.rerun() # Обновляем текущую страницу
                    else:
                        st.error("Failed to start task")
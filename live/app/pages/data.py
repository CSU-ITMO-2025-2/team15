import time
import httpx
import streamlit as st
import pandas as pd
from decouple import config
from streamlit_cookies_controller import CookieController

from auth.jwt_handler import verify_access_token
from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar

# Настройка страницы
make_sidebar()
st.title("Welcome")
st.write("Most of the user interactions with system")

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


# --- API ФУНКЦИИ ---
def upload_data(payload):
    try:
        res = httpx.post(url=f"{config(BACKEND_HOST)}/api/df/upload", json=payload, headers=header, timeout=10.0)
        return res
    except httpx.RequestError:
        return None

def download_data():
    try:
        res = httpx.get(url=f"{config(BACKEND_HOST)}/api/df/all/", headers=header, timeout=10.0)
        return res
    except httpx.RequestError:
        return None

def create_task(task_id: int):
    try:
        res = httpx.post(url=f"{config(BACKEND_HOST)}/api/task/create/data/{task_id}/model/1/", headers=header, timeout=10.0)
        return res
    except httpx.RequestError:
        return None

def delete_data(id_val: int):
    try:
        res = httpx.delete(url=f"{config(BACKEND_HOST)}/api/df/file/{id_val}", headers=header, timeout=10.0)
        return res
    except httpx.RequestError:
        return None


# --- ИНТЕРФЕЙС ---
tab1, tab2 = st.tabs(["Upload data", "Data in system"])

# ВКЛАДКА 1: ЗАГРУЗКА
with tab1:
    with st.form("df enter"):
        st.subheader("Data upload form")

        # Используем колонки для компактности формы
        col1, col2 = st.columns(2)

        with col1:
            fixed_acidity = st.number_input(label="fixed_acidity", value=7.4, key="fixed_acidity")
            volatile_acidity = st.number_input(label="volatile_acidity", value=0.7, key="volatile_acidity")
            citric_acid = st.number_input(label="citric_acid", value=0.0, key="citric_acid")
            residual_sugar = st.number_input(label="residual_sugar", value=1.9, key="residual_sugar")
            chlorides = st.number_input(label="chlorides", value=0.076, format="%.3f", key="chlorides")
            free_sulfur_dioxide = st.number_input(label="free_sulfur_dioxide", value=11.0, key="free_sulfur_dioxide")

        with col2:
            total_sulfur_dioxide = st.number_input(label="total_sulfur_dioxide", value=34.0, key="total_sulfur_dioxide")
            density = st.number_input(label="density", value=0.9978, format="%.4f", key="density")
            pH = st.number_input(label="pH", value=3.51, key="pH")
            sulphates = st.number_input(label="sulphates", value=0.56, key="sulphates")
            alcohol = st.number_input(label="alcohol", value=9.4, key="alcohol")

        submit = st.form_submit_button("Upload data")

        if submit:
            df_payload = {
                "fixed_acidity": fixed_acidity,
                "volatile_acidity": volatile_acidity,
                "citric_acid": citric_acid,
                "residual_sugar": residual_sugar,
                "chlorides": chlorides,
                "free_sulfur_dioxide": free_sulfur_dioxide,
                "total_sulfur_dioxide": total_sulfur_dioxide,
                "density": density,
                "pH": pH,
                "sulphates": sulphates,
                "alcohol": alcohol
            }

            result_resp = upload_data(df_payload)

            if result_resp and result_resp.status_code == 200:
                res_json = result_resp.json()
                msg = res_json.get("message", "Success")
                st.success(msg)
                time.sleep(1) # Даем прочитать сообщение
                st.rerun()    # Обновляем, чтобы данные появились во второй вкладке
            elif result_resp:
                st.error(f"Error: {result_resp.text}")
            else:
                st.error("Connection error")

# ВКЛАДКА 2: СПИСОК ФАЙЛОВ
with tab2:
    data_response = download_data()

    if data_response is None:
        st.error("Failed to connect to backend.")
    elif data_response.status_code != 200:
        st.write(data_response.json())
    else:
        # Заголовки таблицы
        h_id, h_filename, h_datetime, h_create, h_delete = st.columns([0.5, 3, 1.5, 1, 1], gap="small")
        h_id.markdown("**ID**")
        h_filename.markdown("**Filename**")
        h_datetime.markdown("**Date**")
        h_create.markdown("**Action**")
        h_delete.markdown("**Delete**")

        st.divider()

        data_list = data_response.json()
        if not data_list:
            st.info("No data uploaded yet.")

        for i in data_list:
            data_id = i["id"]

            # Строка таблицы
            c_id, c_filename, c_datetime, c_create_task, c_delete = st.columns([0.5, 3, 1.5, 1, 1], gap="small")

            c_id.write(data_id)
            c_filename.write(i["path"])
            c_datetime.write(i["datetime"])

            with c_create_task:
                if st.button("Predict", key=f"create_task_id_{data_id}"):
                    task_res = create_task(data_id)
                    if task_res and task_res.status_code == 200:
                        st.success("Task created!")
                        time.sleep(0.5)
                        st.switch_page("pages/tasks.py")
                    else:
                        st.error("Failed")

            with c_delete:
                if st.button("Delete", key=f"delete_id_{data_id}", type="primary"):
                    del_res = delete_data(data_id)
                    if del_res and del_res.status_code == 200:
                        st.success("Deleted")
                        time.sleep(0.5)
                        st.rerun() # Обновляем список мгновенно
                    else:
                        st.error("Error")
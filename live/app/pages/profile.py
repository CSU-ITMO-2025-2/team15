import time
import httpx
import streamlit as st
from decouple import config
from streamlit_cookies_controller import CookieController
from auth.jwt_handler import verify_access_token
from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar

# Настройка боковой панели
make_sidebar()
st.title("Profile")

# --- ЛОГИКА АВТОРИЗАЦИИ (FIXED) ---
cookie_manager = CookieController()
access_token = None

# 1. Сначала ищем в Session State (быстрая проверка)
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
    decoded_token = verify_access_token(access_token)
    user_id = decoded_token["user"]
except Exception:
    st.error("Session expired or invalid token.")
    time.sleep(2)
    st.switch_page("webui.py")

header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def get_user_balance():
    try:
        response = httpx.get(url=f"{config(BACKEND_HOST)}/api/balance/{user_id}", headers=header, timeout=5.0)
        if response.status_code == 200:
            return response.json()
        return None
    except httpx.RequestError:
        return None


def refill_user_balance(amount_val):
    try:
        response = httpx.post(
            url=f"{config(BACKEND_HOST)}/api/balance/replenish/{amount_val}", headers=header, timeout=5.0
        )
        return response
    except httpx.RequestError:
        return None


with st.form("Balance form"):
    st.subheader("Your Balance")

    # Получаем текущий баланс
    balance_data = get_user_balance()

    if balance_data:
        current_balance = balance_data.get("value", 0.0)
        st.metric(label="Current balance", value=f"{current_balance}")
    else:
        st.error("Failed to load balance.")

    # Кнопка обновления (по сути просто перезагружает форму)
    submit = st.form_submit_button("Refresh")

    st.divider()

    # Поле ввода и кнопка пополнения
    amount = st.number_input(label="Please input amount:", step=50.0, min_value=50.0, max_value=1000.0, value=150.0)
    refill = st.form_submit_button("Refill")

    if refill:
        transaction = refill_user_balance(amount)
        if transaction and transaction.status_code == 200:
            msg = transaction.json().get("message", "Success")
            st.success(msg)
            time.sleep(0.5)
            st.rerun() # Обновляем страницу, чтобы увидеть новый баланс
        elif transaction:
            st.error(f"Error: {transaction.text}")
        else:
            st.error("Connection error")
import time
import httpx
import streamlit as st
from decouple import config
# Используем ту же библиотеку, что и на остальных страницах для совместимости
from streamlit_cookies_controller import CookieController

from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar

make_sidebar()

# Инициализация контроллера
cookie_manager = CookieController()

def password_entered():
    try:
        data = {
            "login": username,
            "password": password
        }
        headers = {'Content-type': 'application/json'}
        # Добавляем таймаут
        res = httpx.post(url=f"{config(BACKEND_HOST)}/api/user/signin", json=data, headers=headers, timeout=10.0)
        return res
    except httpx.RequestError:
        return None

def create_user():
    try:
        data = {
            "login": login,
            "password": user_password,
            "email": email_address,
        }
        headers = {'Content-type': 'application/json'}
        res = httpx.post(url=f"{config(BACKEND_HOST)}/api/user/register", json=data, headers=headers, timeout=10.0)
        return res
    except httpx.RequestError:
        return None

st.title("Hello, world")

tab1, tab2 = st.tabs(["Login", "Register"])

# --- ВХОД ---
with tab1:
    username = st.text_input("Login", key="username")
    password = st.text_input("Password", type="password", key="password")

    if st.button("Sign in", type="primary", key="signin"):
        result = password_entered()

        if result is None:
            st.error("Connection to server failed.")

        # Обработка ошибок (401, 404 и т.д.)
        elif result.status_code != 200:
            try:
                error_desc = result.json().get("detail", "Unknown error")
            except:
                error_desc = result.text

            # Очищаем токен при ошибке
            cookie_manager.set("access_token", '')
            st.error(f"Error: {error_desc}")

        # Успешный вход
        else:
            token_data = result.json()
            val = token_data.get("access_token")

            if val:
                # 1. Сохраняем в куки (надолго)
                cookie_manager.set("access_token", val)

                # 2. Сохраняем в сессию (мгновенно)
                st.session_state["access_token"] = val

                st.success("Logged in successfully!")

                # Небольшая пауза для браузера
                time.sleep(0.5)

                st.switch_page("pages/profile.py")
            else:
                st.error("Server did not return a token.")

# --- РЕГИСТРАЦИЯ ---
with tab2:
    st.write(f"Register a new user.")

    login = st.text_input("Login")
    user_password = st.text_input("Password")
    email_address = st.text_input("Email")

    if st.button("Sign up", type="primary", key="sign_up"):
        result = create_user()

        if result is None:
            st.error("Connection failed.")
        elif result.status_code == 200:
            message = result.json()
            st.success(message.get("message", "Success"))
            time.sleep(1)
            # Обычно после регистрации нужно логиниться,
            # но если бекенд не логинит сразу, этот переход может вернуть на логин.
            # Оставим как было у тебя:
            st.switch_page("pages/profile.py")
        else:
            try:
                st.error(result.json().get("detail", result.text))
            except:
                st.error("Registration failed")
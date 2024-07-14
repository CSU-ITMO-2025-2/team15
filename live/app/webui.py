import uuid

import streamlit as st
import httpx
import extra_streamlit_components as stx
from decouple import config
from streamlit_cookies_controller import CookieController

from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar

make_sidebar()


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


# if 'cookies' not in st.session_state:
#    st.session_state['cookies'] = cookie_manager.get_all()
# cookie_manager = get_manager()
cookie_manager = CookieController()


def password_entered():
    data = {
        "login": username,
        "password": password
    }
    headers = {'Content-type': 'application/json'}
    res = httpx.post(url=f"{config(BACKEND_HOST)}/api/user/signin", json=data, headers=headers)
    return res


def create_user():
    data = {
        "login": login,
        "password": user_password,
        "email": email_address,
    }

    headers = {'Content-type': 'application/json'}
    res = httpx.post(url=f"{config(BACKEND_HOST)}/api/user/register", json=data, headers=headers)
    return res


st.title("Hello, world")

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    username = st.text_input("Login", key="username")
    password = st.text_input("Password", type="password", key="password")

    if st.button("Sign in", type="primary", key="signin"):
        result = password_entered()
        if result.status_code in [401, 404]:
            error_desc = result.json()["detail"]
            st.write(f"{error_desc}")
        else:
            val = result.json()["access_token"]
            cookie_manager.set("access_token", val)
            st.success("Logged in successfully!")

            st.switch_page("pages/profile.py")

with tab2:
    st.write(f"Register a new user.")

    login = st.text_input("Login")
    user_password = st.text_input("Password")
    email_address = st.text_input("Email")

    if st.button("Sign up", type="primary", key="sign_up"):
        result = create_user()
        if result.status_code == 200:
            message = result.json()
            st.write(message["message"])
            st.switch_page("pages/profile.py")
        else:
            message = result.json()
            st.write(message)

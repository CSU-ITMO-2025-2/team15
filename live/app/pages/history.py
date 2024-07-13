import streamlit as st
import httpx
import pandas as pd
from decouple import config

from auth.jwt_handler import verify_access_token
from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar
from webui import cookie_manager

make_sidebar()

st.title("This is yours operations")

access_token = cookie_manager.get("access_token")
if not access_token:
    st.switch_page("webui.py")

user_id = verify_access_token(access_token)["user"]
header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def get_user_history():
    history = httpx.get(
        url=f"{config(BACKEND_HOST)}/api/history/all/", headers=header
    )
    return history


data_response = get_user_history()
if len(data_response.json()) == 0:
    st.write("Nothing is good")
else:
    c_id, c_operation, c_datetime = st.columns([0.5, 1, 1], gap="small")
    with st.container():
        for i in data_response.json():
            c_id.write(i["id"])
            c_operation.write(i["operation"])
            c_datetime.write(i["datetime"])

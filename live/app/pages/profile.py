import httpx
import streamlit as st
import pandas as pd
import numpy as np
from decouple import config

from auth.jwt_handler import verify_access_token
from ml.const import BACKEND_HOST
from pages.common.navigation import make_sidebar
from webui import cookie_manager

make_sidebar()

st.title("Profile")

access_token = cookie_manager.get("access_token")
if not access_token:
    st.switch_page("webui.py")

print(verify_access_token(access_token))
print(access_token)
user_id = verify_access_token(access_token)["user"]
header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def get_user_balance():
    response = httpx.get(url=f"{config(BACKEND_HOST)}/api/balance/{user_id}", headers=header)
    return response.json()


def refill_user_balance():
    response = httpx.post(
        url=f"{config(BACKEND_HOST)}/api/balance/replenish/{amount}", headers=header
    )
    return response.json()


def create_task(data_id: int):
    data = {"userid": user_id, "user_df_id": data_id}
    res = httpx.post(
        url=f"{config(BACKEND_HOST)}/create/data/{data_id}/model/1", json=data, headers=header
    )
    return res


with st.form("Balance form"):
    st.subheader("Your Balance")
    balance = get_user_balance()["value"]
    st.write(f"Current balance: {balance}")
    submit = st.form_submit_button("Refresh")
    amount = st.number_input(label="Please input amount:", step=50.0, min_value=50.0, max_value=1000.0, value=150.0)
    refill = st.form_submit_button("Refill")
    if submit:
        balance = get_user_balance()
    if refill:
        transaction = refill_user_balance()
        try:
            st.write(transaction["message"])
        except:
            st.write(transaction)

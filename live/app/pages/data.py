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

st.title("Welcome")

st.write("Most of the user interactions with system")

access_token = cookie_manager.get("access_token")
if not access_token:
    st.switch_page("webui.py")

user_id = verify_access_token(access_token)["user"]
header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def upload_data():
    df = {
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

    res = httpx.post(url=f"{config(BACKEND_HOST)}/api/df/upload", json=df, headers=header)
    return res.json()


def download_data():
    res = httpx.get(url=f"{config(BACKEND_HOST)}/api/df/all/", headers=header)
    return res


def create_task(task_id: int):
    res = httpx.post(url=f"{config(BACKEND_HOST)}/api/task/create/data/{task_id}/model/1/", headers=header)
    return res


def delete_data(id: int):
    res = httpx.delete(url=f"{config(BACKEND_HOST)}/api/df/file/{id}", headers=header)
    return res


tab1, tab2 = st.tabs(["Upload data", "Data in system"])

with tab1:
    with st.form("df enter"):
        st.subheader("Data upload form")

        fixed_acidity = st.number_input(label="fixed_acidity", value=7.4, key="fixed_acidity")
        volatile_acidity = st.number_input(label="volatile_acidity", value=0.7, key="volatile_acidity")
        citric_acid = st.number_input(label="citric_acid", value=0, key="citric_acid")
        residual_sugar = st.number_input(label="residual_sugar", value=1.9, key="residual_sugar")
        chlorides = st.number_input(label="chlorides", value=0.076, format="%.3f", key="chlorides")
        free_sulfur_dioxide = st.number_input(label="free_sulfur_dioxide", value=11, key="free_sulfur_dioxide")
        total_sulfur_dioxide = st.number_input(label="total_sulfur_dioxide", value=34, key="total_sulfur_dioxide")
        density = st.number_input(label="density", value=0.9978, format="%.4f", key="density")
        pH = st.number_input(label="pH", value=3.51, key="pH")
        sulphates = st.number_input(label="sulphates", value=0.56, key="sulphates")
        alcohol = st.number_input(label="alcohol", value=9.4, key="alcohol")
        submit = st.form_submit_button("Upload data")

        if submit:
            result = upload_data()
            if "message" in result:
                st.write(result["message"])
            else:
                st.write(result.json())

with (tab2):
    data_response = download_data()

    if data_response.status_code != 200:
        st.write(data_response.json())
    else:
        c_id, c_filename, c_datetime, c_create_task, c_delete = st.columns([1, 3, 1, 1, 1], gap="small")

        for i in data_response.json():
            data_id = i["id"]
            c_id.write(data_id)
            c_filename.write(i["path"])
            c_datetime.write(i["datetime"])
            with c_create_task:
                if st.button("task", key=f"create_task_id_{data_id}"):
                    create_task(data_id)
            with c_delete:
                if st.button("delete", key=f"delete_id_{data_id}"):
                    delete_data(data_id)

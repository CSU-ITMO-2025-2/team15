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

st.title("Tasks")

access_token = cookie_manager.get("access_token")
if not access_token:
    st.switch_page("webui.py")

user_id = verify_access_token(access_token)["user"]
header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def download_tasks():
    res = httpx.get(url=f"{config(BACKEND_HOST)}/api/task/all/", headers=header)
    return res


def run_task(task_id: int):
    res = httpx.post(url=f"{config(BACKEND_HOST)}/api/task/execute/{task_id}/", headers=header)
    return res


data_response = download_tasks()

if data_response.status_code != 200:
    st.write(data_response.json())
else:
    c_id, c_task_status, c_task_data, c_run = st.columns([0.5, 1, 3, 1], gap="small")
    with st.container():
        for i in data_response.json():

            task_id = i["id"]
            c_id.write(task_id)
            c_task_data.write(i["datapath"])
            c_task_status.write(i["status"])

            is_disable = i["predicted_value"] != None
            with c_run:
                if is_disable:
                    c_run.write(i["predicted_value"])
                else:
                    if c_run.button("task", key=f"execute_task_id_{task_id}"):
                        response = run_task(task_id)
                        st.switch_page("pages/tasks.py")

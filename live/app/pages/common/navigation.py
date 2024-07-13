import streamlit as st
from time import sleep


def make_sidebar():
    with st.sidebar:
        st.title("WineApp")
        st.write("")
        st.write("")


def logout():
    st.session_state.logged_in = False
    del st.session_state["access_token"]
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("webui.py")

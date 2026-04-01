import streamlit as st

def initialize():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'page' not in st.session_state:
        st.session_state.page = None

    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'role' not in st.session_state:
        st.session_state.role = None

    if 'token' not in st.session_state:
        st.session_state.token = None

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if "login_email_key" not in st.session_state:
        st.session_state.login_email_key = "login_email"

    if "login_password_key" not in st.session_state:
        st.session_state.login_password_key = "login_password"

    if "signup_email_key" not in st.session_state:
        st.session_state.signup_email_key = "signup_email"

    if "signup_password_key" not in st.session_state:
        st.session_state.signup_password_key = "signup_password"

    if (st.session_state.logged_in == False and st.session_state.page != "app"):
        st.session_state.page = "app"
        st.switch_page("app.py")
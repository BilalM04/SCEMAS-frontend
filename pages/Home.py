import streamlit as st

from models.AccountRole import AccountRole
from utils.Initialize import initialize
from utils.Sidebar import render_page_links, render_sidebar

st.set_page_config(layout="centered")
st.session_state.page = "home"


st.set_page_config(layout="centered")
initialize()
render_sidebar()

st.title('🏠 SCEMAS')
st.caption('🚀 Smart City Environmental Monitoring & Alert System')

st.write("Platform designed to monitor environmental data, generate alerts, and provide actionable insights for smart city infrastructure.")

st.subheader("Quick Links")

render_page_links()
import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


initialize()
render_sidebar()

st.title('👤 Accounts')
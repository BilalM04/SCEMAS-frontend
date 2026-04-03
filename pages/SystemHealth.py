import streamlit as st
import time

from clients.OperationalClient import get_system_health
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

st.set_page_config(layout="wide")
st.session_state.page = "system_health"

initialize()
render_sidebar()

# -------------------------------
# Header
# -------------------------------
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title("❤️‍🩹 System Health")
    st.caption("Live system performance overview")

with header_col2:
    st.write("")  # spacing
    st.write("")

# -------------------------------
# Config
# -------------------------------
REFRESH_COOLDOWN = 5  # seconds

# -------------------------------
# Helpers
# -------------------------------
@st.cache_data(show_spinner=False)
def fetch_system_health_cached():
    return get_system_health()

def format_uptime(seconds: float) -> str:
    mins, sec = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hrs > 0:
        parts.append(f"{hrs}h")
    if mins > 0:
        parts.append(f"{mins}m")
    parts.append(f"{sec}s")

    return " ".join(parts)

def usage_color(value: float) -> str:
    if value < 50:
        return "🟢"
    elif value < 80:
        return "🟡"
    return "🔴"

# -------------------------------
# Refresh Logic
# -------------------------------
now = time.time()
cooldown_remaining = REFRESH_COOLDOWN - (now - st.session_state.last_refresh_time)

with header_col2:
    if st.button("🔄 Refresh", use_container_width=True):
        if cooldown_remaining <= 0:
            fetch_system_health_cached.clear()
            st.session_state.system_health_data = fetch_system_health_cached()
            st.session_state.last_refresh_time = time.time()
            st.toast("System metrics refreshed", icon=":material/check:")
        else:
            st.caption(f"⏱️ {cooldown_remaining:.1f}s")

# -------------------------------
# Initial Load
# -------------------------------
if st.session_state.system_health_data is None:
    with st.spinner("Fetching system health..."):
        st.session_state.system_health_data = fetch_system_health_cached()
        st.session_state.last_refresh_time = time.time()

data = st.session_state.system_health_data

# -------------------------------
# Metrics Section
# -------------------------------
st.divider()
st.subheader("📊 Current Status")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="⏱️ Uptime",
            value=format_uptime(data.up_time),
        )

        st.metric(
            label=f"💾 Memory {usage_color(data.memory_usage)}",
            value=f"{data.memory_usage:.1f}%",
            help="Percentage of memory used"
        )

    with col2:
        st.metric(
            label=f"🖥️ CPU {usage_color(data.cpu_usage)}",
            value=f"{data.cpu_usage:.1f}%",
            help="Percentage of CPU used"
        )

        st.metric(
            label=f"📀 Disk {usage_color(data.disk_space)}",
            value=f"{data.disk_space:.1f}%",
            help="Percentage of disk used"
        )

# -------------------------------
# Resource Utilization
# -------------------------------
st.divider()
st.subheader("📈 Resource Utilization")

def render_bar(label, value):
    st.markdown(f"""
    <div style="margin-bottom: 8px;">
        <strong>{label}</strong>
        <span style="float:right;">{value:.1f}% {usage_color(value)}</span>
    </div>
    """, unsafe_allow_html=True)

    st.progress(min(value / 100, 1.0))
    st.write("")  # spacing

with st.container():
    render_bar("CPU", data.cpu_usage)
    render_bar("Memory", data.memory_usage)
    render_bar("Disk", data.disk_space)

# -------------------------------
# Footer
# -------------------------------
st.divider()
st.caption(
    "🕒 Last updated: "
    + time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(st.session_state.last_refresh_time)
    )
)